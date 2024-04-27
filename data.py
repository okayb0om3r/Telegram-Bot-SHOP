from datetime import datetime, timedelta
import sqlite3

conn = sqlite3.connect("shop_data.db", check_same_thread=False)
cursor = conn.cursor()


def add_user(uid, username):
    date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    resp = cursor.execute(f"SELECT count(*) FROM users WHERE user_id = {uid}").fetchone()[0]
    if resp == 0:
        cursor.execute("INSERT INTO users (user_id, username, reg_date) VALUES (?, ?, ?)", (uid, username, date))
        conn.commit()
        return True
    else:
        user, payments = get_user(uid)
        if user[5] == 1:
            return -1
        if user[2] != username:
            cursor.execute(f"UPDATE OR IGNORE users SET username = '{username}' WHERE user_id = {uid}")
            conn.commit()
        return False


def get_user(uid):
    user = cursor.execute(f"SELECT * FROM users WHERE user_id = {uid}").fetchone()
    payments = conn.execute(f'SELECT * FROM orders WHERE user_id = {uid} AND status = 1').fetchall()
    return user, payments


def get_user_by_username(username):
    user = cursor.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchone()
    payments = conn.execute(f"SELECT * FROM orders WHERE username = '{username}' AND status = 1").fetchall()
    return user, payments


def ban_user(uid):
    cursor.execute(f"UPDATE users SET ban = 1 WHERE user_id = {uid}")
    conn.commit()


def pardon_user(uid):
    cursor.execute(f"UPDATE users SET ban = 0 WHERE user_id = {uid}")
    conn.commit()


def get_all_user_ids(text):
    cursor.execute(f'SELECT user_id FROM users')
    row = cursor.fetchall()
    return row


# --PAYMENT--
def get_payment(payment_id):
    payment = cursor.execute(f"SELECT * FROM orders WHERE payment_id = '{payment_id}'").fetchone()
    return payment


def create_payment(message, payment_id, items, price, address):
    date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(
        "INSERT INTO orders (user_id, username, purchase_date, payment_id, items, price, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (message.from_user.id, message.from_user.username, date, payment_id, items, price, address))
    conn.commit()


def confirm_payment(payment_id):
    cursor.execute(f"UPDATE orders SET status = 1 WHERE payment_id = '{payment_id}'")
    conn.commit()


def get_len_of_orders():
    cursor.execute("select * from orders")
    results = cursor.fetchall()
    return len(results)


def update_search_time(uid):
    now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(f"UPDATE users SET last_search = '{now}' WHERE user_id = {uid}")
    conn.commit()


def update_last_order_date(uid):
    now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(f"UPDATE users SET last_order_date = '{now}' WHERE user_id = {uid}")
    conn.commit()


def get_last_order_date(uid):
    date = conn.execute(f'SELECT * FROM users WHERE user_id = {uid}').fetchone()
    return date[4]


def control_search_time(uid):
    user = conn.execute(f'SELECT * FROM users WHERE user_id = {uid}').fetchone()
    str_time = user[4]
    if str_time == "None":
        update_search_time(uid)
        return True
    last_search = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
    if datetime.now() - last_search < timedelta(minutes=1):
        return False
    update_search_time(uid)
    return True


# --GOODS--
def get_goods(todict=False):
    resp = cursor.execute("SELECT * FROM goods").fetchall()
    if not todict:
        return resp
    columns = [col[0] for col in cursor.description]

    result_dict = []
    for row in resp:
        result_dict.append(dict(zip(columns, row)))

    return result_dict


def get_good_by_id(_id):
    resp = cursor.execute(f"SELECT * FROM goods WHERE id = {_id}").fetchone()
    return resp
