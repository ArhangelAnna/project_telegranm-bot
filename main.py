import logging
import sqlite3
from typing import List, Any

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
# Добавление всех клавиатур
reply_keyboard = [['/add', '/complete', '/view']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
reply_keyboard1 = [['По названию', 'По категории', 'Всё']]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=False)
reply_keyboard2 = [['Существующюю', 'Новую']]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)
reply_keyboard3 = [["Далее"]]
markup3 = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=False)
reply_keyboard4 = [['По категории', "Всё"]]
markup4 = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=False)
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
    except:
        pass


# Начало диалога добавления записи(написание самой записи
def add(update, context):
    update.message.reply_text(
        "Вы можете прервать запись, послав команду /stop_add.\n"
        "Напишите запись, которую  хотите добавить ?", reply_markup=ReplyKeyboardRemove())

    return 1


# 2 стадия добавления , 1/2 выбора куда добавлять
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


# 2 стадия добавления , 2/2 выбора куда добавлять
def selecting_category_2(update, context):
    method = update.message.text
    update.message.reply_text(
        f"Вы выбрали - {method}", reply_markup=markup3)
    if method == "Новую":
        return 3
    else:
        return 4


# 3 этап добавления, 1/2  создание новой категории
def new_category(update, context):
    try:
        update.message.reply_text(f"Напишите название новой категории", reply_markup=ReplyKeyboardRemove())
        return 5
    except:
        pass


# 3 этап добавления, 2/2  создание новой категории
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


# 3 этап добавления, 1/2  старой категории . Вывод всех категорий
def old_category(update, context):
    category = cur.execute(f'''SELECT id,category FROM categorys ''').fetchall()
    categorys = ""
    for el in category:
        categorys = categorys + str(el[0]) + ": " + el[1] + "\n"
    update.message.reply_text(f"Вот все существующие категории\n"
                              f"{categorys}\n"
                              f"Напишите ту категорию в каторую хотите добавить", reply_markup=ReplyKeyboardRemove())
    return 8


# 3 этап добавления, 2/2  старой категории . Выбор старой категории
def old_category_2(update, context):
    category = update.message.text
    context.user_data['category'] = category
    update.message.reply_text(
        f"Вы выбрали категорию  - {category}", reply_markup=markup3)
    return 6


#4 этап добавления 
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


# Начало помечания(предупреждение, удаление старой клавиатуры)
def complete(update, context):
    update.message.reply_text(
        f"!ВЫ ТОЧНО ХОТИТЕ ПОМЕТЬ ЗАПИСЬ КАК ВЫПОЛНЕНУЮ! "
        f"Если  вы не хотите помечать пошлите команду /stop_complete.\n"
        f"А если хотите продолжить нажмите далее", reply_markup=markup3)
    return 1


# 2 стания помечания , 1\2 стадия выбора метода поиска(добавления новой клавиатуры)
def choosing_method(update, context):
    update.message.reply_text(
        f"Для начала выберете способ поиска нужной записи в клавиатуре", reply_markup=markup1)
    return 2


# 2 стания помечания , 2\2 стадия выбора метода поиска(выбор метода, разветвление диалога)
def choosing_method_2(update, context):
    method = update.message.text
    update.message.reply_text(
        f"Вы выбрали - {method}", reply_markup=markup3)
    if method == "По названию":
        return 3
    elif method == "По названию":
        return 4
    else:
        return 6


# 3 стадия  помечания , поиск по названию(пользователь вводит название)
def by_name(update, context):
    user_id = update.message.from_user['id']
    name = cur.execute(f'''SELECT id, name FROM records WHERE user_id = {user_id}''').fetchall()
    names = ""
    for el in name:
        names = names + str(el[0]) + "- " + el[1] + "\n"
    update.message.reply_text(
        f"Вот все названия записей"
        f"{names}"
        f"Напиши номер записи, которую хотите пометить", reply_markup=ReplyKeyboardRemove())
    return 7


# 3 стадия  помечания или ... поиска, 1\2 поиск по категории(пользователь вводит название)
def by_category(update, context):
    category = cur.execute(f'''SELECT id, category FROM categorys''').fetchall()
    categorys = ""
    for el in category:
        categorys = categorys + str(el[0]) + ": " + el[1] + "\n"
    update.message.reply_text(f"Вот все существующие категории\n"
                              f"{categorys}"
                              f"Напишите ту категорию , в каторой хотите пометить запись",
                              reply_markup=ReplyKeyboardRemove())
    return 5


# 3 стадия  помечания или ... поиска, 2\2 поиск по категории(пользователь вводит название)
def by_category_2(update, context):
    category = update.message.text
    user_id = update.message.from_user['id']
    record = cur.execute(f'''SELECT id , name, record  FROM records WHERE category = "{category}"
                           AND user_id = {user_id} AND complete = 1''').fetchall()
    records = ""
    for el in record:
        records = records + str(el[0]) + "- " + el[1] + ": " + el[2] + "\n"
    update.message.reply_text(f"Вот все записи в этой категории\n"
                              f"{records}"
                              f"Напишите номер записи , которую хотите пометить как выполненую")
    return 7


