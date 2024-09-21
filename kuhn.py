import numpy as np
import random

class Node:
    def __init__(self, infoset, num_actions):
        self.infoset_id = infoset  # 情報セットの識別子
        self.regret_sum = np.zeros(num_actions)  # 各アクションの後悔の合計
        self.strategy = np.zeros(num_actions)  # 現在の戦略
        self.strategy_sum = np.zeros(num_actions)  # 戦略の合計
        self.num_actions = num_actions  # アクションの数
        self.visited_count = 0  # このノードが訪れた回数
        self.util_sum = 0  # 合計ユーティリティ

    def get_strategy(self):
        normalizing_sum = 0
        # 後悔に基づいて戦略を計算
        for a in range(self.num_actions):
            if self.regret_sum[a] > 0:
                self.strategy[a] = self.regret_sum[a]
            else:
                self.strategy[a] = 0
            normalizing_sum += self.strategy[a]

        # 戦略を正規化
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1.0 / self.num_actions  # 等確率にする

        return self.strategy

    def get_average_strategy(self):
        avg_strategy = np.zeros(self.num_actions)  # 平均戦略を初期化
        normalizing_sum = 0

        # 戦略の合計を計算
        for a in range(self.num_actions):
            normalizing_sum += self.strategy_sum[a]
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum  # 正規化
            else:
                avg_strategy[a] = 1.0 / self.num_actions  # 等確率にする

        return avg_strategy

    def pretty_print(self):
        strat_str = list(
            map(lambda s: "{0:.4f}".format(s), self.get_average_strategy())
        )  # 平均戦略を文字列にフォーマット
        print(
            "history:{0}, avgStrat:{1}, count:{2}, util_sum:{3:.0f}, util:{4:.4f}".format(
                self.infoset_id,  # 情報セットの識別子
                strat_str,  # 平均戦略
                self.visited_count,  # 訪問回数
                self.util_sum,  # 合計ユーティリティ
                self.util_sum / self.visited_count,  # 平均ユーティリティ
            )
        )


class KuhnCFR:
    def __init__(self, iterations, decksize):
        self.nbets = 2  # ベットの数（ハードコーディング）
        self.iterations = iterations  # 繰り返し回数
        self.decksize = decksize  # デッキのサイズ
        self.cards = np.arange(decksize)  # 使用するカードのリスト
        self.bet_options = 2  # ベットオプションの数（ハードコーディング）
        self.nodes = {}  # 情報セットに関連するノードの辞書

    def cfr_iterations_external(self):
        util = np.zeros(2)  # プレイヤーごとのユーティリティ
        for t in range(1, self.iterations + 1):
            for i in range(2):
                random.shuffle(self.cards)  # カードをシャッフル
                util[i] += self.external_cfr(self.cards[:2], [], 2, 0, i, t)  # CFRを実行
        print("Average game value: {}".format(util[0] / (self.iterations)))  # 平均ゲーム値を表示
        for i in sorted(self.nodes):
            self.nodes[i].pretty_print()  # 各ノードの情報を表示

    def external_cfr(self, cards, history, pot, nodes_touched, traversing_player, t):
        plays = len(history)  # プレイの数を取得
        acting_player = plays % 2  # 現在のアクションを取るプレイヤー
        opponent_player = 1 - acting_player  # 対戦相手

        # 終了条件のチェック
        if plays >= 2:
            # ベットフォールドの場合
            if history[-1] == 0 and history[-2] == 1:  # bet fold
                if acting_player == traversing_player:
                    return 1  # プレイヤーが勝利
                else:
                    return -1  # プレイヤーが敗北
            # ショーダウンの場合
            if (history[-1] == 0 and history[-2] == 0) or (
                history[-1] == 1 and history[-2] == 1
            ):  # check check or bet call
                if acting_player == traversing_player:
                    if cards[acting_player] > cards[opponent_player]:
                        return pot / 2  # 勝利した場合のポットの半分を返す
                    else:
                        return -pot / 2  # 敗北した場合のポットの半分を返す
                else:
                    if cards[acting_player] > cards[opponent_player]:
                        return -pot / 2  # 敗北した場合のポットの半分を返す
                    else:
                        return pot / 2  # 勝利した場合のポットの半分を返す

        # 情報セットの作成
        infoset = str(cards[acting_player]) + str(history)
        if infoset not in self.nodes:
            self.nodes[infoset] = Node(infoset, self.bet_options)  # ノードの初期化

        nodes_touched += 1  # ノードのカウントを増加

        if acting_player == traversing_player:
            util = np.zeros(self.bet_options)  # アクション数に基づくユーティリティ
            node_util = 0  # ノードのユーティリティ
            strategy = self.nodes[infoset].get_strategy()  # 現在の戦略を取得
            for a in range(self.bet_options):
                next_history = history + [a]  # 次の履歴を生成
                util[a] = self.external_cfr(
                    cards, next_history, pot + a, nodes_touched, traversing_player, t
                )  # 次のアクションをシミュレーション
                node_util += strategy[a] * util[a]  # ノードユーティリティを計算

            # 後悔の更新
            for a in range(self.bet_options):
                regret = util[a] - node_util  # 後悔を計算
                self.nodes[infoset].regret_sum[a] += regret  # 後悔の合計を更新
            self.nodes[infoset].util_sum += node_util  # ユーティリティの合計を更新
            self.nodes[infoset].visited_count += 1  # 訪問回数を更新
            return node_util  # ノードユーティリティを返す

        else:  # acting_player != traversing_player
            strategy = self.nodes[infoset].get_strategy()  # 戦略を取得
            util = 0
            # 戦略に基づいて次のアクションを決定
            if random.random() < strategy[0]:
                next_history = history + [0]  # アクション0を選択
            else:
                next_history = history + [1]  # アクション1を選択
                pot += 1  # ポットを増加
            util = self.external_cfr(
                cards, next_history, pot, nodes_touched, traversing_player, t
            )  # 次のアクションをシミュレーション
            for a in range(self.bet_options):
                self.nodes[infoset].strategy_sum[a] += strategy[a]  # 戦略の合計を更新
            return util  # ユーティリティを返す

if __name__ == "__main__":
    # シミュレーションの初期化
    # k = KuhnCFR(2000000, 10)  # 2百万回の繰り返しでデッキサイズ10
    k = KuhnCFR(10000, 3)  # 1万回の繰り返しでデッキサイズ3
    k.cfr_iterations_external()  # CFRを実行
