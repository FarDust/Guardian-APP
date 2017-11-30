
__all__ = ['read_styles', 'parse_text', 'parse_info', 'read_styles']


def photo_id():
    i = 0
    while True:
        yield i
        i += 1


def read_styles(path: str, window):
    try:
        with open(path) as styles:
            window.setStyleSheet(styles.read())
    except FileNotFoundError as err:
        print(err)
        print("Error al leer {} , procediendo a usar estilos por defecto".format(path))


def parse_text(text):
    result = dict()
    try:
        result.update(json.loads(text))
    except json.JSONDecodeError:
        text = text.strip(" ")
        for line in text.split("\n"):
            if ":" in line and len(line.split(":")) == 2:
                result[line.split(":")[0]] = line.split(":")[1]
    return result


def parse_info(info):
    if isinstance(info, dict):
        string = str()
        for key in info.keys():
            if isinstance(info[key], dict):
                data = ["   " + i +
                        "\n" for i in parse_info(info[key]).split("\n")]
                string += "{key} = \n{data}\n".format(**
                                                      {"key": key, "data": data})
            else:
                string += "{key} = {data}\n".format(**
                                                    {"key": key, "data": info[key]})
        return string
    else:
        raise TypeError
