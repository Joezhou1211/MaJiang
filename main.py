from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__, static_folder='src/static')


def dfs_melds(cards, path=[]):
    if not cards:
        return path

    unique_cards = sorted(set(cards))

    # 处理刻子
    for card in unique_cards:
        if cards.count(card) >= 3:
            new_cards = cards.copy()
            new_cards.remove(card)
            new_cards.remove(card)
            new_cards.remove(card)
            result = dfs_melds(new_cards, path + [(card, card, card)])
            if result is not None:
                return result

    # 处理顺子
    for i in range(len(unique_cards) - 2):
        if unique_cards[i] + 1 in unique_cards and unique_cards[i] + 2 in unique_cards:
            seq_start = unique_cards[i]
            if cards.count(seq_start) > 0 and cards.count(seq_start + 1) > 0 and cards.count(seq_start + 2) > 0:
                new_cards = cards.copy()
                new_cards.remove(seq_start)
                new_cards.remove(seq_start + 1)
                new_cards.remove(seq_start + 2)
                result = dfs_melds(new_cards, path + [(seq_start, seq_start + 1, seq_start + 2)])
                if result is not None:
                    return result

    return None


def find_hu_combinations_for_each_possible_hu(cards):
    base_score = 4
    possible_hus = find_possible_hu(cards)
    combinations = []

    remaining_counts = {x: 4 - cards.count(x) for x in range(1, 10)}  # 预先计算每张牌的剩余张数

    for hu in possible_hus:
        remaining = remaining_counts[hu]
        test_hand = cards + [hu]
        is_pengpenghu = True
        is_qiduizi = False
        is_longqiduizi = False  # 龙七对标识
        is_dandiao = False  # 单吊标识
        gang_count = 0  # 杠的数量

        # 检查是否有杠
        for j in range(9):
            if test_hand.count(j + 1) == 4:
                gang_count += 1
                if len(set(test_hand)) == 5:  # 如果是五对，那么是龙七对
                    is_longqiduizi = True

        # 检查是否七对子
        if len(test_hand) == 14 and len(set(test_hand)) == 7 and all(test_hand.count(x) == 2 for x in set(test_hand)):
            is_qiduizi = True

        # 检查是否单吊（手牌中除了一对将牌，其他都已成型的碰碰胡）
        if test_hand.count(hu) == 2 and len(set(test_hand)) == 2:
            is_dandiao = True

        for j in range(len(test_hand)):
            if test_hand.count(test_hand[j]) >= 2:
                pair = [test_hand[j], test_hand[j]]
                new_cards = test_hand.copy()
                new_cards.remove(test_hand[j])
                new_cards.remove(test_hand[j])
                result = dfs_melds(new_cards)
                if result is not None:
                    score = base_score
                    # 杠的数量决定翻倍次数
                    score *= (2 ** gang_count)
                    # 检查是否碰碰胡
                    if not all(len(m) == 3 and m[0] == m[1] for m in result):
                        is_pengpenghu = False
                    if is_pengpenghu and not is_longqiduizi and not is_dandiao:
                        score *= 2
                    # 七对子记16分
                    if is_qiduizi:
                        score = 16
                    # 龙七对记32分
                    if is_longqiduizi:
                        score = 32
                    # 清一色单吊记32分
                    if is_dandiao:
                        score = 32
                    combinations.append({
                        '胡牌': hu,
                        '将': pair,
                        '组合': result,
                        '分数': score,
                        '剩余张数': remaining
                    })
                    break

    return possible_hus, combinations


def check_hu(cards):
    if len(cards) == 0:
        return True
    counts = [0] * 9
    for card in cards:
        counts[card - 1] += 1
    for i in range(9):
        if counts[i] >= 2:
            counts[i] -= 2
            if dfs(counts):
                return True
            counts[i] += 2
    return False


def dfs(counts):
    # 移除顺子和刻子
    for i in range(9):
        if counts[i] >= 3:  # 移除刻子
            counts[i] -= 3
            if dfs(counts):
                return True
            counts[i] += 3
        if i <= 6 and counts[i] > 0 and counts[i + 1] > 0 and counts[i + 2] > 0:  # 移除顺子
            counts[i] -= 1
            counts[i + 1] -= 1
            counts[i + 2] -= 1
            if dfs(counts):
                return True
            counts[i] += 1
            counts[i + 1] += 1
            counts[i + 2] += 1
    return all(count == 0 for count in counts)


def find_possible_hu(cards):
    possible_hu = []
    for i in range(1, 10):
        if check_hu(cards + [i]):
            possible_hu.append(i)
    return possible_hu


