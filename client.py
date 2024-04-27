from bot import bot
from data import add_user, get_last_order_date, get_goods
from markups import create_back_to_menu_markup, create_main_menu_markup, create_del_menu_markup
from menu import *
from calc import calculate
from config import support_id, notification, canceled_action, error_text, buy_menu_text, order_capt_1, order_capt_2, \
    address_menu_text
from datetime import datetime, timedelta
from payment import generate_payment, check_payment
from admin_panel import new_user_notification


def on_start(message):
    if not message.from_user.username:
        bot.send_message(message.from_user.id, "установите username, чтобы пользоваться ботом")
        return
    resp = add_user(message.from_user.id, message.from_user.username)
    if resp == -1:
        return
    elif resp:
        new_user_notification(message.from_user.username)

    markup = create_main_menu_markup()
    text = main_menu_text.format(name=message.from_user.first_name)
    with open(f'{os.path.dirname(__file__)}/start.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup)


def func_handler(message):
    if message.chat.type == 'private':
        if message.text.startswith("!calc"):
            markup = create_del_menu_markup()

            bot.delete_message(message.chat.id, message.id)
            try:
                items = message.text.split()[1:]
                items = list(map(int, items))
                text, _ = calculate(items)

                bot.send_message(message.from_user.id, text=text, reply_markup=markup)
            except ValueError:
                bot.send_message(message.from_user.id, text=error_text, reply_markup=markup)


def show_buy_menu(call):
    last_time = get_last_order_date(call.message.chat.id)
    # last_time = "None"
    if last_time != "None":
        date_time_obj = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        delta = timedelta(minutes=2)
        time = datetime.now() - date_time_obj
        if time < delta:
            markup = create_back_to_menu_markup()
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=order_capt_1,
                                     reply_markup=markup)
            return
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=buy_menu_text)
    bot.register_next_step_handler(call.message, get_address, call)


def get_address(order, call):
    bot.delete_message(chat_id=order.chat.id, message_id=order.message_id)
    markup = create_back_to_menu_markup()
    if order.text == "0":
        bot.edit_message_caption(chat_id=order.chat.id, message_id=call.message.id, caption=canceled_action,
                                 reply_markup=markup)
        return

    valid_ids = list(map(lambda x: x["id"], get_goods(todict=True)))
    try:
        ids = list(map(int, order.text.split()))
        if not set(ids) <= set(valid_ids) or len(ids) > 5:
            raise ValueError
    except ValueError:
        bot.edit_message_caption(chat_id=order.chat.id, message_id=call.message.id, caption=order_capt_2,
                                 reply_markup=markup)
        return

    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=address_menu_text)
    bot.register_next_step_handler(call.message, generate_payment, call.message, ids)


def init_client_funcs():
    bot.message_handler(commands=['start'])(on_start)
    bot.message_handler(content_types=['text'])(func_handler)


@bot.callback_query_handler(func=lambda call: not call.data.startswith("ADM"))
def on_callback_query(call):
    if call.data == "профиль":
        show_profile_menu(call)
    elif call.data == "назад_в_меню":
        show_main_menu(call)
    elif call.data == "помощь":
        show_help_menu(call)
    elif call.data == "правила":
        show_rules_menu(call)
    elif call.data == "калькулятор":
        show_calc_menu(call)
    elif call.data == "закрыть":
        del_menu(call)
    elif call.data == "купить":
        show_buy_menu(call)
    elif call.data.startswith("проверить_платеж"):
        check_payment(call)
    elif call.data == "наличие":
        show_availability_menu(call)
