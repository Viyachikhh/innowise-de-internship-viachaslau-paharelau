import re
import logging
from my_utils.my_consts import PERIODS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def define_period_prefix(key: str, regexpr: re.Pattern):
    """
    Есть ли информация о месяце в ключе
    
    :param key: Ключ файла в бакете
    :type key: str
    """
    prefix = re.search(regexpr, key)
    if prefix is not None and len(set([prefix.group(0)]) & PERIODS) > 0:
        return prefix.group(0)
    return None



