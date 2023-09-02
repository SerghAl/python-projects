import json
import os
from datetime import datetime
from functools import reduce

from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *

app_dir = os.path.dirname(
    os.path.abspath(__file__))
data_path = static_path = os.path.join(app_dir, 'data.json')


def calculate_points(gender, short_run, long_run, jump, gym, swimming, scope):

    with use_scope(scope, clear=True):
        put_text('')

    events_data = {
        "short_run": {
            "points": 0,
            "user_result": short_run,
            "get_success_msg": lambda points: f'Ваш результат на короткой дистанции: {short_run} сек. Очки: {points}',
            "failure_msg": f'Ваш результат на короткой дистанции: {short_run} сек. Очки: 0',
            "check_result": lambda user_result, result: user_result <= result
        },
        "long_run": {
            "points": 0,
            "user_result": long_run,
            "get_success_msg": lambda points: f'Ваш результат на длинной дистанции: {long_run} мин. Очки: {points}',
            "failure_msg": f'Ваш результат на длинной дистанции: {long_run} сек. Очки: 0',
            "check_result": lambda user_result, result: datetime.strptime(user_result, '%H:%M:%S').time() <= datetime.strptime(result, '%M:%S').time()
        },
        "gym": {
            "points": 0,
            "user_result": gym,
            "get_success_msg": lambda points: f'Ваш результат в прыжке в длину: {jump} см. Очки: {points}',
            "failure_msg": f'Ваш результат в прыжке в длину: {jump} см. Очки: 0',
            "check_result": lambda user_result, result: user_result >= result
        },
        "jump": {
            "points": 0,
            "user_result": jump,
            "get_success_msg": lambda points: f'Ваш результат в силовой гимнастике: {gym} раз. Очки: {points}',
            "failure_msg": f'Ваш результат в силовой гимнастике: {gym} раз. Очки: 0',
            "check_result": lambda user_result, result: user_result >= result
        },
        "swimming": {
            "points": 0,
            "user_result": swimming,
            "get_success_msg": lambda points: f'Ваш результат в плавании: {swimming} сек. Очки: {points}',
            "failure_msg": f'Ваш результат в плавании: {swimming} сек. Очки: 0',
            "check_result": lambda user_result, result: user_result <= result
        },
    }

    try:
        with open(data_path, 'r') as f:
            data = json.load(f)

        for event in list(events_data.keys()):
            for i, result in enumerate(data[gender][event]):
                user_result = events_data[event]['user_result']

                if events_data[event]['check_result'](user_result, result):
                    with use_scope(scope):
                        points = (i-20)*-1
                        events_data[event]['points'] = points
                        put_text(events_data[event]['get_success_msg'](points))
                    break
                elif i == len(data[gender][event]) - 1:
                    with use_scope(scope):
                        put_text(events_data[event]['failure_msg'])

        with use_scope(scope):
            points = reduce(
                lambda x, key: x + events_data[key]['points'], events_data, 0)
            put_success(
                f'Ваш итоговый результат: {points} очков')

    except:
        print("Возникла ошибка при подсчете данных")


def main():
    style(put_grid([
        [put_link('Назад', '/'), None],
        [span(put_select("gender", label="Пол", options=[
              ('Мужской', 'male', True), ('Женский', 'female')]), col=2)],
        [span(put_info('Введите результаты контрольных испытаний'), col=2)],
        [put_input("short_run", label="Бег 100 м.", value=12.3, type=FLOAT, help_text='Результат в секундах'),
         put_input("long_run", label="Бег 1000 м. (юноши) / 500 м. (девушки)", type=TIME, value="00:02:30", help_text='Время в формате ЧЧ:ММ:СС')],
        [put_input("jump", label="Прыжок в длину с места", value=265, type=NUMBER, help_text='Результат в сантиметрах'),
         put_input("gym", label="Подтягивания (юноши) / отжимания (девушки)", value=20, type=NUMBER, help_text='Результат в количестве раз')],
        [put_input("swimming", label="Плавание", type=FLOAT,
                   value=40, help_text='Результат в секундах')],
        [put_button("Рассчитать", onclick=lambda: calculate_points(
            pin.gender, pin.short_run, pin.long_run, pin.jump, pin.gym, pin.swimming, 'result'))],
        [span(put_text("", scope="result"), col=2)]
    ], cell_width="50%"), "gap: 10px")
