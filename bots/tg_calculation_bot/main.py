from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os
import random
import string
import csv
import logging
from dotenv import load_dotenv
from typing import TypedDict


class CSVRecord(TypedDict):
    name: str
    sex: str
    event: str
    result: list[float]


load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')


def calculate_total_rating(data, discipline):
    filtered_data = [
        sp for sp in data if sp['event'].lower() == discipline.lower()]
    sorted_data = sorted(filtered_data, key=lambda sp: sum(
        sp['result']), reverse=True)
    ratings = {sp['name']: sum(sp['result']) for sp in sorted_data}

    return ratings


def group_by_discipline_gender(data):
    groups = {}
    for sp in data:
        discipline = sp['event']
        gender = sp['sex']

        if discipline not in groups:
            groups[discipline] = {}

        if gender not in groups[discipline]:
            groups[discipline][gender] = []

        groups[discipline][gender].append(sp['name'])

    return groups


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data: list[CSVRecord] = []

    file_name = id_generator()
    downloaded_file = await update.message.effective_attachment.get_file()
    file = await downloaded_file.download_to_drive(custom_path=file_name)

    with open(file, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar="'")
        for row in spamreader:
            data.append({
                'name': row[0],
                'sex': row[1],
                'event': row[2],
                'result': list(map(float, row[3].split(',')))
            })

    grouped_data = group_by_discipline_gender(data)

    message = "Полный рейтинг спортсменов:\n\n"

    for discipline, gender_groups in grouped_data.items():
        message += f"Дисциплина: {discipline}\n"
        for gender, athletes in gender_groups.items():
            message += f"Пол: {gender}\n"
            message += "Список спортсменов: " + ", ".join(athletes) + "\n"

    os.remove(file_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def main():
    print('RUN TG_CALCULATION_BOT')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    app = ApplicationBuilder().token(TG_TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, download_file))

    await app.run_polling()


if __name__ == '__main__':
    main()