HTML_PAGE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>清一色胡牌计算器</title>
    <style>
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 3vw; /* 使用视口宽度单位 */
            text-align: center;
            padding-top: 50px;
            margin: 0;
            background-image: url('/static/images/bg.png');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-weight: bold;
        }
        form {
            font-size: 10px;
            background-color: rgba(120, 150, 200, 0.7);
            padding: 15px;
            border-radius: 10px;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            opacity: 1;
            
        }
        input[type="text"], input[type="button"] {
            font-size: 3vw; /* 输入框内字体大小也根据屏幕大小自动调整 */
            max-font-size: 8px; /* 设置最大字体大小以避免在大屏幕上字体过大 */
        }

        input[type="button"] {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            opacity: 1;
        }
        input[type="button"]:hover {
            background-color: #007BFF;
        }
        #result {
            margin-top: 20px;
            white-space: pre-wrap; 
            
        }
        /* 图片样式 */
        .mahjong-tile {
            width: auto;    
            height: 7vw;   /* 使用视口宽度单位，根据屏幕大小自动调整图片高度 */
            vertical-align: middle;
            max-height: 50px; /* 设置最大高度以避免在大屏幕上图片过大 */
        }
        
        /* 文本样式 */
        #result div, form {
            font-size: 2vw;  /* 使用视口宽度单位，根据屏幕大小自动调整字体大小 */
            line-height: normal; /* 可根据需要调整 */
            vertical-align: middle;
            margin-bottom: 4px;
            max-font-size: 8px; /* 设置最大字体大小以避免在大屏幕上字体过大 */
        }
        
        body::after {
            content: "版权所有 © Joe0210";
            position: fixed;
            bottom: 0;
            left: 0;
            color: #000;
            opacity: 0.5;
            font-size: 10px;
            z-index: 9999;
        }
        .highlight {
            color: red;
            font-weight: bold;
        }
        @media (min-width: 768px) {
            .mahjong-tile, #result div, form, input[type="text"], input[type="button"] {
                font-size: 14px; /* 在屏幕宽度大于768px时，将字体大小固定为14px */
                height: 50px; /* 同理，图片高度固定为50px */
            }
        }
        
    </style>
</head>
<body>
    <h2>麻将胡牌计算器</h2>
    <p>本计算器仅用于计算清一色情况下的手牌胡牌可能性 不包括碰杠牌区 无论花色如何 结果均使用'万'表示 记分为参考值</p>
    <form id="mahjongForm">
        <label for="hand">输入你的清一色'手牌' 不限顺序 如[2223334445556]</label><br>
        <input type="text" id="hand" name="hand"><br>
        <input type="button" value="计算胡牌" onclick="calculateHu()">
    </form>
    <div id="result"></div>

    <script>
    function numberToMahjongTile(number) {
        return `<img src="/static/images/${number}.jpg" alt="Tile ${number}" class="mahjong-tile">`;
    }

    function calculateHu() {
        var hand = document.getElementById('hand').value;
        fetch('/mahjong?hand=' + hand)
        .then(response => response.json())
        .then(data => {
            
            let resultDiv = document.getElementById('result');
            resultDiv.innerHTML = ''; // Clear previous results
    
            if (data.error) {
                resultDiv.innerText = data.error;
            } else {
                let possibleHuDiv = document.createElement('div');
                possibleHuDiv.innerHTML = '听牌  \u279C  ';
                data.possible_hu.forEach(hu => {
                    possibleHuDiv.innerHTML += numberToMahjongTile(hu);
                });
                resultDiv.appendChild(possibleHuDiv);
    
                data.combinations.forEach(combo => {
                    let combinationDiv = document.createElement('div');
                    let tileHtml = combo['将'].map(tile => numberToMahjongTile(tile)).join('');
                
                    combo['组合'].forEach(meld => {
                        tileHtml += '  ';
                        meld.forEach(tile => {
                            tileHtml += numberToMahjongTile(tile);
                        });
                    });
                
                    // 分数保持在原位置，即在牌型显示之前
                    let scoreHtml = ` ${combo['分数']}分 `;
                
                    // 在每一行的最后添加剩余张数
                    let remaining = combo['剩余张数'];
                    let remainingHtml = remaining !== undefined ? `   （剩余张数：${remaining}）` : '';
                    if (remaining === 0) {
                        remainingHtml = `<span class="highlight">   （剩余张数：0）</span>`;
                    }
                
                    combinationDiv.innerHTML = `${numberToMahjongTile(combo['胡牌'])} \u279C ${scoreHtml}${tileHtml}${remainingHtml}`;
                    resultDiv.appendChild(combinationDiv);
                });

            }
        })
        .catch(error => {
            console.error('错误:', error);
            document.getElementById('result').innerText = '错误：' + error;
        });
    }
    </script>
</body>
</html>

'''


def number_to_mahjong_tile_html(number):
    return f'<img src="/static/images/{number}.jpg" alt="Tile {number}" class="mahjong-tile">'


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/mahjong', methods=['GET'])
def mahjong_api():

    hand_str = request.args.get('hand', '')
    if not hand_str.isdigit():
        return jsonify({'error': '只能输数字！别乱输哈！'}), 400

    hand = [int(x) for x in hand_str]
    if len(hand) % 3 != 1:
        return jsonify({'error': '你相公了！'}), 400

    if not all(char.isdigit() and 1 <= int(char) <= 9 for char in hand_str):
        return jsonify({'error': '不能有0！只能1～9！'}), 400

    possible_hu, combinations = find_hu_combinations_for_each_possible_hu(hand)
    if not possible_hu:
        return jsonify({'error': '还没听呢！再等等吧！'}), 400

    combinations_data = []
    for combo in combinations:
        combinations_data.append({
            '胡牌': combo['胡牌'],
            '将': combo['将'],
            '组合': combo['组合'],
            '分数': combo['分数'],
            '剩余张数': combo['剩余张数']
        })
    return jsonify({'possible_hu': possible_hu, 'combinations': combinations_data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=False)
