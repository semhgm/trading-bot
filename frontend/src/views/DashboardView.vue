<template>
  <div class="min-h-screen bg-gray-950 text-white p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-white">Trading Bot</h1>
      <div class="flex items-center gap-4">
        <router-link to="/settings" class="text-gray-400 hover:text-white transition text-sm">⚙ Ayarlar</router-link>
        <div class="flex items-center gap-2">
          <div :class="status.is_running ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
          <span class="text-sm text-gray-400">{{ status.is_running ? 'Çalışıyor' : 'Durduruldu' }}</span>
        </div>
      </div>
    </div>

    <!-- Üst Kartlar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-1">Anlık Fiyat</p>
        <p class="text-2xl font-bold text-white">${{ status.current_price?.toLocaleString() }}</p>
        <p class="text-gray-500 text-sm mt-1">{{ status.symbol }}</p>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-1">Referans Fiyat</p>
        <p class="text-2xl font-bold text-yellow-400">${{ status.entry_price?.toLocaleString() }}</p>
        <p class="text-gray-500 text-sm mt-1">
          <span :class="priceChange >= 0 ? 'text-green-400' : 'text-red-400'">
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange }}%
          </span>
        </p>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-1">Toplam P&L</p>
        <p :class="status.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'" class="text-2xl font-bold">
          {{ status.total_pnl >= 0 ? '+' : '' }}${{ status.total_pnl?.toFixed(4) }}
        </p>
        <p class="text-gray-500 text-sm mt-1">Komisyon: ${{ status.total_commission?.toFixed(4) }}</p>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-1">Günlük İşlem</p>
        <p class="text-2xl font-bold text-blue-400">{{ status.daily_trades }} / {{ status.max_daily_trades }}</p>
        <p class="text-gray-500 text-sm mt-1">İşlem sayısı</p>
      </div>
    </div>

    <!-- Pozisyon & Kontrol -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-3">Pozisyon Durumu</p>
        <div :class="status.in_position ? 'bg-green-900 border-green-700' : 'bg-gray-800 border-gray-700'"
          class="rounded-lg p-4 border text-center">
          <p class="text-lg font-semibold">{{ status.in_position ? '📈 Pozisyonda' : '⏳ Bekliyor' }}</p>
        </div>
        <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div class="bg-gray-800 rounded-lg p-3">
            <p class="text-gray-500">Alış Eşiği</p>
            <p class="text-green-400 font-semibold">{{ status.buy_threshold }}%</p>
          </div>
          <div class="bg-gray-800 rounded-lg p-3">
            <p class="text-gray-500">Satış Eşiği</p>
            <p class="text-red-400 font-semibold">+{{ status.sell_threshold }}%</p>
          </div>
        </div>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p class="text-gray-400 text-sm mb-3">Bot Kontrolü</p>
        <div class="flex gap-3">
          <button @click="startBot" :disabled="status.is_running"
            class="flex-1 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg py-3 font-semibold transition">
            ▶ Başlat
          </button>
          <button @click="stopBot" :disabled="!status.is_running"
            class="flex-1 bg-red-600 hover:bg-red-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg py-3 font-semibold transition">
            ■ Durdur
          </button>
        </div>
        <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div class="bg-gray-800 rounded-lg p-3">
            <p class="text-gray-500">İşlem Miktarı</p>
            <p class="text-white font-semibold">${{ status.trade_amount }} USDT</p>
          </div>
          <div class="bg-gray-800 rounded-lg p-3">
            <p class="text-gray-500">Mod</p>
            <p :class="status.live_trading ? 'text-red-400' : 'text-blue-400'" class="font-semibold">
              {{ status.live_trading ? '🔴 Gerçek' : '🔵 Simülasyon' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- İşlem Geçmişi -->
    <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
      <p class="text-gray-400 text-sm mb-4">Son İşlemler</p>
      <div v-if="status.trade_history?.length === 0" class="text-center text-gray-600 py-8">
        Henüz işlem yok
      </div>
      <div v-else class="space-y-2">
        <div v-for="(trade, i) in [...status.trade_history].reverse()" :key="i"
          :class="trade.side === 'Buy' ? 'border-green-800' : 'border-red-800'"
          class="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3 border">
          <div class="flex items-center gap-3">
            <span :class="trade.side === 'Buy' ? 'bg-green-600' : 'bg-red-600'"
              class="px-2 py-1 rounded text-xs font-bold">
              {{ trade.side.toUpperCase() }}
            </span>
            <span class="text-gray-400 text-sm">{{ trade.reason }}</span>
          </div>
          <div class="flex items-center gap-6">
            <div class="text-right" v-if="trade.side === 'Sell'">
              <p :class="trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm font-semibold">
                {{ trade.pnl >= 0 ? '+' : '' }}${{ trade.pnl?.toFixed(4) }}
              </p>
              <p class="text-gray-600 text-xs">komisyon: ${{ trade.commission }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold">${{ trade.price?.toLocaleString() }}</p>
              <p class="text-gray-500 text-xs">{{ new Date(trade.timestamp).toLocaleTimeString() }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const status = ref({
  is_running: false,
  symbol: 'BTCUSDT',
  current_price: 0,
  entry_price: null,
  in_position: false,
  daily_trades: 0,
  max_daily_trades: 10,
  trade_amount: 10,
  buy_threshold: -1.0,
  sell_threshold: 1.0,
  live_trading: false,
  total_pnl: 0,
  total_commission: 0,
  trade_history: []
})

const priceChange = computed(() => {
  if (!status.value.entry_price || !status.value.current_price) return 0
  return (((status.value.current_price - status.value.entry_price) / status.value.entry_price) * 100).toFixed(3)
})

let interval = null

const fetchStatus = async () => {
  try {
const res = await fetch(`${import.meta.env.VITE_API_URL}/api/status`)
    status.value = await res.json()
  } catch (e) {
    console.error('API bağlantı hatası:', e)
  }
}

const startBot = async () => {
await fetch(`${import.meta.env.VITE_API_URL}/api/start`, { method: 'POST' })
  fetchStatus()
}

const stopBot = async () => {
await fetch(`${import.meta.env.VITE_API_URL}/api/stop`, { method: 'POST' })
  fetchStatus()
}

onMounted(() => {
  fetchStatus()
  interval = setInterval(fetchStatus, 2000)
})

onUnmounted(() => {
  clearInterval(interval)
})
</script>