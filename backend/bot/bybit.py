import asyncio
import json
import ssl
import websockets
from typing import Callable
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import os

load_dotenv()

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"

def get_bybit_client():
    return HTTP(
        testnet=False,
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
    )

async def watch_price(symbol: str, callback: Callable):
    symbol_lower = symbol.lower()
    url = f"{BINANCE_WS_URL}/{symbol_lower}@ticker"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    while True:
        try:
            async with websockets.connect(url, ssl=ssl_context, ping_interval=20, ping_timeout=10) as ws:
                print(f"[Binance] {symbol} izleniyor...")
                async for message in ws:
                    data = json.loads(message)
                    price = float(data.get("c", 0))
                    if price > 0:
                        yield_result = await callback(symbol, price)
                        # Bot durdurulduysa WebSocket'ten çık
                        if not yield_result and hasattr(callback, '__self__') and not callback.__self__.config.is_running:
                            return
        except Exception as e:
            print(f"[Binance] Bağlantı koptu ({e})")
            await asyncio.sleep(3)
            symbol_lower = symbol.lower()
    url = f"{BINANCE_WS_URL}/{symbol_lower}@ticker"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    while True:
        try:
            async with websockets.connect(url, ssl=ssl_context, ping_interval=20, ping_timeout=10) as ws:
                print(f"[Binance] {symbol} izleniyor...")
                async for message in ws:
                    data = json.loads(message)
                    price = float(data.get("c", 0))
                    if price > 0:
                        await callback(symbol, price)
        except Exception as e:
            print(f"[Binance] Bağlantı koptu, yeniden bağlanıyor... ({e})")
            await asyncio.sleep(3)
    symbol_lower = symbol.lower()
    url = f"{BINANCE_WS_URL}/{symbol_lower}@ticker"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with websockets.connect(url, ssl=ssl_context) as ws:
        print(f"[Binance] {symbol} izleniyor...")
        async for message in ws:
            data = json.loads(message)
            price = float(data.get("c", 0))
            if price > 0:
                await callback(symbol, price)

def place_order(symbol: str, side: str, qty: float):
    """Bybit'e gerçek emir gönder"""
    try:
        client = get_bybit_client()
        result = client.place_order(
            category="spot",
            symbol=symbol,
            side=side,        # "Buy" veya "Sell"
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