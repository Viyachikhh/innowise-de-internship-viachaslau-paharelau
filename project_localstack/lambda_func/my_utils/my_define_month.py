import re
import logging
from my_utils.my_consts import PERIODS, MONTH_PREFIXES

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def define_period_prefix(key: str, regexpr: re.Pattern):
    """
    Есть ли информация о периоде в ключе
    
    :param key: Ключ файла в бакете
    :type key: str
    """
    prefix = re.search(regexpr, key)
    if prefix is not None and len(set([prefix.group(0)]) & PERIODS) > 0:
        return prefix.group(0)
    return None

def define_month_prefix(key: str):
    """
    Есть ли информация о месяце в ключе
    
    :param key: Ключ файла в бакете
    :type key: str
    """
    for prefix in MONTH_PREFIXES:
        if prefix in key:
            return prefix
    return None

