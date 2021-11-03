# Funding rate trading tool v 0.0.2
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager, BinanceSocketManager
from datetime import date, datetime, time, timedelta
import time

#
# api_key = "Change This"
# api_secret = "Change This"
from binance.exceptions import BinanceAPIException

api_key = input("Input your API Key: ")
api_secret = input("Input your API Secret: ")
client = Client(api_key, api_secret)
pair = dict()

tickers = client.get_ticker()


# for s in exchange_info['symbols']:
#     pair[s['symbol']] = client.get_ticker(symbol="BTCUSDT")["priceChangePercent"]
#     print(client.get_ticker(symbol="BTCUSDT")["priceChangePercent"])
# print(pair)
def find_pair():
    for i in tickers:
        if "USDT" in i["symbol"]:
            pair[i["symbol"]] = float(i["priceChangePercent"])
            # print(i["symbol"] + " " + i["priceChangePercent"])
    all_values = pair.values()
    max_value = max(all_values)
    max_key = max(pair, key=pair.get)
    # a = sorted(pair.items(), key=lambda x: x[1], reverse=True)
    return max_key


trade_pair = ""
walletpercentage = int(input("Input wallet percent(0-100): "))
gainpercentage = 1  # Percent TP
losspercentage = 1.5  # Percent STOP LOSS
leverage = 1  # Don Bay

status = False


def long():
    # Long
    # 1 for BTC , 5 for USDT
    balance = (float(client.futures_account_balance()[5]["balance"]) * walletpercentage) / 100
    print(balance)
    price_first_pair = float(client.futures_mark_price(symbol=trade_pair)["markPrice"])
    quantity_usdt = float(round((balance * leverage) / price_first_pair, 0))
    print("DEBUG quantity_usdt " + str(quantity_usdt))
    order = client.futures_create_order(symbol=trade_pair,
                                        side="BUY",
                                        type="MARKET",
                                        quantity=quantity_usdt)
    # BTCUSDT thì là BTC
    price = float(client.futures_mark_price(symbol=trade_pair)["markPrice"])

    # Take profit
    take_profit = float(price + (price * gainpercentage) / 100)
    print("DEBUG take_profit " + str(round(take_profit, 4)))
    TAKEPROFIT = client.futures_create_order(symbol=trade_pair, side="SELL",
                                             type="TAKE_PROFIT_MARKET",
                                             stopPrice=round(take_profit, 4),
                                             closePosition=True)
    stop_price = float(price - (price * losspercentage) / 100)
    print("DEBUG stop price " + str(round(stop_price, 4)))
    # Stop loss
    STOP = client.futures_create_order(symbol=trade_pair, side="SELL", type="STOP_MARKET",
                                       stopPrice=round(stop_price, 4),
                                       closePosition=True)

    return str(datetime.now())[0:19] + " - Long position opened"


def short():
    balance = (float(client.futures_account_balance()[5]["balance"]) * walletpercentage) / 100
    print(balance)
    price_first_pair = float(client.futures_mark_price(symbol=trade_pair)["markPrice"])
    quantity_usdt = float(round((balance * leverage) / price_first_pair, 0))
    print("DEBUG quantity_usdt " + str(quantity_usdt))

    order = client.futures_create_order(symbol=trade_pair, side="SELL", type="MARKET", quantity=quantity_usdt)
    # BTCUSDT thì là BTC
    price = float(client.futures_mark_price(symbol=trade_pair)["markPrice"])

    # stop
    stop_price = float(price + (price * losspercentage) / 100)
    print("DEBUG stop price " + str(round(stop_price, 4)))
    STOP = client.futures_create_order(symbol=trade_pair, side="BUY",
                                       type="STOP_MARKET",
                                       stopPrice=round(stop_price, 4),
                                       closePosition=True)

    # take
    take_profit = float(price - (price * gainpercentage) / 100)
    print("DEBUG take_profit " + str(round(take_profit, 4)))
    TAKEPROFIT = client.futures_create_order(symbol=trade_pair, side="BUY",
                                             type="TAKE_PROFIT_MARKET",
                                             stopPrice=round(take_profit, 4),
                                             closePosition=True)

    return str(datetime.now())[0:19] + " - Short position opened"


def __init__():
    global status
    global trade_pair
    try:
        while True:
            trade_pair = find_pair()
            print("Choosen pair: " + trade_pair)
            mark_price = client.futures_mark_price(symbol=trade_pair)
            lastFundingRate = float(mark_price["lastFundingRate"])
            print("Funding Rate " + trade_pair + " " + str(lastFundingRate * 100) + "%")
            now = datetime.now()
            print("Time : " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
            if lastFundingRate > 0:
                if (now.hour == 6 and now.minute == 59 and 50 <= now.second <= 59) \
                        or (now.hour == 14 and now.minute == 55 and 50 <= now.second <= 59) \
                        or (now.hour == 22 and now.minute == 55 and 50 <= now.second <= 59) and not status:
                    print(long())
                    time.sleep(10)
                else:
                    status = False
            else:
                if (now.hour == 6 and now.minute == 59 and 50 <= now.second <= 59) \
                        or (now.hour == 14 and now.minute == 55 and 50 <= now.second <= 59) \
                        or (now.hour == 22 and now.minute == 55 and 50 <= now.second <= 59) and not status:
                    print(short())
                    time.sleep(10)
                else:
                    status = False
            time.sleep(2)
    except BinanceAPIException as e:
        print(e.status_code, file=open('output.txt', 'a'))
        print(e.message, file=open('output.txt', 'a'))

    # long()


__init__()
