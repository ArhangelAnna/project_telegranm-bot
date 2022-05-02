import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler

TOKEN = "5357056348:AAHKBN4Va0NVAmGAxkeShO3oQZDpIVBeenI"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
# Добавление всех клавиатур
reply_keyboard = [['/add', '/delete'],
                  ['/site', '/work_time']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
reply_keyboard1 = [['По названию', 'По категории']]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=False)
# Подключение к БД
con = sqlite3.connect("record_db.sqlite_db.sqlite")

# Создание курсора
cur = con.cursor()


# Начало работы бота(приветственное сообщение,добавление основной кллавиатуры)
def start(update, context):
    update.message.reply_text(
        f'''ghjfgghh
            hjjkiijjjikkkkk''',
        reply_markup=markup
    )


# Начало диалога добавления записи(написание самой записи
def add(update, context):
    update.message.reply_text(
        "Вы можете прервать запись, послав команду /stop_add.\n"
        "Напишите запись, которую  хотите добавить ?")

    return 1


# 2 стадия добавления(выбор категории куда добавлять запись)
def selecting_category(update, context):
    # Сохраняем ответ в словаре.
    context.user_data['record'] = update.message.text
    userr_id = update.message.from_user
    print(userr_id)
    update.message.reply_text(
        f"В какую категорию хотите дабавить эту запись\n"
        f"Можете выбрать одну из существующих или придумать новую")
    return 2


# конец добавления(оповещение о добавлении)
def end_add(update, context):
    category = update.message.text
    update.message.reply_text(
        f"Вы добавили эту запись '{context.user_data['record']}\n"
        f"В эту категорию {category}'")
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


# Прекращение добавления
def stop_add(update, context):
    update.message.reply_text("Вы прекратили добавления")
    return ConversationHandler.END


# Начало удаления(предупреждение, удаление старой клавиатуры)
def delete(update, context):
    update.message.reply_text(
        f"!ВЫ ТОЧНО ХОТИТЕ УДАЛИТЬ ЗАПИСЬ! "
        f"Если  вы не хотите удалять  послите команду /stop.\n"
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


# 3 стадия , поиск по названию(пользователь вводит название)
def by_name(update, context):
    update.message.reply_text(
        f"Напишите название")


# Последняяя стадия удаления по имени
def delete_by_name(update, context):
    update.message.reply_text(
        f"Напишите название")


def stop(update, context):
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
            2: [MessageHandler(Filters.text & ~Filters.command, end_add, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, end_add, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop_add', stop_add)]
    )

    dp.add_handler(add_conv_handler)
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', delete)],
        states={
            # Добавили user_data для сохранения ответа.
            1: [MessageHandler(Filters.text & ~Filters.command, choosing_method, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, choosing_method_2, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(delete_conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
