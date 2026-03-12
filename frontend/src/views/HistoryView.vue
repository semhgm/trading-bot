<template>
  <div class="min-h-screen bg-[#0a0a0f] text-white p-6 font-mono">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-8">
      <router-link to="/" class="text-[#00ff88] hover:text-white transition text-sm tracking-widest">← DASHBOARD</router-link>
      <h1 class="text-xl font-bold tracking-widest text-[#00ff88]">// GEÇMİŞ</h1>
    </div>

    <!-- Özet Kartlar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-4">
        <p class="text-[#00ff88]/60 text-xs tracking-widest mb-1">TOPLAM TRADE</p>
        <p class="text-2xl font-bold text-[#00ff88]">{{ trades.length }}</p>
      </div>
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-4">
        <p class="text-[#00ff88]/60 text-xs tracking-widest mb-1">NET P&L</p>
        <p :class="totalPnl >= 0 ? 'text-[#00ff88]' : 'text-red-400'" class="text-2xl font-bold">
          {{ totalPnl >= 0 ? '+' : '' }}${{ totalPnl.toFixed(4) }}
        </p>
      </div>
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-4">
        <p class="text-[#00ff88]/60 text-xs tracking-widest mb-1">KOMİSYON</p>
        <p class="text-2xl font-bold text-yellow-400">${{ totalCommission.toFixed(4) }}</p>
      </div>
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-4">
        <p class="text-[#00ff88]/60 text-xs tracking-widest mb-1">BAŞARILI</p>
        <p class="text-2xl font-bold text-blue-400">{{ winRate }}%</p>
      </div>
    </div>

    <!-- Tab: Trades / Sessions -->
    <div class="flex gap-1 mb-6">
      <button @click="activeTab = 'trades'"
        :class="activeTab === 'trades' ? 'bg-[#00ff88] text-black' : 'text-[#00ff88]/60 border border-[#00ff88]/20'"
        class="px-6 py-2 text-xs tracking-widest rounded transition font-bold">
        TRADE GEÇMİŞİ
      </button>
      <button @click="activeTab = 'sessions'"
        :class="activeTab === 'sessions' ? 'bg-[#00ff88] text-black' : 'text-[#00ff88]/60 border border-[#00ff88]/20'"
        class="px-6 py-2 text-xs tracking-widest rounded transition font-bold">
        OTURUMLAR
      </button>
    </div>

    <!-- Trades Tablosu -->
    <div v-if="activeTab === 'trades'" class="border border-[#00ff88]/20 rounded-lg overflow-hidden">
      <div class="grid grid-cols-6 gap-4 px-4 py-3 bg-[#00ff88]/10 text-[#00ff88]/60 text-xs tracking-widest">
        <span>ZAMAN</span>
        <span>COIN</span>
        <span>İŞLEM</span>
        <span>FİYAT</span>
        <span>P&L</span>
        <span>MOD</span>
      </div>
      <div v-if="trades.length === 0" class="text-center text-[#00ff88]/30 py-12 text-sm tracking-widest">
        HENÜZ KAYIT YOK
      </div>
      <div v-for="trade in trades" :key="trade.id"
        class="grid grid-cols-6 gap-4 px-4 py-3 border-t border-[#00ff88]/10 hover:bg-[#00ff88]/5 transition text-sm">
        <span class="text-gray-500 text-xs">{{ formatDate(trade.created_at) }}</span>
        <span class="text-white font-bold">{{ trade.symbol }}</span>
        <span :class="trade.side === 'Buy' ? 'text-[#00ff88]' : 'text-red-400'" class="font-bold tracking-widest">
          {{ trade.side.toUpperCase() }}
        </span>
        <span class="text-white">${{ trade.price?.toLocaleString() }}</span>
        <span :class="trade.pnl >= 0 ? 'text-[#00ff88]' : 'text-red-400'" class="font-bold">
          {{ trade.pnl !== 0 ? (trade.pnl >= 0 ? '+' : '') + '$' + trade.pnl?.toFixed(4) : '—' }}
        </span>
        <span :class="trade.mode === 'live' ? 'text-red-400' : 'text-blue-400'" class="text-xs tracking-widest">
          {{ trade.mode?.toUpperCase() }}
        </span>
      </div>
    </div>

    <!-- Sessions Tablosu -->
    <div v-if="activeTab === 'sessions'" class="border border-[#00ff88]/20 rounded-lg overflow-hidden">
      <div class="grid grid-cols-5 gap-4 px-4 py-3 bg-[#00ff88]/10 text-[#00ff88]/60 text-xs tracking-widest">
        <span>BAŞLANGIÇ</span>
        <span>BİTİŞ</span>
        <span>COIN</span>
        <span>TRADE</span>
        <span>P&L</span>
      </div>
      <div v-if="sessions.length === 0" class="text-center text-[#00ff88]/30 py-12 text-sm tracking-widest">
        HENÜZ KAYIT YOK
      </div>
      <div v-for="session in sessions" :key="session.id"
        class="grid grid-cols-5 gap-4 px-4 py-3 border-t border-[#00ff88]/10 hover:bg-[#00ff88]/5 transition text-sm">
        <span class="text-gray-500 text-xs">{{ formatDate(session.started_at) }}</span>
        <span class="text-gray-500 text-xs">{{ session.stopped_at ? formatDate(session.stopped_at) : '🟢 Aktif' }}</span>
        <span class="text-white font-bold">{{ session.symbol }}</span>
        <span class="text-blue-400 font-bold">{{ session.total_trades }}</span>
        <span :class="session.total_pnl >= 0 ? 'text-[#00ff88]' : 'text-red-400'" class="font-bold">
          {{ session.total_pnl >= 0 ? '+' : '' }}${{ session.total_pnl?.toFixed(4) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../api.js'

const trades = ref([])
const sessions = ref([])
const activeTab = ref('trades')

const totalPnl = computed(() => trades.value.reduce((sum, t) => sum + (t.pnl || 0), 0))
const totalCommission = computed(() => trades.value.reduce((sum, t) => sum + (t.commission || 0), 0))
const winRate = computed(() => {
  const sells = trades.value.filter(t => t.side === 'Sell')
  if (!sells.length) return 0
  return Math.round(sells.filter(t => t.pnl > 0).length / sells.length * 100)
})

const formatDate = (str) => {
  if (!str) return '—'
  return new Date(str).toLocaleString('tr-TR', { dateStyle: 'short', timeStyle: 'short' })
}

onMounted(async () => {
  const [tradesRes, sessionsRes] = await Promise.all([
    apiFetch('/api/trades'),
    apiFetch('/api/sessions')
  ])
  if (tradesRes) trades.value = (await tradesRes.json()).trades
  if (sessionsRes) sessions.value = (await sessionsRes.json()).sessions
})
</script>