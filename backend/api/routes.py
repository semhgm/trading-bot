from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bot.engine import engine
from pydantic import BaseModel
from auth import login, verify_token
import asyncio

router = APIRouter()
security = HTTPBearer()

# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
def auth_login(req: LoginRequest):
    token = login(req.username, req.password)
    if not token:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
    return {"token": token}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz token")
    return user

# --- Bot ---
class ConfigUpdate(BaseModel):
    symbol: str = None
    buy_threshold: float = None
    sell_threshold: float = None
    max_daily_trades: int = None
    trade_amount: float = None
    stop_loss: float = None
    live_trading: bool = None

@router.get("/status")
def get_status(user=Depends(get_current_user)):
    return engine.get_status()

@router.post("/start")
async def start_bot(user=Depends(get_current_user)):
    if engine.config.is_running:
        return {"message": "Bot zaten çalışıyor"}
    asyncio.create_task(engine.start())
    return {"message": "Bot başlatıldı"}

@router.post("/stop")
def stop_bot(user=Depends(get_current_user)):
    engine.stop()
    return {"message": "Bot durduruldu"}

@router.post("/config")
async def update_config(config: ConfigUpdate, user=Depends(get_current_user)):
    was_running = engine.config.is_running
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
    
    if was_running:
        await asyncio.sleep(0.5)
        asyncio.create_task(engine.start())
    
    return {"message": "Config güncellendi", "config": vars(engine.config)}

@router.get("/balance")
def get_balance(user=Depends(get_current_user)):
    from bot.bybit import get_balance as fetch_balance
    balance = fetch_balance("USDT")
    return {"balance": balance}