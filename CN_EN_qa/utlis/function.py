# -*- coding: utf-8 -*-

'''Util functions '''
import os
import re
import jieba
from pypinyin import pinyin, Style

def delete_excessive_files(folder_path, files_number):
    """判断文件数量，超过一定数量则清空，避免存储空间不够

    Args:
        folder_path: 准备删除的文件夹的路径 例如：'./static/output/translate_output/'
        files_number: 文件数量超过多少则将文件夹清空
    Returns:
        No Return
    """
    # print("delete_excessive_files(...) is called.")
    global Files_Num  # 存储文件的数量
    Files_Num = len([lists for lists in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, lists))])
    #print("现输出文件夹文件数量.encode('utf-8'), Files_Num)
    if Files_Num >= files_number:  # 判断存储的文件数量是不是超过一定的值。避免存储空间满了。
        for i in os.listdir(folder_path):
            path_file = os.path.join(folder_path, i)  # 取文件路径
            # print(path_file)
            # print(os.path.isfile(path_file))  # 判断是不是文件
            if os.path.isfile(path_file):
                os.remove(path_file)

def text_to_pinyin(text):
    """将文字转化为拼音加韵律的的形式

    Args:
        text: 输入的中文文本
        files_number: 文件数量超过多少则将文件夹清空
    Returns:
        转换为拼音加音律的字符串。例如：xiao3 ming2 shuo4 shi4
    """
    # seg_list = jieba.cut(txt, cut_all=True) # 会切出重复的部分
    # print("Full Mode: " + " ".join(seg_list))  # 全模式
    # print("Full Mode: " + " ".join(seg_list))  # 全模式
    seg_list = jieba.cut(text, cut_all=False) # 无重复的部分
    # print("Default Mode: " + " ".join(seg_list))  # 精确模式
    seg_list = " ".join(seg_list)
    result = pinyin(seg_list, style=Style.TONE3)
    result = [i for lst in result for i in lst]
    # print("result的结果",result)
    pinyin_str = [x.strip() for x in result]
    #print("x的结果", pinyin_str)
    pinyin_str = ' '.join(pinyin_str)
    r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~”“。！，、…—～﹏￥]+'
    #pinyin_str = re.sub(r, '', pinyin_str)
    return pinyin_str

def dict_get(dict1, objkey, default):
    """获取字典中的objkey对应的值，适用于字典嵌套

    Args:
        dict1: 字典
        objkey: 目标key
        default: 找不到时返回的默认值
    Returns:
        返回所对应的目标key对应的值
    Example:
        dicttest={"result":{"to_lang":"to_lang", "from_lang":"from_lang", "result": "result"},   "msg":"设备设备序列号或验证码错误"}
        ret=dict_get(dicttest, 'to_lang', None)
        print(ret)
    """
    tmp = dict1
    for k, v in tmp.items():
        if k == objkey:
            return v
        else:
            # if type(v) is dict1:
            # if isinstance(v, dict1):
            if type(v).__name__ == 'dict':
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
    return default
