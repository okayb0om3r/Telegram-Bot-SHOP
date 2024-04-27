from config import support, support_id, y_token, card, order_capt, new_order_capt, paid_text
from markups import create_buy_menu_markup
from data import update_last_order_date, get_len_of_orders, create_payment, get_payment, confirm_payment
from yoomoney import Client, Quickpay
from calc import calculate, convert_text
from telebot import types
from bot import bot

client = Client(y_token)


def check_operation(payment_id):
    history = client.operation_history(label=payment_id)
    if history.operations:
        if history.operations[0].status == "success":
            return True
    return False


def generate_payment(message, orig_msg, ids):
    address = message.text
    user_id = message.chat.id
    bot.delete_message(chat_id=user_id, message_id=message.message_id)
    items, price = calculate(ids)

    update_last_order_date(user_id)
    payment_id = f"{user_id}-{get_len_of_orders() + 1}"
    create_payment(message, payment_id, " ".join(map(str, ids)), price, address)
    url = Quickpay(
        receiver=card,
        quickpay_form="shop",
        targets=items,
        paymentType="SB",
        sum=price,
        label=payment_id
    ).redirected_url
    markup = create_buy_menu_markup(payment_id, url)
    capt = order_capt.format(price=price, items=items, payment_id=payment_id)

    bot.edit_message_caption(chat_id=orig_msg.chat.id, message_id=orig_msg.message_id, caption=convert_text(capt),
                             reply_markup=markup, parse_mode="HTML")


def check_payment(call):
    cmd, payment_id = call.data.split(":")
    status = check_operation(payment_id) if not cmd.endswith("TEST") else 1
    if status:
        confirm_payment(payment_id)
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=paid_text.format(support=support))
        _, username, purchase_date, _, items, price, _, address = get_payment(payment_id)
        processed_items, _ = calculate(list(map(int, items.split())))
        text = new_order_capt.format(username=username, price=price, items=items, processed_items=processed_items,
                                     address=address, payment_id=payment_id, purchase_date=purchase_date)
        bot.send_message(chat_id=support_id, text=convert_text(text))
        bot.answer_callback_query(call.id, text='Успешно!')

    else:
        bot.answer_callback_query(call.id, text='Платеж не выполнен')
