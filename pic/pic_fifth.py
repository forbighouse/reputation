import random
import uuid
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


#  一个优质的节点被腐化后的声誉变化
def fifth_pic():
    _zone_num, _all_vehicle_num = print_one_day(14, 14)
    select_num = 2
    x_time = range(0, 5)
    mu = [5, 17, 19, 21]
    init_reputation = 10
    ratings = [0.5, 0.6, -0.6, -0.7, -0.8, -0.9]
    #  一个节点干了件不好的事，获得了一个不好的评分，不好的评分直接在一个交易里出现
    #  评估一个节点的声誉会立即审计所有的交易
    #  一个交易需要多久才会被认证，并且通过阈值
    #  1. 我们需要一个tip的集合，判断包含做错事的交易是不是在里面

    #  发布交易的结构
    dict_issued = rec_dd()
    #  参与事件的结构
    dict_event = rec_dd()
    #  tip集合，每个分区只有一个tip的数量
    dict_tip = rec_dd()
    #  剩余tip的集合，每个分区是一个tip列表，表示每个step之后tip的数量
    dict_remind_tip = rec_dd()

    for i in range(0, _all_vehicle_num):
        #  交易用32位十六进制的uuid表示
        trans_id = uuid.uuid1().hex
        dict_issued[trans_id] = 0
        dict_event[trans_id] = []

    #  交易的集合是字典，因为需要计算累积权重
    #  tip的集合只能是字典，因为需要计算累积权重
    #  key是tip的id，value是累积权重
    #
    list_trans = []
    ledger = nx.DiGraph()
    trans_id = 0
    trans_status = rec_dd()
    for i in x_time:
        num_new_tip = st.poisson.rvs(mu=mu[0], size=1, random_state=None)
        num_new_tip = num_new_tip[0]
        #  在初始时间，tip正常到达并直接进入
        #  列表代表账本为空，说明账本被重置，新到达的交易要补充进账本里


if __name__ == '__main__':
    fifth_pic()
