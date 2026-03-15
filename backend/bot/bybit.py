import asyncio
import json
import ssl
import websockets
from typing import Callable
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/spot"

def get_bybit_client():
    return HTTP(
        testnet=False,
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
    )

async def watch_price(symbol: str, callback: Callable):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            async with websockets.connect(BYBIT_WS_URL, ssl=ssl_context, ping_interval=20, ping_timeout=10) as ws:
                # Bybit'e subscribe ol
                subscribe_msg = {
                    "op": "subscribe",
                    "args": [f"tickers.{symbol}"]
                }
                await ws.send(json.dumps(subscribe_msg))
                print(f"[Bybit] {symbol} izleniyor...")

                async for message in ws:
                    data = json.loads(message)
                    if data.get("topic", "").startswith("tickers."):
                        price_str = data.get("data", {}).get("lastPrice", 0)
                        price = float(price_str) if price_str else 0
                        if price > 0:
                            await callback(symbol, price)
        except Exception as e:
            print(f"[Bybit] Bağlantı koptu ({e})")
            await asyncio.sleep(3)

def place_order(symbol: str, side: str, qty: float):
    """Bybit'e gerçek emir gönder"""
    try:
        client = get_bybit_client()
        result = client.place_order(
            category="spot",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
        )
        print(f"[Bybit] Emir gönderildi: {side} {qty} {symbol}")
        return result
    except Exception as e:
        print(f"[Bybit] Emir hatası: {e}")
        return None

def get_balance(coin: str = "USDT"):
    """Hesap bakiyesini çek"""
    try:
        client = get_bybit_client()
        result = client.get_wallet_balance(accountType="UNIFIED", coin=coin)
        balance = result["result"]["list"][0]["coin"][0]["walletBalance"]
        return float(balance)
    except Exception as e:
        print(f"[Bybit] Bakiye hatası: {e}")
        return 0.0