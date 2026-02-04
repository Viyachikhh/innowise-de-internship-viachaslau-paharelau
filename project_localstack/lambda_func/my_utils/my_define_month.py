from my_utils.my_consts import MONTHS


def define_month_prefix(key: str):
    """
    Есть ли информация о месяце в ключе
    
    :param key: Ключ файла в бакете
    :type key: str
    """
    for month_prefix in MONTHS:
        if month_prefix in key:
            return month_prefix
    return None



