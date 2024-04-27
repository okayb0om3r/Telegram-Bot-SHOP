from config import support_id, canceled_action, success_ban, error_text, sender_started, adm_menu_text, sender_ended, \
    success_pardon, notification
from data import get_all_user_ids, ban_user, pardon_user, get_user_by_username
from markups import create_admin_menu_markup, create_del_menu_markup
from bot import bot
from time import sleep
from telebot.apihelper import ApiTelegramException

def panel(message):
    if message.from_user.id == support_id:
        markup = create_admin_menu_markup()
        bot.send_message(message.from_user.id, adm_menu_text, reply_markup=markup)


def show_sender_menu(call):
    text = "Введите текст (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, spam, call.message)


def show_ban_menu(call):
    text = "Введите айди для бана (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, ban_user_adm, call.message)


def show_info_user(call):
    text = "Введите юзернейм для получения информации (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, get_info_user, call.message)


def new_user_notification(username):
    bot.send_message(support_id, text=notification.format(username=username))


def spam(message, orig_msg):
    text = message.text
    bot.delete_message(chat_id=support_id, message_id=message.message_id)
    markup = create_del_menu_markup()
    if text.startswith('-'):
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=canceled_action,
                              reply_markup=markup)
    else:
        info = get_all_user_ids(text)
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=sender_started)
        success_sent = 0
        for i in range(len(info)):
            sleep(0.5)
            try:
                bot.send_message(info[i][0], str(text))
            except ApiTelegramException: # пользователь из бд не авторизирован
                continue
            success_sent += 1
            
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id,
                              text=sender_ended.format(success_sent=success_sent))


def ban_user_adm(message, orig_msg):
    text = message.text
    bot.delete_message(chat_id=support_id, message_id=message.message_id)
    markup = create_del_menu_markup()
    if "-" in text:
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=canceled_action,
                              reply_markup=markup)
    else:
        try:
            ban_user(int(text))
            bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id,
                                  text=success_ban.format(user=text))
        except Exception as ex:
            print(ex)
            bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=error_text)


def pardon_user_adm(message, orig_msg):
    text = message.text
    bot.delete_message(chat_id=support_id, message_id=message.message_id)
    markup = create_del_menu_markup()
    if "-" in text:
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=canceled_action,
                              reply_markup=markup)
    else:
        try:
            pardon_user(int(text))
            bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id,
                                  text=success_pardon.format(user=text))
        except Exception as ex:
            print(ex)
            bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=error_text)


def get_info_user(message, orig_msg):
    username = message.text
    bot.delete_message(chat_id=support_id, message_id=message.message_id)
    markup = create_del_menu_markup()
    if username.startswith('-'):
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=canceled_action,
                              reply_markup=markup)
        return
    info = get_user_by_username(username)
    if not info[0]:
        bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=error_text, reply_markup=markup)
        return
    _, user_id, _, reg_date, last_order, ban = info[0]
    ban = True if ban == 1 else False

    payments = 0 if not info[1] else info[1]

    information = f"""Информация о пользователе ({username})
    user_id: {user_id}
    reg_date: {reg_date}
    ban: {ban}

    count of payments: {payments}

    """
    bot.edit_message_text(chat_id=support_id, message_id=orig_msg.message_id, text=information, reply_markup=markup)


def show_sender_menu(call):
    text = "Введите текст (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, spam, call.message)


def show_ban_menu(call):
    text = "Введите айди для бана (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, ban_user_adm, call.message)


def show_info_user(call):
    text = "Введите юзернейм для получения информации (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, get_info_user, call.message)


def show_pardon_menu(call):
    text = "Введите айди для разбана (для отмены '-')"
    bot.edit_message_text(chat_id=support_id, message_id=call.message.id, text=text)
    bot.register_next_step_handler(call.message, pardon_user_adm, call.message)


def init_admin_funcs():
    bot.message_handler(commands=['admin'])(panel)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ADM"))
def on_callback_query(call):
    if call.data == "ADMрассылка":
        show_sender_menu(call)
    elif call.data == "ADMбан":
        show_ban_menu(call)
    elif call.data == "ADMразбан":
        show_pardon_menu(call)
    elif call.data == "ADMинфо_юзер":
        show_info_user(call)
