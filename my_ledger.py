import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from utility import rec_dd


class DAGLedger:
    def __init__(self, func_tip_selection):
        self._ledger_state = nx.DiGraph()  # 账本的状态：是一个DAG，节点是交易，边是认证关系
        self._node_reputation_consensus_state = rec_dd()  # 节点声誉的共识测度：key是节点，value是目前的最新的声誉
        self._node_issued_transactions = rec_dd()  # 节点发布过的交易记录：key是节点，value是所有发布过的交易的列表
        self._transaction_state = rec_dd()  # 交易状态：key是交易，value表示该交易发布和被认证的time_epoch,"start":-1, "end":-1
        self._transaction_state_for_select = rec_dd()  # 交易状态：key是交易，value表示该交易发布和被认证的time_epoch,"start":-1, "end":-1
        self._lazy_transaction_state = []  # 所有lazy交易
        self._normal_transaction_state = []  # 所有lazy交易
        self._alpha = 0.1  # 沿着边找tip的时候的转移概率
        self._trans_id = 0  # 当前的内部交易号，初始值为0
        self._bad_probability = 0.3  # tip选择算法
        self._anchor_key = [3, 5]  # 作为所有lazy的选择，放大lazy的效果
        self._lazy_tag = -2  # 删除anchor_key的标记位

        self.tip_select_algorithm = func_tip_selection  # 账本使用的tip选择算法
        print(func_tip_selection.__name__)

    def add_new_transaction(self, time_epoch, update_transaction):
        """
        更新账本
        :param time_epoch: 代表本轮时间
        :param update_transaction: 待更新的交易，里面实际是发布交易的节点，是一个列表，具体交易在本函数内生成
        :return:
        """
        #  账本初始化
        self._transaction_state_for_select[time_epoch] = []
        if not self._transaction_state.keys():
            for j, _node in enumerate(update_transaction):
                if _node not in self._node_issued_transactions.keys():
                    self._add_new_node(_node)
                self._ledger_state.add_node(self._trans_id, pos=(time_epoch, j), desc=_node)
                self._update_new_transaction(_node, self._trans_id, time_epoch)
                self._transaction_state_for_select[time_epoch].append(self._trans_id)
                self._trans_id += 1
            return

        if self._lazy_tag == 0:
            [self._transaction_state.pop(k) for k in self._anchor_key]
            self._lazy_tag += 1

        #  先每个新交易选出来的tip存起来，等下一起加到账本里
        pair_tip_node = self._tip_selecting(time_epoch, update_transaction)

        for j, pairs in enumerate(pair_tip_node):
            __tips = pairs[0]
            __trans_id = pairs[1]
            __node_id = pairs[2]
            _x = rec_dd()
            _y = rec_dd()
            if __tips == self._anchor_key:
                _x["time"] = time_epoch
                _x["trans_id"] = __trans_id
                _x["node_id"] = __node_id
                self._lazy_transaction_state.append(_x)
            else:
                self._normal_transaction_state.append(__trans_id)
            for _tip in __tips:
                #  账本中添加新增的交易节点
                self._ledger_state.add_node(__trans_id, pos=(time_epoch, j), desc=__node_id)
                self._transaction_state_for_select[time_epoch].append(__trans_id)
                #  与选择出来的tip连边
                self._ledger_state.add_edge(_tip, __trans_id)
                #  在审计结构中，添加tip的被认证时间
                self._update_tip(_tip, time_epoch)

            #  在审计结构中，添加新增的交易
            self._update_new_transaction(__node_id, __trans_id, time_epoch)

        return

    def draw_ledger(self):
        """
        将账本画图打印出来
        :return:
        """
        fig, ax = plt.subplots(1, 1, dpi=300)
        pos = nx.get_node_attributes(self._ledger_state, 'pos')  # 随机分布
        # cmap=plt.cm.Paired, # matplotlib 的调色板，可以搜搜，很多颜色呢吃
        # nx.draw(ledger, with_labels=True, node_size=200)
        nx.draw_networkx_nodes(self._ledger_state, pos=pos, label=True, node_size=150, alpha=0.7)  # 点的样式
        nx.draw_networkx_edges(self._ledger_state, pos=pos, width=0.3, alpha=0.2)  # 边的样式
        nx.draw_networkx_labels(self._ledger_state, pos, font_size=14)  # 节点的标签
        fig.tight_layout()
        plt.show()

    def get_tip_transition_pro(self, _front, _rear):
        _front_AC = self.get_accumulative_weight(_front)
        _rear_AC = self.get_accumulative_weight(_rear)
        _ = self._alpha * (_front_AC - _rear_AC)
        return round(np.exp(-_), 1), _front_AC - _rear_AC

    def get_accumulative_weight(self, _node):
        """
        获取账本中，某个节点的累积权重
        :param _node: 想要获取的结点
        :return: 权重计算结果
        """
        _list_all_successors = self._find_all_successors(_node)
        accumulative_weight = len(set(_list_all_successors))
        return accumulative_weight

    def get_valid_transaction_id(self, time_epoch):
        a = time_epoch - 30
        if a < 0:
            a = 0
        _list = []
        while a < time_epoch:
            _list += self._transaction_state_for_select[a]
            a += 1

        return _list

    def get_transaction_state(self, _node):
        return self._transaction_state[_node]

    def get_nodes(self):
        return self._ledger_state.nodes

    def get_lazy_info(self):
        return self._lazy_transaction_state

    def get_normal_info(self):
        return self._normal_transaction_state

    def get_transaction_info(self, _trans_id):
        """
        获取账本中，某个结点的信息
        :param _trans_id:
        :return: 返回的是存储在DAG中的全部信息
        """
        return self._ledger_state.nodes[_trans_id]

    def get_predecessors(self, _node):
        """
        获取结点前置
        :param _node: 想要获取的结点
        :return: 前置结点
        """
        return self._ledger_state.predecessors(_node)

    def get_successors(self, _node):
        """
        获取结点后置
        :param _node: 想要获取的结点
        :return: 后置结点
        """
        _ = []
        for i in self._ledger_state.successors(_node):
            _.append(i)
        _ = list(set(_))
        return _

    def _tip_selecting(self, time_epoch, update_transaction):
        pair_tip_node = []
        #  这一步只是在账本中加入新的节点
        for _node in update_transaction:
            #  判断每发起交易的节点是不是新来的
            if _node not in self._node_issued_transactions.keys():
                self._add_new_node(_node)

            _tips = []
            if time_epoch > 5:
                #  手动选择部分交易成为lazy
                if round(np.random.uniform(0, 1), 1) < self._bad_probability:
                    _tips = self._anchor_key
                else:
                    #  按正常流程选择，且去除掉重复
                    _tips = self.tip_select_algorithm(self, time_epoch)
                    _tips = list(set(_tips))
            else:
                #  在小于5轮时，所有交易都是正常的
                _tips = self.tip_select_algorithm(self, time_epoch)
                _tips = list(set(_tips))

            try:

                pair_tip_node.append((_tips, self._trans_id, _node))
                self._trans_id += 1
                if not _tips:
                    raise ValueError("选择的tip集合为空")
            except ValueError as e:
                print("异常错误： ", repr(e))
        return pair_tip_node

    def _add_new_node(self, node_id):
        self._node_issued_transactions[node_id] = []

    def _update_new_transaction(self, node_id, trans_id, time_epoch):
        self._transaction_state[trans_id]["start"] = time_epoch
        self._transaction_state[trans_id]["end"] = -1

        self._node_issued_transactions[node_id].append(trans_id)

    def _update_tip(self, trans_id, time_epoch):
        if trans_id == 3 or trans_id == 5:
            self._lazy_tag += 1
            return
        if self._transaction_state[trans_id]["end"] > 0:
            return
        self._transaction_state[trans_id]["end"] = time_epoch

    def _find_all_successors(self, _node):
        _number = []
        _select_successors = self._ledger_state.successors(_node)
        for _successor in _select_successors:
            #  _successor肯定是一个，所以先加一个
            _number.append(_successor)
            #  开始迭代，
            _number += self._find_all_successors(_successor)
        return _number



