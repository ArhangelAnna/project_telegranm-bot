import logging
import sqlite3
from typing import List, Any

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler

TOKEN = "5357056348:AAHKBN4Va0NVAmGAxkeShO3oQZDpIVBeenI"
'''logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)'''
# Добавление всех клавиатур
reply_keyboard = [['/add', '/complete'],
                  ['/site', '/work_time']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
reply_keyboard1 = [['По названию', 'По категории']]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=False)
reply_keyboard2 = [['Существующюю', 'Новую']]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)
reply_keyboard3 = [["Далее"]]
markup3 = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=False)
# Подключение к БД
con = sqlite3.connect("record_db.sqlite", check_same_thread=False)
# Создание курсора
cur = con.cursor()


# Начало работы бота
def start(update, context):
    try:
        update.message.reply_text(
            f'''ghjfgghh
            hjjkiijjjikkkkk''',
            reply_markup=markup)  # (приветственное сообщение,добавление основной кллавиатуры)
        # Получение user_id и user_name
        user_id = update.message.from_user['id']
        user_name = update.message.from_user['username']
        # Получение последнего id пользователя
        _id = list(cur.execute(f'''SELECT id FROM users ''').fetchall())
        cur.execute(
            f'''INSERT INTO  users(id, user_id, username) VALUES({_id[-1][0] + 1}, {user_id}, "{user_name}")''').fetchall()
        con.commit()
        # con.close()
    except:
        pass


# Начало диалога добавления записи(написание самой записи
def add(update, context):
    update.message.reply_text(
        "Вы можете прервать запись, послав команду /stop_add.\n"
        "Напишите запись, которую  хотите добавить ?", reply_markup=ReplyKeyboardRemove())

    return 1


# 2 стадия добавления(выбор категории куда добавлять запись)
def selecting_category(update, context):
    try:
        #
        context.user_data['record'] = update.message.text
        update.message.reply_text(
            f"В какую категорию хотите дабавить эту запись?\n"
            f"На клавиатуре выберете будите использовать уже существующюю или новую", reply_markup=markup2)
        return 2
    except:
        pass


def selecting_category_2(update, context):
    method = update.message.text
    update.message.reply_text(
        f"Вы выбрали - {method}", reply_markup=markup3)
    if method == "Новую":
        return 3
    else:
        return 4


def new_category(update, context):
    try:
        update.message.reply_text(f"Напишите название новой категории", reply_markup=ReplyKeyboardRemove())
        return 5
    except:
        pass


def new_category_2(update, context):
    try:
        category = update.message.text
        update.message.reply_text(
            f"Новая категория записана", reply_markup=markup3)
        context.user_data['category'] = category
        _id = list(cur.execute(f'''SELECT id FROM categorys''').fetchall())
        cur.execute(
            f'''INSERT INTO categorys(id,category) VALUES({_id[-1][0] + 1},"{category}")''').fetchall()
        con.commit()
        return 6
    except:
        pass


def old_category(update, context):
    try:
        category = cur.execute(f'''SELECT id FROM categorys''').fetchall()
        categorys = ""
        for el in category:
            categorys = categorys + el[0] + ","
        update.message.reply_text(f"Вот все существующие категории\n"
                                  f"{categorys}", reply_markup=ReplyKeyboardRemove())
        return 5
    except:
        pass


def short_name(update, context):
    update.message.reply_text(
        f"Напишите кароткое название записи", reply_markup=ReplyKeyboardRemove())
    return 7


# конец добавления(оповещение о добавлении)
def end_add(update, context):
    name = update.message.text
    update.message.reply_text(
        f"Вы добавили эту запись '{context.user_data['record']}\n"
        f"В эту категорию {context.user_data['category']}\n"
        f"C таким каротким названием{name}", reply_markup=markup)
    user_id = update.message.from_user['id']
    _id = list(cur.execute(f'''SELECT id FROM records ''').fetchall())
    cur.execute(
        f'''INSERT INTO  records(id, user_id, record, name, category, complete) 
                VALUES({_id[-1][0] + 1}, {user_id}, "{context.user_data['record']}", 
                "{name}", "{context.user_data['category']}", True)''').fetchall()
    con.commit()
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


# Прекращение добавления
def stop_add(update, context):
    update.message.reply_text("Вы прекратили добавления", reply_markup=markup)
    return ConversationHandler.END


# Начало удаления(предупреждение, удаление старой клавиатуры)
def delete(update, context):
    update.message.reply_text(
        f"!ВЫ ТОЧНО ХОТИТЕ ПОМЕТЬ ЗАПИСЬ КАК ВЫПОЛНЕНУЮ! "
        f"Если  вы не хотите помечать пошлите команду /stop_delete.\n"
        f"А если хотите продолжить напишите любое другое", reply_markup=ReplyKeyboardRemove())
    return 1


# 2 стания удаления , 1\2 стадия выбора метода поиска(добавления новой клавиатуры)
def choosing_method(update, context):
    update.message.reply_text(
        f"Для начала выберете способ поиска нужной записи в клавиатуре", reply_markup=markup1)
    return 2


# 2 стания удаления , 2\2 стадия выбора метода поиска(выбор метода, разветвление диалога)
def choosing_method_2(update, context):
    method = update.message.text
    update.message.reply_text(
        f"Вы выбрали - {method}")
    if method == "По названию":
        return 3
    else:
        return 4


# 3 стадия  удаления или ... поиска, 1\2 поиск по названию(пользователь вводит название)
def by_name(update, context):
    update.message.reply_text(
        f"Напишите название записи")
    return 5


# 3 стадия удаления или ... поиска , 2\2 поиск по названию(пользователь выбирает точное название)
def by_name_2(update, context):
    name = update.message.text
    update.message.reply_text(
        f"Вот все записи с таким названием"
        f"{name}"
        f"Отправте точное назавание записи")
    return 6


# 3 стадия  удаления или ... поиска, 1\2 поиск по категории(пользователь вводит название)
def by_category():
    pass


def by_category_2():
    pass


def stop_delete(update, context):
    update.message.reply_text('Вы прикратили удаление', reply_markup=markup)
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            # Добавили user_data для сохранения ответа.
            1: [MessageHandler(Filters.text & ~Filters.command, selecting_category, pass_user_data=True)],
            # ...и для его использования.
            2: [MessageHandler(Filters.text & ~Filters.command, selecting_category_2, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, new_category, pass_user_data=True)],
            4: [MessageHandler(Filters.text & ~Filters.command, end_add, pass_user_data=True)],
            5: [MessageHandler(Filters.text & ~Filters.command, new_category_2, pass_user_data=True)],
            6: [MessageHandler(Filters.text & ~Filters.command, short_name, pass_user_data=True)],
            7: [MessageHandler(Filters.text & ~Filters.command, end_add, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('stop_add', stop_add)]
    )

    dp.add_handler(add_conv_handler)
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('complete', delete)],
        states={
            # Добавили user_data для сохранения ответа.
            1: [MessageHandler(Filters.text & ~Filters.command, choosing_method, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, choosing_method_2, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, by_name, pass_user_data=True)],
            4: [MessageHandler(Filters.text & ~Filters.command, by_category, pass_user_data=True)],
            5: [MessageHandler(Filters.text & ~Filters.command, by_name_2, pass_user_data=True)],
            6: [MessageHandler(Filters.text & ~Filters.command, by_category_2, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop_delete', stop_delete)]
    )

    dp.add_handler(delete_conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
