import random
import uuid
import math
import numpy as np
import scipy.stats as st
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

from origin_data_process import print_one_day
from utility import rec_dd, calculate
from my_ledger import DAGLedger
from selection.monte_carlo import tip_selection_mc
from selection.random_selection import tip_selection_random

plt.rcParams['axes.unicode_minus'] = False


def func_x3(a):
    return a * a * a


def fourth_main():
    mu = [5, 15, 30]
    x_time = range(0, 45)
    old_ratio = 0.05
    fourth_ledger = DAGLedger(tip_selection_mc)

    for time_epoch in x_time:
        num_new_tip = st.poisson.rvs(mu=mu[2], size=1, random_state=None)
        num_new_tip = num_new_tip[0]
        list_issuing_node = []

        print("******  epoch: " + str(time_epoch), "  ******")
        if time_epoch < 10:
            for j in range(0, num_new_tip):
                node_id = uuid.uuid1().hex
                list_issuing_node.append(node_id)
        else:
            num_old_node = math.ceil(num_new_tip * old_ratio)
            current_nodes = fourth_ledger.get_nodes()
            _old_nodes = random.sample(current_nodes, num_old_node)
            for j in range(0, num_new_tip-num_old_node):
                node_id = uuid.uuid1().hex
                list_issuing_node.append(node_id)
            for _n in _old_nodes:
                list_issuing_node.append(_n)
        fourth_ledger.add_new_transaction(time_epoch, list_issuing_node)

    # fourth_ledger.draw_ledger()

    _y = fourth_ledger.get_lazy_info()
    _res = []
    for i in _y:
        _x = fourth_ledger.get_transaction_state(i["trans_id"])
        if _x["end"] > 5:
            _res.append(_x["end"]-_x["start"])
    print(_res)
    sum_min, sum_mean, sum_max, sum_std, sum_med, sum_ppf = calculate(_res, 0.95)
    print("Lzay")
    print("      SET SIZ           : ", len(_y))
    print("      SUM MEAN          : ", int(sum_mean))
    print("      SUM MAX           : ", int(sum_max))
    print("      SUM MED           : ", int(sum_med))
    print("      SUM PPF(0.95)     : ", int(sum_ppf))
    print("")

    _z = fourth_ledger.get_normal_info()
    _res1 = []
    for i in _z:
        _x = fourth_ledger.get_transaction_state(i)
        # print(_x)
        if _x["end"] > 5:
            _res1.append(_x["end"]-_x["start"])
    print(_res1)
    sum_min, sum_mean, sum_max, sum_std, sum_med, sum_ppf = calculate(_res1, 0.95)
    print("Normal")
    print("      SET SIZE           : ", len(_z))
    print("      SUM MEAN          : ", int(sum_mean))
    print("      SUM MAX           : ", int(sum_max))
    print("      SUM MED           : ", int(sum_med))
    print("      SUM PPF(0.95)     : ", int(sum_ppf))
    print("")

    return


def func_exp(a):
    # -e ^ (-x) + 1
    _x = 0.1 * a
    _e = math.exp(_x)
    return round((-_e), 1) + 1


def func_ratio(x, y, z):
    y = y + (y * z)
    return x + (x * y)


def func_list_add(list1, list2):
    c = []
    for i in range(0, len(list2)):
        _ = round(list1[i]+list2[i], 1)
        c.append(_)
    return c


