import requests
import os
import time

# 城市設定
cities = ["Caerleon", "Black Market"]

def load_items(path):
    if not os.path.exists(path):
        print(f"⚠️ 找不到 {path}")
        input("按 Enter 結束...")
        exit(1)

    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) >= 2:
                item_id = parts[1].strip()
                items.append(item_id)
    return items

def get_prices(item_ids, locations):
    url = f"https://east.albion-online-data.com/api/v2/stats/prices/{','.join(item_ids)}.json?locations={','.join(locations)}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    base_path = os.path.dirname(__file__)
    item_file = os.path.join(base_path, "items.txt")
    item_ids = load_items(item_file)

    batch_size = 40
    total_profit = 0
    total_net_profit = 0

    for i in range(0, len(item_ids), batch_size):
        batch = item_ids[i:i+batch_size]
        try:
            data = get_prices(batch, cities)
            batch_diff = []

            for item_id in batch:
                qualities = set([x["quality"] for x in data if x["item_id"] == item_id])
                for q in qualities:
                    caerleon_price = next((x["sell_price_min"] for x in data if x["item_id"] == item_id and x["city"] == "Caerleon" and x["quality"] == q), 0)
                    black_price = next((x["buy_price_max"] for x in data if x["item_id"] == item_id and x["city"] == "Black Market" and x["quality"] == q), 0)

                    if black_price > caerleon_price and caerleon_price > 0:
                        diff = black_price - caerleon_price
                        diff_percent = diff / caerleon_price
                        if diff_percent > 0.04:
                            net_profit = diff * 0.96
                            total_profit += diff
                            total_net_profit += net_profit
                            batch_diff.append((item_id, q, caerleon_price, black_price, diff, round(diff_percent * 100, 2), net_profit, total_profit, total_net_profit))

            if batch_diff:
                print("\n🧾 本批毛利 >4% 的項目：")
                for item_id, q, c_price, b_price, diff, diff_percent, net_profit, total_p, total_net_p in sorted(batch_diff, key=lambda x: x[4], reverse=True):
                    print(f"{item_id} (Q{q}): Caerleon={c_price}, BlackMarket={b_price}, Diff={diff}, Profit={diff_percent}%, 淨利={round(net_profit,2)}, 💰累計毛利={round(total_p,2)}, 💸累計淨利={round(total_net_p,2)}")

        except Exception as e:
            print(f"❌ Batch 錯誤: {e}")

        if i + batch_size < len(item_ids):
            time.sleep(5)

    print(f"\n✅ 全部完成！")
    print(f"💰 最終毛利總額: {round(total_profit, 2)} 銀幣")
    print(f"💸 最終扣除手續費後淨利: {round(total_net_profit, 2)} 銀幣")

if __name__ == "__main__":
    main()


# Albion Online 物品品質對照表 
# qualities     品質英文名稱    遊戲內中文對應      說明 
# Q1             Normal          普通            無額外加成 (無邊)
# Q2             Good            優良            稍好一點的品質 (鐵邊)
# Q3             Outstanding     優秀            有中等提升 (銅邊)
# Q4             Excellent       精良            高品質裝備 (銀邊)
# Q5             Masterpiece     傑作            最高品質 (金邊)