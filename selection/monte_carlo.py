import time, timeit
import numpy as np
from my_ledger import DAGLedger


def find_tip_mc(ledger_graph, _trans_id):
    """
    v1版本的找tip扫描算法是根据蒙特卡洛来的，具体的alpha值封装在账本里面
    :param ledger_graph:
    :param _trans_id:
    :return:
    """
    _random_trans_rear = ledger_graph.get_successors(_trans_id)
    # 1 如果没有后置，它自己就是tip，直接返回
    if not _random_trans_rear:
        return _trans_id
    else:
        _max_trans_pro = -1
        _may_be_trans = 0
        a = 3  # 少循环几次可以显著提高效率
        # 2 循环是为了防止一次找不到合适的后置就多找几次
        # print("_trans_id", _trans_id, "    _rear: ", _random_trans_rear)
        for j in _random_trans_rear:
            trans_pro, _ = ledger_graph.get_tip_transition_pro(_trans_id, j)
            #  根据概率沿着边缘继续迭代找, 迭代找的结果是总会遇到没有后置的时候，也就是情况1,
            if round(np.random.uniform(0, 1), 1) < trans_pro:
                _x = find_tip_mc(ledger_graph, j)
                return _x
            if trans_pro > _max_trans_pro:
                _max_trans_pro = trans_pro
                _may_be_trans = j
        #  随便选完了还是要继续找，也可能出现找不到的情况
        _y = find_tip_mc(ledger_graph, _may_be_trans)
        return _y


def tip_selection_mc(ledger_graph, time_epoch):
    """
    tip选择算法，采用蒙特卡洛随机游走
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
        t0 = timeit.default_timer()
        _tip = find_tip_mc(ledger_graph, _random_trans)
        elapsed = timeit.default_timer() - t0
        print('[%0.8fs]' % elapsed)

        two_tips.append(_tip)
    return two_tips
