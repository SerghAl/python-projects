from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import gspread
import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
G_SHEET_KEY = os.getenv('G_SHEET_KEY')

app_dir = os.path.dirname(
    os.path.abspath(__file__))
credentials_dir = os.path.join(app_dir, 'credentials.json')


def format_rating(sorted_rating_list: list) -> str:
    text = ''

    for athlete in sorted_rating_list:
        print(athlete)
        text += f'{athlete[0]}: {athlete[2]}\n'

    return text


def get_google_sheet(event):
    gc = gspread.service_account(credentials_dir)
    sheet = gc.open_by_key(G_SHEET_KEY).worksheet(event)

    data = sheet.get_all_values()

    return data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('UPDATE: ', update)
    list_of_values = get_google_sheet('skiing')
    rating_list = []

    for row in list_of_values[1:]:
        athlete = row[0]
        sex = row[1]
        scores = sum(list(map(int, row[2:])))

        rating_list.append([athlete, sex, scores])

    rating_list.sort(key=lambda x: x[2], reverse=True)

    message = format_rating(rating_list)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def main():
    print('RUN TG_RATING_BOT')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    app = ApplicationBuilder().token(TG_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == '__main__':
    main()
