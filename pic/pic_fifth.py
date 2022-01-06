import random
import uuid
import math
import random
import numpy as np
import scipy.stats as st
import networkx as nx
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import cProfile
import re

from origin_data_process import print_one_day
from utility import rec_dd, calculate
from my_ledger import DAGLedger
from selection.random_selection import tip_selection_random, find_tip_all
from selection.monte_carlo import tip_selection_mc

plt.rcParams["font.family"] = "SimHei"  # 设置全局中文字体为黑体


def find_all_successors(ledger_graph, _node):
    _number = []
    _select_successors = ledger_graph.successors(_node)
    for _successor in _select_successors:
        #  _successor肯定是一个，所以先加一个
        _number.append(_successor)
        #  开始迭代，
        _number += find_all_successors(ledger_graph, _successor)
    return _number


def count_accumulative_weight(ledger_graph, _node):
    _list_all_successors = find_all_successors(ledger_graph, _node)
    accumulative_weight = len(set(_list_all_successors))
    return accumulative_weight


'''
#  一个优质的节点被腐化后的声誉变化，终究还是要做这个比对
#  一个优质节点的定义为持续的获得好的评价，根据论文公式，这种好的评价来自两个方面
#    1） 积极的参与数据共享
#          1. 发布了多少交易
#          2. 参与了多少交易
#    2） 积极的参与交易共识
#          
'''


def func_x3(a):
    return a * a * a


class Vehicle:
    def __init__(self, _input_bad_share_ration, _input_bad_consensus_ration, share_count=100, consensus_count=100):
        self.share_count = share_count
        self.consensus_count = consensus_count
        self.bad_share_ratio = _input_bad_share_ration
        self.bad_consensus_ratio = _input_bad_consensus_ration
        self.accumulate_share_metric = 0
        self.accumulate_consensus_metric = 0
        self.tau_1 = 0.5
        self.tau_2 = 0.5
        self.beta = 0.01  # 共识的缩放因子
        self.share_metric = 0
        self.consensus_metric = 0

    def add_share_metric(self, _input):
        self.accumulate_share_metric += _input
        self.share_count += 1

    def add_consensus_metric(self, _input):
        self.accumulate_consensus_metric += _input
        self.consensus_count += 1

    def _get_consensus_metric(self):
        '''
        计算共识测度，
        :return:
        '''
        consensus_minus = round(self.consensus_count * self.bad_consensus_ratio)
        share_plus = self.consensus_count - consensus_minus
        _sum = share_plus - consensus_minus
        self.consensus_metric = 1 - math.exp(-(self.beta * _sum))
        self.consensus_metric = round(self.consensus_metric, 2)
        if self.consensus_metric < -1:
            self.consensus_metric = -1

    def _get_share_metric(self):
        R_minus = round(self.share_count * self.bad_share_ratio)
        R_plus = self.share_count - R_minus
        theta_plus = func_x3(R_plus) / (func_x3(R_plus) + func_x3(R_minus))
        theta_minus = func_x3(R_minus) / (func_x3(R_plus) + func_x3(R_minus))
        self.share_metric = ((theta_plus * R_plus) - (theta_minus * R_minus)) / (R_plus + R_minus)
        self.share_metric = round(self.share_metric, 2)

    def get_reputation(self):
        self._get_consensus_metric()
        self._get_share_metric()
        reputation_value = (self.tau_1 * self.share_metric) + (self.tau_2 * self.consensus_metric)
        return reputation_value

    def get_share_metric(self):
        self._get_share_metric()
        return self.share_metric

    def get_consensus_metric(self):
        self._get_consensus_metric()
        return self.consensus_metric


def fifth_pic():
    # _zone_num, _all_vehicle_num = print_one_day(14, 14)
    vehicle_num = 50
    x_bad_ratio = range(0, 100, 10)

    # 测试用
    share_rating = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    consensus_rating = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    bad_ratio = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    reputation = []
    share_ = []
    consensus = []
    for i in bad_ratio:
        x = Vehicle(i, i)
        reputation.append(x.get_reputation())
        share_.append(x.get_share_metric())
        consensus.append(x.get_consensus_metric())

    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1

    m = 10
    y_new_ticks = np.arange(0, m + 10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']

    ax.plot(bad_ratio, reputation, color=color_select[0], marker='o', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("reputation"))
    ax.plot(bad_ratio, share_, color=color_select[1], marker='^', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("share"))
    ax.plot(bad_ratio, consensus, color=color_select[2], marker='d', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("consensus"))

    plt.rcParams['font.sans-serif'] = "Arial"
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.legend(loc='upper right', prop={'size': 10})

    ax.set_xlabel("Misbehavior Ratio for One Vehicle", fontdict={'size': 10})
    ax.set_ylabel("Reputation metric", fontdict={'size': 10})
    ax.set_ylim(ymin=-1)
    ax.set_ylim(ymax=1.1)
    ax.set_xlim(xmin=0)
    # ax.set_xlim(xmax=x_time)
    ax.grid(linestyle='-', alpha=0.3)

    fig.tight_layout()
    # fig.savefig('output/fifth.pdf', dpi=300)
    plt.show()


def fifth02_pic():
    # _zone_num, _all_vehicle_num = print_one_day(14, 14)
    vehicle_num = 50
    # 推50次操作，包括共享和共识
    _num = range(0, 50)

    # 测试用
    share_rating = range(0, 50)
    consensus_rating = range(0, 50)

    bad_ratio = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    x = []
    reputation = []
    share_ = []
    consensus = []
    y = Vehicle(0, 0, 0, 0)
    for i in _num:
        x.append(i)
        y.add_share_metric(1)
        y.add_consensus_metric(1)
        reputation.append(y.get_reputation())
        share_.append(y.get_share_metric())
        consensus.append(y.get_consensus_metric())

    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1

    m = 10
    y_new_ticks = np.arange(0, m + 10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']

    ax.plot(x, reputation, color=color_select[0], marker='o', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("reputation"))
    ax.plot(x, share_, color=color_select[1], marker='^', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("share"))
    ax.plot(x, consensus, color=color_select[2], marker='d', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("consensus"))

    plt.rcParams['font.sans-serif'] = "Arial"
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.legend(loc='upper right', prop={'size': 10})

    ax.set_xlabel("Misbehavior Ratio for One Vehicle", fontdict={'size': 10})
    ax.set_ylabel("Reputation metric", fontdict={'size': 10})
    ax.set_ylim(ymin=-1)
    ax.set_ylim(ymax=1.1)
    ax.set_xlim(xmin=0)
    # ax.set_xlim(xmax=x_time)
    ax.grid(linestyle='-', alpha=0.3)

    fig.tight_layout()
    # fig.savefig('output/fifth.pdf', dpi=300)
    plt.show()

if __name__ == '__main__':
    fifth_pic()
