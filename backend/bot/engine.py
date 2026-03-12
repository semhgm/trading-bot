import asyncio
from datetime import datetime
from typing import Optional
from .bybit import watch_price, place_order, get_balance
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db


class BotConfig:
    def __init__(self):
        self.symbol = "BTCUSDT"
        self.buy_threshold = -1.0
        self.sell_threshold = 1.0
        self.max_daily_trades = 10
        self.trade_amount = 10
        self.stop_loss = -5.0
        self.is_running = False
        self.live_trading = False


class TradingEngine:
    def __init__(self):
        self.config = BotConfig()
        self.entry_price: Optional[float] = None
        self.current_price: float = 0
        self.daily_trades: int = 0
        self.trade_history = []
        self.in_position = False
        self.balance: float = 0
        self.session_id: Optional[int] = None

    def get_status(self):
        total_pnl = sum(t.get("pnl", 0) for t in self.trade_history)
        total_commission = sum(t.get("commission", 0) for t in self.trade_history)
        return {
            "is_running": self.config.is_running,
            "symbol": self.config.symbol,
            "current_price": self.current_price,
            "entry_price": self.entry_price,
            "in_position": self.in_position,
            "daily_trades": self.daily_trades,
            "max_daily_trades": self.config.max_daily_trades,
            "trade_amount": self.config.trade_amount,
            "buy_threshold": self.config.buy_threshold,
            "sell_threshold": self.config.sell_threshold,
            "stop_loss": self.config.stop_loss,
            "live_trading": self.config.live_trading,
            "balance": self.balance,
            "total_pnl": round(total_pnl, 4),
            "total_commission": round(total_commission, 4),
            "trade_history": self.trade_history[-20:],
        }

    async def on_price_update(self, symbol: str, price: float):
        if symbol.lower() != self.config.symbol.lower():
            return

        self.current_price = price

        if not self.config.is_running:
            return
        if self.daily_trades >= self.config.max_daily_trades:
            return

        if not self.entry_price:
            self.entry_price = price
            print(f"[Engine] Referans fiyat: {price}")
            return

        change = ((price - self.entry_price) / self.entry_price) * 100

        if not self.in_position:
            if change <= self.config.buy_threshold:
                await self.execute_trade("Buy", price)
        else:
            if change >= self.config.sell_threshold:
                await self.execute_trade("Sell", price)
            elif change <= self.config.stop_loss:
                await self.execute_trade("Sell", price, reason="STOP_LOSS")

    async def execute_trade(self, side: str, price: float, reason: str = "SIGNAL"):
        qty = round(self.config.trade_amount / price, 6)
        commission_rate = 0.001
        commission = self.config.trade_amount * commission_rate

        pnl = 0
        if side == "Sell" and self.entry_price:
            gross_pnl = (price - self.entry_price) / self.entry_price * self.config.trade_amount
            pnl = gross_pnl - (commission * 2)

        if self.config.live_trading:
            result = place_order(self.config.symbol, side, qty)
            if not result:
                print(f"[Engine] Emir başarısız, atlandı")
                return

        trade = {
            "side": side,
            "price": price,
            "qty": qty,
            "amount_usdt": self.config.trade_amount,
            "commission": round(commission, 4),
            "pnl": round(pnl, 4),
            "reason": reason,
            "live": self.config.live_trading,
            "timestamp": datetime.now().isoformat(),
        }
        self.trade_history.append(trade)
        self.daily_trades += 1

        # SQLite'a kaydet
        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO trades (symbol, side, price, quantity, pnl, commission, mode, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.config.symbol,
                side,
                price,
                qty,
                round(pnl, 4),
                round(commission, 4),
                "live" if self.config.live_trading else "simulation",
                reason
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] Kayıt hatası: {e}")

        if side == "Buy":
            self.in_position = True
            self.entry_price = price
        else:
            self.in_position = False
            self.entry_price = price

        print(f"[{reason}] {side} @ {price} | pnl: {pnl:.4f} USDT | komisyon: {commission:.4f}")

        if self.config.live_trading:
            self.balance = get_balance("USDT")

    async def start(self):
        self.config.is_running = True
        self.daily_trades = 0
        self.entry_price = None
        self.in_position = False
        self.trade_history = []
        if self.config.live_trading:
            self.balance = get_balance("USDT")

        # Session başlat
        try:
            conn = get_db()
            cursor = conn.execute("""
                INSERT INTO sessions (symbol, mode)
                VALUES (?, ?)
            """, (
                self.config.symbol,
                "live" if self.config.live_trading else "simulation"
            ))
            self.session_id = cursor.lastrowid
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] Session başlatma hatası: {e}")

        print(f"[Engine] Bot başlatıldı → {self.config.symbol} | Live: {self.config.live_trading}")
        await watch_price(self.config.symbol, self.on_price_update)

    def stop(self):
        self.config.is_running = False

        # Session kapat
        if self.session_id:
            try:
                total_pnl = sum(t.get("pnl", 0) for t in self.trade_history)
                total_commission = sum(t.get("commission", 0) for t in self.trade_history)
                conn = get_db()
                conn.execute("""
                    UPDATE sessions
                    SET stopped_at = CURRENT_TIMESTAMP,
                        total_trades = ?,
                        total_pnl = ?,
                        total_commission = ?
                    WHERE id = ?
                """, (len(self.trade_history), round(total_pnl, 4), round(total_commission, 4), self.session_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[DB] Session kapatma hatası: {e}")

        self.entry_price = None
        self.in_position = False
        self.current_price = 0
        self.session_id = None
        print("[Engine] Bot durduruldu")


engine = TradingEngine()