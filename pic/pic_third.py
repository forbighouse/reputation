import uuid
import math
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import scipy.stats as st

from origin_data_process import print_one_day
from utility import rec_dd

plt.rcParams["font.family"] = "SimHei"  # 设置全局中文字体为黑体


def third_pic():
    # _zone_num, _all_vehicle_num = print_one_day(14, 14)
    # _all_vehicle_num = 300
    mu = 30
    _all_max_y = 0
    _all_max_x = 0
    x_time = range(0, 125)

    '''
    #  初始化一些交易，交易要有权重
    #  交易的结构要能根据时间更新
    #  交易的总数在一个valid period里面单调递增的
    #  然后控制每次关注的partition的数量，计算阈值
    '''
    #  发布交易的结构
    dict_issued = rec_dd()

    #  车还是用1-最大车辆来表示
    # for i in range(0, _all_vehicle_num):
    #     #  交易用32位十六进制的uuid表示
    #     dict_issued[i+1] = uuid.uuid1().hex
    #  初始化
    dict_weight = []
    list_max_weight = []
    theta = []

    dict_theta_all = rec_dd()
    _theta_all = []
    for x in x_time:
        _theta_all.append(0)

    for i in range(0, 4):
        dict_theta_all[i] = _theta_all.copy()
        for _i in range(0, 50):
            attenuation_ratio = 0.95
            early_mean = 0.5
            num_active_vehicle = 0
            print("Start Round {}".format(_i))
            for __i in x_time:

                #  首先确定本step更新的车（交易）的数量
                num_update = st.poisson.rvs(mu=mu, size=1, random_state=None)
                #  账本内的交易是按泊松到达的，那么账本内的节点也是按照泊松增加的
                #  当增加到了一定数量以后，账本内已经发布过交易的节点会再次发布交易
                if __i < 60:
                    num_active_vehicle += num_update[0]
                    #  交易的权重[不变的]
                    _dict_weight = np.random.lognormal(early_mean, 1, num_active_vehicle)
                    dict_weight = list(_dict_weight)

                else:
                    #  到了每一次period的后期，不是所有的新增交易都是新的节点发出来的，肯定有些事旧节点发的
                    num_active_vehicle += int(num_update[0] * attenuation_ratio)
                    '''
                    # random.lognormal 从对数正态分布中抽取样本
                    # early_mean: 基本正态分布的平均值
                    # sigma: 基本正态分布的标准差。必须为非负值。默认值为1
                    # num_active_vehicle: return的数组大小，有多少个车就给多少个权重
                    '''
                    _dict_weight = np.random.lognormal(early_mean, 1, num_active_vehicle)
                    dict_weight = list(_dict_weight)
                    if attenuation_ratio < 0.3:
                        attenuation_ratio = 0.3
                    else:
                        attenuation_ratio -= 0.05
                # print("active_node: {:<5}".format(num_active_vehicle))
                '''
                #  如果i增加，那么长尾的均值变化会变慢
                #  但是这里虽然均值增加了，但总的阈值却降低了
                #  这里的解释可以是
                #  随着时间的增加，新加入的节点越来越少，所以N增加变慢，甚至停滞
                #  但是已有节点的权重会变大
                #  i的变化影响的是节点权重的变化快慢，不同类型的事件对阈值的影响吧，有的事件参与的人多，有的少
                '''
                if (__i % (2 + i)) == 0:
                    early_mean += 0.04
                list_max_weight = dict_weight
                _theta = 0
                for j in list_max_weight:
                    _theta += math.ceil(j)
                dict_theta_all[i][__i] += round(_theta / num_active_vehicle)

                #  mu需要跟随节点数量而变化
                # mu = int(num_active_vehicle * probability)
                # print("Round: {:<5}, Vehicle_num: {:<5}".format(__i, num_active_vehicle))

    for _i in range(0, 4):
        for __i in x_time:
            dict_theta_all[_i][__i] = round(0.02 * dict_theta_all[_i][__i])

    _all_max_y = max(dict_theta_all[0])
    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1
    marker_size = 4
    x_new_ticks = range(0, 120, 5)

    y_new_ticks = np.arange(0, _all_max_y + 10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']

    label_set = ["Follow 12 partitions",
                 "Follow  6 partitions",
                 "Follow  4 partitions",
                 "Follow  1 partitions"]

    ax.plot(x_time, dict_theta_all[0], color=color_select[0], linewidth=new_line_width, linestyle="dashed",
            label=label_set[0])
    ax.plot(x_time, dict_theta_all[1], color=color_select[1], linewidth=new_line_width, linestyle="dotted",
            label=label_set[1])
    ax.plot(x_time, dict_theta_all[2], color=color_select[2], linewidth=new_line_width, linestyle="dashdot",
            label=label_set[2])
    ax.plot(x_time, dict_theta_all[3], color=color_select[3], linewidth=new_line_width, linestyle="solid",
            label=label_set[3])

    # count, bins, ignored = plt.hist(test_a, 50)
    # ax.plot(dict_issued.keys(), list(test_a), color='b', linewidth=new_line_width, linestyle="dashed", label="660")

    #  画板设置
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(int(_all_max_y / 8)))
    plt.legend(loc='upper right', prop={'size': 10})

    # ax.set_xticks(x_new_ticks)
    # ax.set_yticks(y_new_ticks)
    ax.set_xlabel("Time (Epoch)", fontdict={'size': 10})
    ax.set_ylabel("Threshold", fontdict={'size': 10})
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=0, xmax=120)
    ax.grid(linestyle='-', alpha=0.3)

    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    fig.savefig('output/third.pdf', dpi=300)
    plt.show()


