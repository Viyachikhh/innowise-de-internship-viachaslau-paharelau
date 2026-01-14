from my_utils.my_consts import MONTHS


def define_month_prefix(key):
    """
    Есть ли в нашем ключе информация о месяце
    """
    for month_prefix in MONTHS:
        if month_prefix in key:
            return month_prefix
    return None



