from binance.client import Client
from time import sleep

persent = int(input("Введите процент[Пример - 1.2]: "))
min_depth_asks = int(input("Введите объем в тысячах для верхнего(↑) стакана[Пример - 500]: "))
min_depth_bids = int(input("Введите объем в тысячах для нижнего(↓) стакана[Пример - 500]: "))

client = Client()
info = client.futures_exchange_info()
rate_limit = info["rateLimits"][0]["limit"]
print(f"Rate limit per minute: {rate_limit}")

symbols = client.futures_exchange_info()["symbols"]
symbols = list(filter(
    lambda x: x["quoteAsset"] == "USDT" and x["marginAsset"] == "USDT" and x["status"] == "TRADING", symbols
))
symbols = list(map(lambda x: x["baseAsset"], symbols))
symbols = sorted(list(set(symbols)))
print(f"Доступных символов на бирже: {len(symbols)}")

api_load_adjustment = 1.2
all_time = api_load_adjustment * len(symbols) * 20 / rate_limit
time_to_sleep = all_time / len(symbols) * 60
print(f"Примерно займет времени: {str(all_time)}m")


white_list = []
white_list_asks = []
white_list_bids = []
for progress, symbol in enumerate(symbols):
    depth = client.futures_order_book(symbol=symbol + "USDT", limit=1000)
    # asks - верхний стакан, bids - нижний

    # 0 - price, 1 - qty
    asks_min = min(list(map(lambda x: float(x[0]), depth["asks"])))
    bids_max = max(list(map(lambda x: float(x[0]), depth["bids"])))
    asks_qty = sum(list(map(
        lambda x: float(x[1]), filter(lambda x: float(x[0]) <= asks_min * (1 + persent / 100), depth["asks"])
    )))
    bids_qty = sum(list(map(
        lambda x: float(x[1]), filter(lambda x: float(x[0]) >= bids_max * (1 - persent / 100), depth["bids"])
    )))
    asks_k = asks_qty * asks_min / 1000
    bids_k = bids_qty * bids_max / 1000

    if asks_k >= min_depth_asks and bids_k >= min_depth_bids:
        white_list.append(symbol)
    if asks_k >= min_depth_asks:
        white_list_asks.append(symbol)
    if bids_k >= min_depth_bids:
        white_list_bids.append(symbol)
    print(f"Прогресс: {progress + 1}/{len(symbols)}; {symbol} ↑:{asks_k} | ↓:{bids_k}")
    sleep(time_to_sleep)

white_list = sorted(list(set(white_list)))
black_list = sorted(list(set(symbols) - set(white_list)))
print()
print(f"Для обоих стаканов:")
print(f"White list, всего {len(white_list)} монет с объемом ↑{min_depth_asks}k и ↓{min_depth_bids}k в {persent}%:")
print("\t", ",".join(white_list), sep="")
print(f"Black list, всего {len(black_list)} монет с объемом ↑{min_depth_asks}k и ↓{min_depth_bids}k в {persent}%:")
print("\t", ",".join(black_list), sep="")

white_list = sorted(list(set(white_list_asks)))
black_list = sorted(list(set(symbols) - set(white_list_asks)))
print()
print(f"Для верхнего стакана стакана:")
print(f"White list, всего {len(white_list)} монет с объемом ↑{min_depth_asks}k в {persent}%:")
print("\t", ",".join(white_list), sep="")
print(f"Black list, всего {len(black_list)} монет с объемом ↑{min_depth_asks}k в {persent}%:")
print("\t", ",".join(black_list), sep="")

white_list = sorted(list(set(white_list_bids)))
black_list = sorted(list(set(symbols) - set(white_list_bids)))
print()
print(f"Для нижнего стакана стакана:")
print(f"White list, всего {len(white_list)} монет с объемом ↓{min_depth_bids}k в {persent}%:")
print("\t", ",".join(white_list), sep="")
print(f"Black list, всего {len(black_list)} монет с объемом ↓{min_depth_bids}k в {persent}%:")
print("\t", ",".join(black_list), sep="")

input("Нажмите для выхода...")