import random

def bluff_spot():
    player1_card = 0  # プレイヤー1のカード（ブラフ：Q）
    player2_card = 1  # プレイヤー2のカード（ブラフキャッチャー：K）
    pot = 2  # 各プレイヤーからの1のアンティ
    bluff_size = 1  # ブラフのサイズ
    # ブラフが成功する確率のブレイクイーブン（損益分岐点）
    breakeven_bluff_success_freq = bluff_size / (bluff_size + pot)  # 1/3
    # ブラフキャッチの確率（損益分岐点での期待値0のブラフ）
    bluffcatch_freq = 1 - breakeven_bluff_success_freq  # 0 ev bluff
    # ここで、ブラフキャッチの確率を調整することもできる
    # bluffcatch_freq = 1 - .25  # アンダーフォールド
    # bluffcatch_freq = 1 - .40  # オーバーフォールド
    # 確率に基づいて結果を決定
    if random.random() < bluffcatch_freq:
        return -bluff_size  # プレイヤー2がコールし、プレイヤー1が負ける
    else:
        return pot  # プレイヤー2がフォールドし、プレイヤー1がポットを獲得

def sim_bluff_spot():
    total = 0  # アンティは含めない！ブラフの局面だけを独立して考える
    iterations = 1000  # シミュレーションの回数
    for i in range(iterations):
        total += bluff_spot()  # ブラフ局面をシミュレーション
        print('{0:0.2f}'.format(total / iterations))  # 平均値を出力

def bluffcatch_spot():
    player1_card = 0  # プレイヤー1のカード（ブラフ：Q）
    player2_card = 1  # プレイヤー2のカード（ブラフキャッチャー：K）
    pot = 2  # 各プレイヤーからの1のアンティ
    bet_size = 1  # ベットのサイズ
    # ブラフの確率
    bluff_freq = bet_size / (2 * bet_size + pot)  # .25
    # AKQゲームでは、3枚のAと3枚のQが配られた場合、Qの1/3をブラフ
    # ブラフの頻度を調整することもできる
    # bluff_freq = .3  # オーバーブラフ
    # bluff_freq = .2  # アンダーブラフ
    # 確率に基づいて結果を決定
    if random.random() < bluff_freq:
        return pot + bet_size  # プレイヤー2がコールし、ポット + ブラフを獲得
    else:
        return -bet_size  # プレイヤー2がコールし、負ける

def sim_bluffcatch_spot():
    total = 0  # アンティは含めない！ブラフの局面だけを独立して考える
    iterations = 1000  # シミュレーションの回数
    for i in range(iterations):
        total += bluffcatch_spot()  # ブラフキャッチ局面をシミュレーション
        print('{0:0.2f}'.format(total / iterations))  # 平均値を出力

def polarized_spot():
    # プレイヤー1のカードをランダムに決定
    player1_card = 2 if random.random() > 0.5 else 0  # 値のある手かブラフか
    player2_card = 1  # プレイヤー2は常にブラフキャッチャー
    ante = 1  # 各プレイヤーのアンティ
    pot = 2 * ante  # ポットのサイズ
    bet_size = 1  # ベットのサイズ

    # 最良の結果は、常にブラフを行い、相手が常にフォールドすること
    bluff_freq = 1 / 3  # ブラフの頻度（全体の範囲の25%がブラフであるべき）
    bluffcatch_freq = 1 - bluff_freq  # ブラフキャッチの頻度

    # プレイヤー1が値のある手を持っている場合
    if player1_card == 2:  # 値のある手
        if random.random() < bluffcatch_freq:  # 相手がコールして負ける場合
            return pot + bet_size - ante  # ポット + ベット - アンティを獲得
        else:  # 相手がフォールドする場合
            return pot - ante  # ポット - アンティを獲得
    else:  # ブラフをしている場合
        if random.random() < bluff_freq:  # ブラフを選択する場合
            if random.random() < bluffcatch_freq:  # 相手がコールして負ける場合
                return -bet_size - ante  # ベットとアンティを失う
            else:  # 相手がフォールドする場合
                return pot - ante  # ポット - アンティを獲得
        else:  # 諦めて常に負ける場合
            return -ante  # アンティを失う

def sim_polarized_spot():
    total = 0  # アンティは含めない！ブラフの局面だけを独立して考える
    iterations = 1000  # シミュレーションの回数
    for i in range(iterations):
        total += polarized_spot()  # ポラライズされた局面をシミュレーション
        print('{0:.2f}'.format(total / iterations))  # 平均値を出力

if __name__ == "__main__":
    # シミュレーションを実行
    # sim_bluff_spot()
    # sim_bluffcatch_spot()
    sim_polarized_spot()  # ポラライズされた局面をシミュレーション
