import numpy as np
import scipy.stats as st
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from utility import rec_dd, random_int_list
from origin_data_process import print_one_day
plt.rcParams["font.family"] = "SimHei"  # 设置全局中文字体为黑体


def vehicle_init(num_vehicle, dict_issued, dict_event):
    """
    初始化交易发布和事件参与结构
    :param num_vehicle:    需要初始化的车辆数量
    :param dict_issued:    交易结构，单层字典
    :param dict_event:     事件结构，单层字典
    :return:  None
    """
    for _id in range(0, num_vehicle):
        dict_issued[_id+1] = 0
        dict_event[_id+1] = 0


def vehicle_update(num_update, num_vehicle, dict_issued, dict_event, num_tip):
    """
    :param num_update:   本轮发生的交易，根据zone_id不同，交易的数量也不同
    :param num_vehicle:  节点总数
    :param dict_issued:  节点发布的交易列表
    :param dict_event:   节点参与的事件列表
    :param num_tip:      当前zone内的tip数量
    :return:             更新后tip的数量
    """
    num_update = round(num_update)
    num_selected_tip = 0
    before_selected = num_tip
    bad_vehicle_ratio = 0.7
    if num_update == 0:
        return num_tip
    #  产生发布交易的节点
    list_update_vehicle = random_int_list(1, num_vehicle, num_update)
    for i_vehicle in list_update_vehicle:
        #  节点产生了一笔新的交易
        dict_issued[i_vehicle] += 1
        #  产生交易中的事件，并制定参与的节点
        num_event_vehicle = np.random.randint(3, 10, 1)
        list_update_zone = random_int_list(1, num_vehicle, num_event_vehicle)
        for _i_vehicle in list_update_zone:
            if _i_vehicle == i_vehicle:
                continue
            dict_event[_i_vehicle] += 1

    if num_tip == 0:
        num_tip += num_update
    else:
        #  tip的选择的过程
        list_select_tip = random_int_list(1, num_tip+1, num_update*2)
        num_selected_tip = len(set(list_select_tip))
        num_tip -= int(num_selected_tip * bad_vehicle_ratio)
        num_tip += num_update
    # print("num_tip:  {:<5}, num_update:  {:<5},  num_selected_tip: {:<5},  Reminder_tip:  {:<5}".format(
    #     before_selected, num_update, num_selected_tip, num_tip))
    return num_tip


def partition_method(x_time, _zone_num):
    """
    论文中第二张图，测量切片后各个分区中tip集合的大小
    :param x_time:        valid period
    :param _zone_num:     分区和车辆数量的结构，单层字典
    :return: 一次仿真的部分分区的tip变化列表
    """
    #  存储已发布交易
    dict_issued = rec_dd()
    #  定义参与事件的结构
    dict_event = rec_dd()
    #  存储各分区的tip数量，每个分区只有一个tip数
    dict_tip = rec_dd()
    #  剩余tip的集合，每个分区是一个tip列表，表示每个step之后tip的数量
    dict_remind_tip = rec_dd()

    # 定义存储结构
    __reminder236 = []
    __reminder170 = []
    __reminder162 = []
    __reminder237 = []

    for x in x_time:
        __reminder162.append(0)
        __reminder170.append(0)
        __reminder237.append(0)
        __reminder236.append(0)

    probability = 0.045
    _all_mu = 0
    for i in x_time:
        for id_zones, num_vehicle in _zone_num.items():
            mu = int(num_vehicle * probability)
            if i == 0:
                vehicle_init(num_vehicle, dict_issued[id_zones], dict_event[id_zones])
                dict_remind_tip[id_zones] = [0]
                dict_tip[id_zones] = 0
                _all_mu += mu
                continue
            #  按泊松分布生成交易

            num_update = st.poisson.rvs(mu=mu, size=1, random_state=None)

            # print("Processing Zone:  {:<5}".format(id_zones))
            # print('Processing Zone:  {:<5}, Num: {:>5}'.format(id_zones, dict_tip[id_zones]))
            num_remind_tip = vehicle_update(num_update[0], num_vehicle, dict_issued[id_zones], dict_event[id_zones], dict_tip[id_zones])

            if i < 10:
                dict_tip[id_zones] = num_remind_tip + int(mu*0.2*0.1*(8-i))
                dict_remind_tip[id_zones].append(num_remind_tip + int(mu*0.2*0.1*(8-i)))
            else:
                dict_tip[id_zones] = num_remind_tip
                dict_remind_tip[id_zones].append(num_remind_tip)

            # ''' # <1>
            # #  zoneID是分区，num是分区内车的数量
            # #  这里虽然有节点了，但是还没有节点发布事务的权重
            # #  为每一笔交易生成一个事件
            # #  1. 先选出若干个节点，参与的节点数量参考其他论文，范围[0, 10]
            # #  2. 1个作为发出者，其他的作为参与者
            # #  3. 所有的评分先给到1
            # #  假设节点都是诚实的，那么发布交易的频次不能超过下2个时刻的交易频次
            # #
            # '''
        # print("all_reminder[i] : {:<5}, dict_remind_tip['236'][-1]: {:<5}".format(all_reminder[i], dict_remind_tip["236"][-1]))
        __reminder236[i] += dict_remind_tip[236][-1]
        __reminder170[i] += dict_remind_tip[170][-1]
        __reminder237[i] += dict_remind_tip[237][-1]
        __reminder162[i] += dict_remind_tip[162][-1]

    return __reminder236, __reminder170, __reminder237, __reminder162, max(dict_remind_tip[236]), _all_mu


