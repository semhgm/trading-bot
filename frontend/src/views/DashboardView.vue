<template>
  <div class="min-h-screen bg-[#0a0a0f] text-white font-mono">
    <!-- Top Bar -->
    <div class="border-b border-[#00ff88]/20 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div :class="status.is_running ? 'bg-[#00ff88] shadow-[0_0_10px_#00ff88]' : 'bg-red-500'" 
          class="w-2 h-2 rounded-full transition-all"></div>
        <span class="text-[#00ff88] font-bold tracking-widest text-sm">TRADING BOT</span>
        <span class="text-[#00ff88]/40 text-xs">// {{ status.symbol }}</span>
      </div>
      <div class="flex items-center gap-6">
        <router-link to="/history" class="text-[#00ff88]/50 hover:text-[#00ff88] transition text-xs tracking-widest">GEÇMIŞ</router-link>
        <router-link to="/settings" class="text-[#00ff88]/50 hover:text-[#00ff88] transition text-xs tracking-widest">AYARLAR</router-link>
        <button @click="logout" class="text-red-500/50 hover:text-red-400 transition text-xs tracking-widest">ÇIKIŞ</button>
        <span class="text-[#00ff88]/40 text-xs">{{ status.is_running ? 'ÇALIŞIYOR' : 'DURDURULDU' }}</span>
      </div>
    </div>

    <div class="p-6">
      <!-- Fiyat Kartları -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-4 relative overflow-hidden">
          <div class="absolute top-0 right-0 w-16 h-16 bg-[#00ff88]/5 rounded-full -translate-y-6 translate-x-6"></div>
          <p class="text-[#00ff88]/50 text-xs tracking-widest mb-2">ANLİK FİYAT</p>
          <p class="text-2xl font-bold text-white">${{ status.current_price?.toLocaleString() }}</p>
          <p class="text-[#00ff88]/40 text-xs mt-1">{{ status.symbol }}</p>
        </div>

        <div class="border border-yellow-500/20 bg-yellow-500/5 rounded-lg p-4 relative overflow-hidden">
          <div class="absolute top-0 right-0 w-16 h-16 bg-yellow-500/5 rounded-full -translate-y-6 translate-x-6"></div>
          <p class="text-yellow-500/50 text-xs tracking-widest mb-2">REFERANS</p>
          <p class="text-2xl font-bold text-yellow-400">${{ status.entry_price?.toLocaleString() ?? '—' }}</p>
          <p :class="priceChange >= 0 ? 'text-[#00ff88]' : 'text-red-400'" class="text-xs mt-1 font-bold">
            {{ priceChange >= 0 ? '▲' : '▼' }} {{ Math.abs(priceChange) }}%
          </p>
        </div>

        <div class="border border-blue-500/20 bg-blue-500/5 rounded-lg p-4 relative overflow-hidden">
          <div class="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 rounded-full -translate-y-6 translate-x-6"></div>
          <p class="text-blue-400/50 text-xs tracking-widest mb-2">TOPLAM P&L</p>
          <p :class="status.total_pnl >= 0 ? 'text-[#00ff88]' : 'text-red-400'" class="text-2xl font-bold">
            {{ status.total_pnl >= 0 ? '+' : '' }}${{ status.total_pnl?.toFixed(4) }}
          </p>
          <p class="text-blue-400/40 text-xs mt-1">KOM: ${{ status.total_commission?.toFixed(4) }}</p>
        </div>

        <div class="border border-purple-500/20 bg-purple-500/5 rounded-lg p-4 relative overflow-hidden">
          <div class="absolute top-0 right-0 w-16 h-16 bg-purple-500/5 rounded-full -translate-y-6 translate-x-6"></div>
          <p class="text-purple-400/50 text-xs tracking-widest mb-2">GÜNLÜK İŞLEM</p>
          <p class="text-2xl font-bold text-purple-400">{{ status.daily_trades }} / {{ status.max_daily_trades }}</p>
          <div class="mt-2 h-1 bg-purple-900 rounded-full overflow-hidden">
            <div class="h-full bg-purple-400 rounded-full transition-all"
              :style="`width: ${(status.daily_trades / status.max_daily_trades) * 100}%`"></div>
          </div>
        </div>
      </div>

      <!-- Orta Panel -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <!-- Pozisyon -->
        <div class="border border-[#00ff88]/20 rounded-lg p-5">
          <p class="text-[#00ff88]/50 text-xs tracking-widest mb-4">POZİSYON DURUMU</p>
          <div :class="status.in_position ? 'border-[#00ff88]/40 bg-[#00ff88]/10' : 'border-gray-700 bg-gray-800/50'"
            class="rounded-lg p-4 border text-center mb-4 transition-all">
            <p class="text-lg font-bold tracking-widest">
              {{ status.in_position ? '📈 POZİSYONDA' : '⏳ BEKLİYOR' }}
            </p>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="bg-[#00ff88]/5 border border-[#00ff88]/10 rounded-lg p-3">
              <p class="text-[#00ff88]/40 text-xs tracking-widest">ALIŞ EŞİĞİ</p>
              <p class="text-[#00ff88] font-bold text-lg">{{ status.buy_threshold }}%</p>
            </div>
            <div class="bg-red-500/5 border border-red-500/10 rounded-lg p-3">
              <p class="text-red-400/40 text-xs tracking-widest">SATIŞ EŞİĞİ</p>
              <p class="text-red-400 font-bold text-lg">+{{ status.sell_threshold }}%</p>
            </div>
          </div>
        </div>

        <!-- Kontrol -->
        <div class="border border-[#00ff88]/20 rounded-lg p-5">
          <p class="text-[#00ff88]/50 text-xs tracking-widest mb-4">BOT KONTROLÜ</p>
          <div class="flex gap-3 mb-4">
            <button @click="startBot" :disabled="status.is_running"
              class="flex-1 py-3 rounded-lg font-bold tracking-widest text-sm transition-all
              bg-[#00ff88]/10 border border-[#00ff88]/30 text-[#00ff88]
              hover:bg-[#00ff88] hover:text-black
              disabled:opacity-20 disabled:cursor-not-allowed">
              ▶ BAŞLAT
            </button>
            <button @click="stopBot" :disabled="!status.is_running"
              class="flex-1 py-3 rounded-lg font-bold tracking-widest text-sm transition-all
              bg-red-500/10 border border-red-500/30 text-red-400
              hover:bg-red-500 hover:text-white
              disabled:opacity-20 disabled:cursor-not-allowed">
              ■ DURDUR
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="bg-gray-800/50 border border-gray-700/50 rounded-lg p-3">
              <p class="text-gray-500 text-xs tracking-widest">BAKİYE</p>
              <p class="text-white font-bold">${{ balance.toFixed(2) }} USDT</p>
            </div>
            <div class="bg-gray-800/50 border border-gray-700/50 rounded-lg p-3">
              <p class="text-gray-500 text-xs tracking-widest">MOD</p>
              <p :class="status.live_trading ? 'text-red-400' : 'text-blue-400'" class="font-bold">
                {{ status.live_trading ? '🔴 GERÇEK' : '🔵 SİMÜLASYON' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Son İşlemler -->
      <div class="border border-[#00ff88]/20 rounded-lg overflow-hidden">
        <div class="px-5 py-3 border-b border-[#00ff88]/10 flex items-center justify-between">
          <p class="text-[#00ff88]/50 text-xs tracking-widest">SON İŞLEMLER</p>
          <router-link to="/history" class="text-[#00ff88]/30 hover:text-[#00ff88] text-xs tracking-widest transition">
            TÜMÜNÜ GÖR →
          </router-link>
        </div>
        <div v-if="!status.trade_history?.length" class="text-center text-[#00ff88]/20 py-10 text-xs tracking-widest">
          HENÜZ İŞLEM YOK
        </div>
        <div v-else>
          <div v-for="(trade, i) in [...status.trade_history].reverse().slice(0, 5)" :key="i"
            class="flex items-center justify-between px-5 py-3 border-t border-[#00ff88]/10 hover:bg-[#00ff88]/5 transition">
            <div class="flex items-center gap-3">
              <span :class="trade.side === 'Buy' ? 'bg-[#00ff88]/20 text-[#00ff88] border-[#00ff88]/30' : 'bg-red-500/20 text-red-400 border-red-500/30'"
                class="px-2 py-0.5 rounded text-xs font-bold border tracking-widest">
                {{ trade.side.toUpperCase() }}
              </span>
              <span class="text-gray-500 text-xs tracking-widest">{{ trade.reason }}</span>
            </div>
            <div class="flex items-center gap-8">
              <span v-if="trade.side === 'Sell'"
                :class="trade.pnl >= 0 ? 'text-[#00ff88]' : 'text-red-400'"
                class="text-sm font-bold">
                {{ trade.pnl >= 0 ? '+' : '' }}${{ trade.pnl?.toFixed(4) }}
              </span>
              <div class="text-right">
                <p class="text-white font-bold text-sm">${{ trade.price?.toLocaleString() }}</p>
                <p class="text-gray-600 text-xs">{{ new Date(trade.timestamp).toLocaleTimeString('tr-TR') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { apiFetch, logout } from '../api.js'

const status = ref({
  is_running: false, symbol: 'BTCUSDT', current_price: 0, entry_price: null,
  in_position: false, daily_trades: 0, max_daily_trades: 10, trade_amount: 10,
  buy_threshold: -1.0, sell_threshold: 1.0, live_trading: false,
  total_pnl: 0, total_commission: 0, trade_history: []
})
const balance = ref(0)

const fetchBalance = async () => {
  try {
    const res = await apiFetch('/api/balance')
    if (res) {
      const data = await res.json()
      balance.value = data.balance
    }
  } catch (e) { console.error('Bakiye hatası:', e) }
}

const priceChange = computed(() => {
  if (!status.value.entry_price || !status.value.current_price) return 0
  return (((status.value.current_price - status.value.entry_price) / status.value.entry_price) * 100).toFixed(3)
})

let interval = null

const fetchStatus = async () => {
  try {
    const res = await apiFetch('/api/status')
    if (res) status.value = await res.json()
  } catch (e) { console.error('API bağlantı hatası:', e) }
}

const startBot = async () => { await apiFetch('/api/start', { method: 'POST' }); fetchStatus() }
const stopBot = async () => { await apiFetch('/api/stop', { method: 'POST' }); fetchStatus() }

onMounted(() => { fetchStatus(); fetchBalance(); interval = setInterval(fetchStatus, 2000) })
onUnmounted(() => clearInterval(interval))
</script>