#
def by_all(update, context):
    user_id = update.message.from_user['id']
    _all = cur.execute(
        f'''SELECT id, name, record FROM records WHERE user_id={user_id} AND complete = 1''').fetchall()
    categorys = ""
    for el in _all:
        categorys = categorys + str(el[0]) + "- " + el[1] + ": " + el[2] + "\n"
    update.message.reply_text(
        f"Вот все записи\n"
        f"{categorys}"
        f"Напишите номер записи ,которую хотите пометить как выполненую", reply_markup=ReplyKeyboardRemove())
    return 7


#
def end_complete(update, context):
    id = update.message.text
    cur.execute(f'''UPDATE records SET complete = 0 WHERE id = {id} ''').fetchall()
    record = cur.execute(f'''SELECT name, record  FROM records WHERE id = {id}''').fetchall()
    update.message.reply_text(f"Вы пометили эту запись:\n"
                              f"{record[0][0]} : {record[0][1]}\n"
                              f" Как сделаную", reply_markup=markup)
    return ConversationHandler.END


#
def stop_complete(update, context):
    update.message.reply_text('Вы прикратили помечание', reply_markup=markup)
    return ConversationHandler.END


#
def view(update, context):
    update.message.reply_text(
        "Вы можете прервать поиск, послав команду /stop_view.\n"
        "Вы можете посмотреть все задания или в определённой категории , "
        "или посмотреть запись с определёным названием. \n"
        "Для этого выберите нужный вам способ в клавиатуре",
        reply_markup=markup4)
    return 1


def choosing_method_v(update, context):
    method = update.message.text
    update.message.reply_text(
        f"Вы выбрали - {method}", reply_markup=markup3)
    if method == "По категории":
        return 2
    else:
        return 3


def by_category_v(update, context):
    category = cur.execute(f'''SELECT id, category FROM categorys''').fetchall()
    categorys = ""
    for el in category:
        categorys = categorys + str(el[0]) + ": " + el[1] + "\n"
    update.message.reply_text(f"Вот все существующие категории\n"
                              f"{categorys}"
                              f"Напишите ту категорию , которую хотите посмотреть",
                              reply_markup=ReplyKeyboardRemove())
    return 4


def end_view_category(update, context):
    try:
        category = update.message.text
        user_id = update.message.from_user['id']
        category = cur.execute(
            f'''SELECT id, name, record FROM records 
            WHERE category = "{category}" AND user_id={user_id} AND complete = 1''').fetchall()
        if len(category) == 0:
            update.message.reply_text(
                f"Записи с такой категорией  нет", reply_markup=markup)
        else:
            categorys = ""
            for el in category:
                categorys = categorys + str(el[0]) + "- " + el[1] + ": " + el[2] + "\n"
            update.message.reply_text(f"Вот все записи с такой категорией"
                                      f"{categorys}", reply_markup=markup)
        return ConversationHandler.END

    except:
        update.message.reply_text(f"Такой категории нет")


def end_view_all(update, context):
    try:
        user_id = update.message.from_user['id']
        _all = cur.execute(
            f'''SELECT id, name, record FROM records WHERE user_id={user_id} AND complete = 1''').fetchall()
        categorys = ""
        for el in _all:
            categorys = categorys + str(el[0]) + "- " + el[1] + ": " + el[2] + "\n"
        update.message.reply_text(
            f"Вот все записи\n"
            f"{categorys}", reply_markup=markup)
        return ConversationHandler.END
    except:
        pass


def stop_view(update, context):
    update.message.reply_text('Вы прикратили поиск', reply_markup=markup)
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    # Диалог добавления записи
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, selecting_category, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, selecting_category_2, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, new_category, pass_user_data=True)],
            4: [MessageHandler(Filters.text & ~Filters.command, old_category, pass_user_data=True)],
            5: [MessageHandler(Filters.text & ~Filters.command, new_category_2, pass_user_data=True)],
            6: [MessageHandler(Filters.text & ~Filters.command, short_name, pass_user_data=True)],
            7: [MessageHandler(Filters.text & ~Filters.command, end_add, pass_user_data=True)],
            8: [MessageHandler(Filters.text & ~Filters.command, old_category_2, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop_add', stop_add)]
    )

    dp.add_handler(add_conv_handler)
    # Диалог помечания как выполненого
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('complete', complete)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, choosing_method, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, choosing_method_2, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, by_name, pass_user_data=True)],
            4: [MessageHandler(Filters.text & ~Filters.command, by_category, pass_user_data=True)],
            5: [MessageHandler(Filters.text & ~Filters.command, by_category_2, pass_user_data=True)],
            6: [MessageHandler(Filters.text & ~Filters.command, by_all, pass_user_data=True)],
            7: [MessageHandler(Filters.text & ~Filters.command, end_complete, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop_complete', stop_complete)]
    )
    dp.add_handler(delete_conv_handler)
    # Диалог помечания как выполненого
    view_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('view', view)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, choosing_method_v, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, by_category_v, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, end_view_all, pass_user_data=True)],
            4: [MessageHandler(Filters.text & ~Filters.command, end_view_category, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop_view', stop_view)]
    )
    dp.add_handler(view_conv_handler)
    updater.start_polling()
    updater.idle()
    con.close()


if __name__ == '__main__':
    main()
