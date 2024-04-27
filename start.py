from bot import bot
from admin_panel import init_admin_funcs
from client import init_client_funcs

init_admin_funcs()
init_client_funcs()

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
