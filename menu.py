from markups import create_back_to_menu_markup, create_main_menu_markup
from config import main_menu_text, rules, calc_menu_text, support, profile_text
from calc import get_availability_text
from telebot import types
from bot import bot
from data import get_user
import os


def show_main_menu(call):
    markup = create_main_menu_markup()

    text = main_menu_text.format(name=call.from_user.first_name)
    with open(f'{os.path.dirname(__file__)}/start.png', 'rb') as photo:
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id,
                               media=types.InputMediaPhoto(photo))

        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption=text,
                                 reply_markup=markup)


def show_help_menu(call):
    text = f"поддержка: @{support}"
    markup = create_back_to_menu_markup()
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=text,
                             reply_markup=markup)


def show_rules_menu(call):
    markup = create_back_to_menu_markup()
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=rules,
                             reply_markup=markup)


def show_calc_menu(call):
    markup = create_back_to_menu_markup()
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=calc_menu_text,
                             reply_markup=markup)


def show_availability_menu(call):
    markup = create_back_to_menu_markup()
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=get_availability_text(),
                             reply_markup=markup, parse_mode="markdown")


def del_menu(call):
    bot.delete_message(call.message.chat.id, call.message.id)


def show_profile_menu(call):
    photos = bot.get_user_profile_photos(call.from_user.id)
    first_name = call.from_user.first_name
    info = get_user(call.from_user.id)
    _id, user_id, username, reg_date, _, _ = info[0]
    count = 0 if not info[1] else len(info[1])

    text = profile_text.format(first_name=first_name, user_id=user_id, username=username, reg_date=reg_date,
                               count=count)

    markup = create_back_to_menu_markup()

    if photos.total_count > 0:
        photo = photos.photos[0][0]
        file_id = photo.file_id
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id,
                               media=types.InputMediaPhoto(file_id))
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=text,
                                 reply_markup=markup)
    else:
        with open(f'{os.path.dirname(__file__)}/default.png', 'rb') as photo:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id,
                                   media=types.InputMediaPhoto(photo))
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id, caption=text,
                                     reply_markup=markup)