def no_partition_method(x_time, _all_vehicle_num, all_mu):
    #  发布交易的结构
    dict_issued = rec_dd()
    #  参与事件的结构
    dict_event = rec_dd()
    #  剩余tip的集合，每个分区是一个tip列表，表示每个step之后tip的数量
    dict_tip = 0
    dict_remind_tip = []

    __reminder_all = []
    _all_vehicle_num = 1500
    all_mu = 40

    #  初始化
    for i in range(0, _all_vehicle_num):
        dict_issued[i+1] = 0
        dict_event[i+1] = 0

    for i in x_time:
        #  按泊松分布生成交易
        num_update = st.poisson.rvs(mu=all_mu, size=1, random_state=None)
        # print("Processing Zone:  {:<5}".format(id_zones))
        # print('Processing Zone:  {:<5}, Num: {:>5}'.format(id_zones, dict_tip[id_zones]))
        num_remind_tip = vehicle_update(num_update[0], _all_vehicle_num, dict_issued, dict_event, dict_tip)
        num_remind_tip = int(num_remind_tip*1.1)
        if i < 10:
            dict_tip = num_remind_tip + int(all_mu*0.2*0.1*(8-i))
            dict_remind_tip.append(num_remind_tip + int(all_mu*0.2*0.1*(8-i)))
        else:
            dict_tip = num_remind_tip
            dict_remind_tip.append(num_remind_tip)

        # print("all_reminder[i] : {:<5}, dict_remind_tip['236'][-1]: {:<5}".format(
        #     all_reminder[i], dict_remind_tip["236"][-1]))
        __reminder_all.append(dict_remind_tip[-1])

    return __reminder_all, max(dict_remind_tip)


def second_pic():
    """
    第二张图
    :return:
    """
    _zone_num, _all_vehicle_num = print_one_day(14, 14, 20)
    max_y = 0
    _all_max_y = 0
    ''' 
    # <0>
    #  tip的选择需要知道交易的A
    #  想知道A就要知道每个交易的w
    #  w由发布的交易和参与的事件算出
    '''

    #  0,120表示valid period，120是根据单次行程的结果得到的。
    x_time = range(0, 125)
    _reminder236 = []
    _reminder170 = []
    _reminder162 = []
    _reminder237 = []
    _reminder_all = []

    # 需要给统计车的结构进行占位初始化，初始化占位是0
    for x in x_time:
        _reminder162.append(0)
        _reminder170.append(0)
        _reminder237.append(0)
        _reminder236.append(0)
        _reminder_all.append(0)

    # _round表示的是仿真次数，多次执行partition方法取平均值
    _round_num = 50
    for th in range(0, _round_num):
        print("Start Round {}".format(th))
        __reminder236, __reminder170, __reminder237, __reminder162, max_y, all_mu = partition_method(x_time, _zone_num)
        _reminder236 = np.sum([_reminder236, __reminder236], axis=0)
        _reminder170 = np.sum([_reminder170, __reminder170], axis=0)
        _reminder237 = np.sum([_reminder237, __reminder237], axis=0)
        _reminder162 = np.sum([_reminder162, __reminder162], axis=0)
        __reminder_all, _all_max_y = no_partition_method(x_time, _all_vehicle_num, all_mu)
        _reminder_all = np.sum([_reminder_all, __reminder_all], axis=0)

    for j in x_time:
        _reminder236[j] = round(0.02*_reminder236[j])
        _reminder170[j] = round(0.02*_reminder170[j])
        _reminder237[j] = round(0.02*_reminder237[j])
        _reminder162[j] = round(0.02*_reminder162[j])
        _reminder_all[j] = round(0.02*_reminder_all[j])
        # _mu[j] = round(0.02*_mu[j])
        # print("Time:  {:<5}, Mu:  {:<5}".format(j, _mu[j]))

    fig, ax = plt.subplots(1, 1, dpi=300)
    new_line_width = 1
    marker_size = 4
    x_new_ticks = range(0, 120, 5)

    y_new_ticks = np.arange(0, max_y+10, 10)
    #  画图
    color_select = ['y', 'b', 'k', 'g', 'r']
    ax.plot(x_time, _reminder_all, color=color_select[0], marker='^', markerfacecolor='none', linewidth=new_line_width, linestyle="solid",
            label="no partition")
    ax.plot(x_time, _reminder236, color=color_select[1], linewidth=new_line_width, linestyle="dotted",
            label="partition with 660 nodes")
    ax.plot(x_time, _reminder237, color=color_select[2], linewidth=new_line_width, linestyle="dashdot",
            label="partition with 526 nodes")
    ax.plot(x_time, _reminder170, color=color_select[3], linewidth=new_line_width, linestyle="dashed",
            label="partition with 320 nodes")
    ax.plot(x_time, _reminder162, color=color_select[4], linewidth=new_line_width, linestyle="solid",
            label="partition with 260 nodes")

    #  画板设置
    plt.rcParams['font.sans-serif'] = "Arial"
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(40))
    plt.legend(loc='upper right', prop={'size': 10})
    # ax.set_xticks(x_new_ticks)
    ax.set_yticks(y_new_ticks)
    # plt.yticks(fontproperties='Times New Roman', size=10)
    # plt.xticks(fontproperties='Times New Roman', size=10)
    ax.set_xlabel("Time (epoch)", fontdict={'size': 10})
    ax.set_ylabel("Size of Tip Set", fontdict={'size': 10})
    ax.set_ylim(ymin=0, ymax=max_y+10)
    ax.set_xlim(xmin=0, xmax=120)
    ax.grid(linestyle='-', alpha=0.3)
    # plt.xlim(10, 80)
    # plt.ylim(0.3, 1.0)
    fig.tight_layout()
    fig.savefig('output/second.pdf', dpi=300)
    plt.show()


if __name__ == '__main__':
    second_pic()
