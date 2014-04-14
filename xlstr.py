__author__ = 'Administrator'


def substr(src_str:str, first:str, end:str):
    """

    :param src_str: 源字符串
    :param first: 开始字符串
    :param end:结束字符串
    :return:
    """
    start=src_str.find(first)+len(first)
    end=src_str.find(end, src_str.find(first)+1)
    return src_str[start:end]