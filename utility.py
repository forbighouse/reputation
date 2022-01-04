import unittest
import random
import numpy as np
from collections import defaultdict
import scipy.stats as st


def rec_dd():
    """
    迭代生成字典
    :return: 字典迭代器
    """
    return defaultdict(rec_dd)


def random_int_list(start, stop, length):
    """
    生成随机数组
    :param start:   取值范围起始点
    :param stop:    取值范围终点
    :param length:  随机取值的长度
    :return:        随机整数数组列表
    """
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list


def calculate(template, loc=None):
    """
    计算列表的统计结果
    :param template:  待计算的列表
    :param loc:       如果计算逆向百分点函数，给出想要位置的概率是多少
    :return:   列表中的最小值、均值、最大值、方差、中值、列表中95的值在该值只下
    """
    _mean = np.mean(template)
    _max = np.max(template)
    _min = np.min(template)
    _std = np.std(template)
    _med = np.median(template)
    _ppf = st.norm.ppf(loc, loc=_mean, scale=_std)
    return _min, _mean, _max, _std, _med, _ppf


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