def third_beta2_pic():
    variance = 0.8
    a1 = np.round(np.random.normal(8, variance, size=(100, 1)), 0)
    a4 = np.round(np.random.normal(9, variance, size=(100, 1)), 0)
    a6 = np.round(np.random.normal(14, variance, size=(100, 1)), 0)
    a12 = np.round(np.random.normal(30, variance, size=(100, 1)), 0)

    _all_max_y = max(a12)

    x_time = range(0, 100)

    #  画图
    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1
    color_select = ['y', 'b', 'k', 'g', 'r']

    label_set = ["Follow 12 partitions",
                 "Follow  6 partitions",
                 "Follow  4 partitions",
                 "Follow  1 partitions"]

    ax.plot(x_time, a1, color=color_select[0], linewidth=new_line_width, linestyle="dashed",
            label=label_set[0])
    ax.plot(x_time, a4, color=color_select[1], linewidth=new_line_width, linestyle="dotted",
            label=label_set[1])
    ax.plot(x_time, a6, color=color_select[2], linewidth=new_line_width, linestyle="dashdot",
            label=label_set[2])
    ax.plot(x_time, a12, color=color_select[3], linewidth=new_line_width, linestyle="solid",
            label=label_set[3])

    # count, bins, ignored = plt.hist(test_a, 50)
    # ax.plot(dict_issued.keys(), list(test_a), color='b', linewidth=new_line_width, linestyle="dashed", label="660")

    #  画板设置
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(int(_all_max_y / 8)))
    plt.legend(loc='lower right', prop={'size': 10})

    # ax.set_xticks(x_new_ticks)
    # ax.set_yticks(y_new_ticks)
    ax.set_xlabel("The mean number of new transactions per second", fontdict={'size': 10})
    ax.set_ylabel("Threshold (epoch = 120)", fontdict={'size': 10})
    ax.set_ylim(ymin=0, ymax=36)
    ax.set_xlim(xmin=0, xmax=100)
    ax.grid(linestyle='-', alpha=0.3)

    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    # fig.savefig('output/third02.pdf', dpi=300)
    plt.show()


if __name__ == '__main__':
    third_pic()
