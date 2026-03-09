from fastapi import APIRouter
from bot.engine import engine
from pydantic import BaseModel
import asyncio

router = APIRouter()

class ConfigUpdate(BaseModel):
    symbol: str = None
    buy_threshold: float = None
    sell_threshold: float = None
    max_daily_trades: int = None
    trade_amount: float = None
    stop_loss: float = None
    live_trading: bool = None

@router.get("/status")
def get_status():
    return engine.get_status()

@router.post("/start")
async def start_bot():
    if engine.config.is_running:
        return {"message": "Bot zaten çalışıyor"}
    asyncio.create_task(engine.start())
    return {"message": "Bot başlatıldı"}

@router.post("/stop")
def stop_bot():
    engine.stop()
    return {"message": "Bot durduruldu"}

@router.post("/config")
async def update_config(config: ConfigUpdate):
    was_running = engine.config.is_running
    
    # Önce durdur
    engine.stop()
    
    if config.symbol is not None:
        engine.config.symbol = config.symbol
    if config.buy_threshold is not None:
        engine.config.buy_threshold = config.buy_threshold
    if config.sell_threshold is not None:
        engine.config.sell_threshold = config.sell_threshold
    if config.max_daily_trades is not None:
        engine.config.max_daily_trades = config.max_daily_trades
    if config.trade_amount is not None:
        engine.config.trade_amount = config.trade_amount
    if config.stop_loss is not None:
        engine.config.stop_loss = config.stop_loss
    if config.live_trading is not None:
        engine.config.live_trading = config.live_trading
    
    # Çalışıyorsa yeniden başlat
    if was_running:
        await asyncio.sleep(0.5)
        asyncio.create_task(engine.start())
    
    return {"message": "Config güncellendi", "config": vars(engine.config)}

@router.get("/balance")
def get_balance():
    from bot.bybit import get_balance as fetch_balance
    balance = fetch_balance("USDT")
    return {"balance": balance}