from data import get_goods, get_good_by_id


def calculate(ids):
    text = ""
    res = 0
    for i, _id in enumerate(ids):
        good = get_good_by_id(_id)
        if not good:
            continue
        res += good[2]
        text += f"{good[1]} ({good[2]})"
        if i + 1 == len(ids):
            break
        text += " + "
    text += f" = {res}"
    return text, res


def create_str_table(data):
    rows = len(data)
    cols = len(data[0])

    col_width = []
    for col in range(cols):
        columns = [str(data[row][col]) for row in range(rows)]
        col_width.append(len(max(columns, key=len)))

    separator = "-+-".join('-' * n for n in col_width)
    lines = []

    for i, row in enumerate(range(rows)):
        result = []
        for col in range(cols):
            item = str(data[row][col]).rjust(col_width[col])
            result.append(item)

        lines.append(' | '.join(result))

        if not i:
            lines.append(separator)

    return '\n'.join(lines)


def get_availability_text():
    goods = get_goods()
    goods.insert(0, ["ID", "наименование", "цена"])
    text = create_str_table(goods)
    return f'```🛒Товары {text}```'


def convert_text(text):
    lines = list(map(str.strip, text.split("\n")))
    res = ""
    for line in lines:
        if not line:
            res += "\n"
        res += "\n"
        res += line
    return res