def fourth_pic01():
    """
    车辆的声誉随着作恶比率的变化
    :return:
    """

    '''
    #  当不良行为的比例是0.1的时候，此时车辆声誉的共识测度的值
    #  共识测度需要阈值和交易（前置）的<累积权重>
    #  根据公式，累积权重是后续所有交易的<实时权重>的和
    #          阈值是关注区域内所有节点的<最大实时权重>的均值
    #  因此，需要先确定节点<实时权重>的大小。
    #  论文中定义一个交易的实时权重与两个要素有关
    #      1. 发布的有效交易（不能是lazy）
    #      2. 共享数据的累积评分

    # 交易的累积权重
    # 假设车辆发布了10次交易，提高一个0.1个比例，就替换其中的一个为lazy
    # 需要模拟确定其前置交易实时累积声誉
    #
    # 0.0 = 2
    # 0.1 = 4
    # 0.2 = 8
    # 0.3 = 16
    # 0.4 = 30
    # 0.5 = 46
    '''
    #              0, 1, 2,  3,  4   5,  6,  7,  8,  9, 10
    bad_rs_ca   = [2, 6, 8, 11, 15, 19, 22, 26, 38, 46, 55]
    bad_mcmc_ca = [2, 6, 9, 13, 18, 24, 28, 39, 47, 56, 66]
    bad_cw_ca   = [2, 6, 8, 17, 24, 30, 37, 45, 52, 60, 67]
    _trans_gama = []  # 某个车辆发布的所有交易集合
    _successors_gama = rec_dd()  # 某车辆发布过的交易的前置的集合
    #  trans_id ----
    #           ---- trans_id ---- 实时权重
    #           ---- trans_id ---- 实时权重
    # _ca_gama = []  # 某个车辆在发布某个交易的时候的其前置交易的累积权重：
    _theta_gama = 6  # 某个车辆视角的阈值：这里确实不好下定义，理论上，参考上图3的结论，我们取6
    x = []
    m = 10
    y_mcmc = []
    y_rs = []
    y_cw = []
    consensus_metric = 0.5
    for i in range(0, m):
        x.append(round((i * 0.1), 1))
        _ = ((10 - i) * (2 - _theta_gama)) + bad_mcmc_ca[i]
        _ca_gama = func_exp(_)
        # consensus_metric = consensus_metric + _tmp
        y_mcmc.append(0.5 + round((0.5 * _ca_gama), 1))

        _ = ((10 - i) * (2 - _theta_gama)) + bad_rs_ca[i]
        _ca_gama = func_exp(_)
        # consensus_metric = consensus_metric + _tmp
        y_rs.append(0.5 + round((0.5 * _ca_gama), 1))

        _ = ((10 - i) * (2 - _theta_gama)) + bad_cw_ca[i]
        _ca_gama = func_exp(_)
        # consensus_metric = consensus_metric + _tmp
        y_cw.append(0.5 + round((0.5 * _ca_gama), 1))

    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1

    y_new_ticks = np.arange(0, m+10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']

    #  画板设置
    ax.plot(x, y_mcmc, color=color_select[0], marker='o', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("Proposed reputation with existing MCMC"))
    ax.plot(x, y_rs, color=color_select[1], marker='^', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("Proposed reputation with existing RS"))
    ax.plot(x, y_cw, color=color_select[2], marker='d', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("Proposed reputation with CW"))

    plt.rcParams['font.sans-serif'] = "Arial"
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.legend(loc='upper right', prop={'size': 10})

    # ax.set_xticks(x_new_ticks)
    # ax.set_yticks(y_new_ticks)
    ax.set_xlabel("Misbehavior Ratio for One Vehicle", fontdict={'size': 10})
    ax.set_ylabel("Reputation", fontdict={'size': 10})
    ax.set_ylim(ymin=-1)
    ax.set_ylim(ymax=1.1)
    ax.set_xlim(xmin=0)
    # ax.set_xlim(xmax=x_time)
    ax.grid(linestyle='-', alpha=0.3)

    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    fig.savefig('output/fourth01.pdf', dpi=300)
    plt.show()


def fourth_pic02():
    mu = [5, 15, 30]

    x = []
    m = 10
    y_ = []
    for _j in range(0, m):
        y_.append(0)

    for _i in range(0, 50):
        x = []
        for i in range(0, m):
            _ratio = round((i * 0.1), 1)
            if len(x) < 10:
                x.append(_ratio)
            num_update = st.poisson.rvs(mu=30, size=1, random_state=None)
            bad = int(num_update * _ratio)
            good = num_update[0] - bad
            f_good = func_x3(good)
            f_bad = func_x3(bad)
            if not num_update:
                print("error")
                continue
            _theta01 = f_good / (f_bad + f_good)
            _theta02 = f_bad / (f_bad + f_good)
            _sharing_metric = ((_theta01 * f_good) - (_theta02 * f_bad)) / (f_good + f_bad)
            y_[i] += (round(_sharing_metric, 1))

    for i in range(0, m):
        y_[i] = round((y_[i]*0.02), 1)

    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1

    y_new_ticks = np.arange(0, m+10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']

    #  画板设置
    ax.plot(x, y_, color=color_select[0], marker='o', markerfacecolor='none', linewidth=new_line_width,
            linestyle="dashed", label="{}".format("Sharing Metric with mu=5"))
    # ax.plot(x, y_[mu[1]], color=color_select[1], marker='^', markerfacecolor='none', linewidth=new_line_width,
    #         linestyle="dashed", label="{}".format("Sharing Metric with mu=15"))
    # ax.plot(x, y_[mu[2]], color=color_select[2], marker='d', markerfacecolor='none', linewidth=new_line_width,
    #         linestyle="dashed", label="{}".format("Sharing Metric with mu=30"))

    plt.rcParams['font.sans-serif'] = "Arial"
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.legend(loc='upper right', prop={'size': 10})

    # ax.set_xticks(x_new_ticks)
    # ax.set_yticks(y_new_ticks)
    ax.set_xlabel("Bad Rating Ratio for One Vehicle", fontdict={'size': 10})
    ax.set_ylabel("Metric Value", fontdict={'size': 10})
    ax.set_ylim(ymin=-1)
    ax.set_ylim(ymax=1.1)
    ax.set_xlim(xmin=0)
    # ax.set_xlim(xmax=x_time)
    ax.grid(linestyle='-', alpha=0.3)

    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    fig.savefig('output/fourth01.pdf', dpi=300)
    plt.show()


def fourth_pic():
    _zone_num, _all_vehicle_num = print_one_day(14, 14)
    #  可以是事件发生的泊松
    mu = [15, 17, 19, 21]
    ratings = [-0.6, 0.6, 0.7, 0.8, 0.9]
    tau_1 = 0.5
    tau_2 = 0.5

    x_time = range(0, 125)

    #  发布交易的结构
    dict_issued = rec_dd()
    dict_event = rec_dd()
    #  车还是用1-最大车辆来表示
    _all_vehicle_num = 600
    for i in range(0, _all_vehicle_num):
        #  交易用32位十六进制的uuid表示
        node_id = uuid.uuid1().hex
        dict_issued[node_id] = 0
        dict_event[node_id] = []

    target_vehicle = np.random.choice(list(dict_issued.keys()), 1)
    #  事件发生的数量
    reputation = rec_dd()

    for _mu in mu:
        reputation[_mu] = []
        for i in x_time:
            reputation[_mu].append(0)
        for j in range(0, 5):
            for _id in dict_issued.keys():
                dict_issued[_id] = 0
                dict_event[_id] = []
            print("Start Round {}".format(j))
            for i in x_time:
                rating_sum = 0
                #  本轮新增交易
                num_update = st.poisson.rvs(mu=_mu, size=1, random_state=None)
                #  为交易分配具体的节点
                list_issue_vehicle = random.sample(dict_issued.keys(), num_update[0])
                for _j in list_issue_vehicle:
                    dict_issued[_j] += 1
                #  为每一个交易添加事件
                for _i in range(0, num_update[0]):
                    #  产生事件中参与的节点数量
                    num_event_vehicle = np.random.randint(3, 10, 1)
                    #  选择具体的参与节点
                    list_event_vehicle = random.sample(list(dict_issued.keys()), num_event_vehicle[0])
                    for __i in list_event_vehicle:
                        rating = np.random.choice(ratings, 1)
                        #  产生评分
                        dict_event[__i].append(rating)
                for __j in dict_event[target_vehicle[0]]:
                    rating_sum += __j[0]
                reputation[_mu][i] += tau_1*dict_issued[target_vehicle[0]] + tau_2*rating_sum

    for _mu in mu:
        for __i in x_time:
            reputation[_mu][__i] = round(0.2 * reputation[_mu][__i])

    _all_max_y = max(reputation[mu[-1]])
    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1

    y_new_ticks = np.arange(0, _all_max_y+10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']
    _j = 0
    for _mu in mu:
        ax.plot(x_time, reputation[_mu], color=color_select[_j], linewidth=new_line_width,
                linestyle="dashed", label="mu={}".format(_mu))
        _j += 1

    #  画板设置
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
    # plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(int(_all_max_y/4)))
    plt.legend(loc='upper right', prop={'size': 8})

    # ax.set_xticks(x_new_ticks)
    # ax.set_yticks(y_new_ticks)
    ax.set_xlabel("Time", fontdict={'size': 10})
    ax.set_ylabel("Reputation", fontdict={'size': 10})
    ax.set_ylim(ymin=0)
    # ax.set_ylim(ymax=_all_max_y)
    ax.set_xlim(xmin=0)
    # ax.set_xlim(xmax=x_time)
    ax.grid(linestyle='-.')

    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    # fig.savefig('output/(5)ratio.pdf', dpi=300)
    plt.show()


if __name__ == '__main__':
    fourth_pic()
