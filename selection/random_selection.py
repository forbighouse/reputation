import timeit
import numpy as np

from my_ledger import DAGLedger


def find_tip_all(ledger_graph, trans_id):
    """
    这个tip选择是根据输入的trans_id, 找到该交易的所有tip
    :param ledger_graph: 账本
    :param trans_id: 搜索其实位置
    :return: 找到的所有的tip的列表
    """
    _successors_iter = ledger_graph.get_successors(trans_id)
    if not _successors_iter:
        return trans_id
    else:
        _trans_id = np.random.choice(_successors_iter)
        _tip = find_tip_all(ledger_graph, _trans_id)
        return _tip

    # _sum = 0
    # _successors_list = []
    # for _ in _successors_iter:
    #     _sum += 1
    #     _successors_list += find_tip_all(ledger_graph, _)
    # if not _sum:  # 表示此时输入的交易就是一个tip，那么直接返回即可
    #     _successors_list.append(trans_id)
    # # print("后置集合： " + str(len(_successors_list)))
    # return _successors_list


def tip_selection_random(ledger_graph, time_epoch):
    """
    tip选择，完全随机
    :param time_epoch:
    :param ledger_graph:
    :return:
    """
    #  如果不是DAG结构就返回
    if not isinstance(ledger_graph, DAGLedger):
        print(type(ledger_graph).__name__)
        raise KeyError("tip选择算法加载的账本格式错误")
    m = 2
    two_tips = []
    for i in range(0, m):
        #  随机从账本中找一个交易结点
        all_trans = ledger_graph.get_valid_transaction_id(time_epoch)

        _random_trans = np.random.choice(list(all_trans))

        # t0 = timeit.default_timer()
        _tip = find_tip_all(ledger_graph, _random_trans)
        two_tips.append(_tip)
        # elapsed = timeit.default_timer() - t0

        # print('[%0.8fs]' % elapsed)

        #  这一步体现完全随机

    return two_tips
