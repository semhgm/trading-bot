<template>
  <div class="min-h-screen bg-[#0a0a0f] text-white font-mono p-6">
    <div class="flex items-center gap-4 mb-8">
      <router-link to="/" class="text-[#00ff88] hover:text-white transition text-xs tracking-widest">← DASHBOARD</router-link>
      <span class="text-[#00ff88]/30">//</span>
      <h1 class="text-sm font-bold tracking-widest text-[#00ff88]">AYARLAR</h1>
    </div>

    <div class="max-w-xl space-y-3">
      <!-- Symbol -->
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-5">
        <label class="text-[#00ff88]/50 text-xs tracking-widest block mb-3">VARLIK (SYMBOL)</label>
        <select v-model="form.symbol" class="w-full bg-[#0a0a0f] border border-[#00ff88]/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00ff88] transition">
          <option>BTCUSDT</option>
          <option>ETHUSDT</option>
          <option>SOLUSDT</option>
          <option>XAUTUSDT</option>
        </select>
      </div>

      <!-- Eşikler -->
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-5">
        <label class="text-[#00ff88]/50 text-xs tracking-widest block mb-4">EŞİK DEĞERLERİ</label>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-[#00ff88]/40 text-xs block mb-2">ALIŞ EŞİĞİ (%)</label>
            <input v-model.number="form.buy_threshold" type="number" step="0.1"
              class="w-full bg-[#0a0a0f] border border-[#00ff88]/30 rounded-lg px-4 py-3 text-[#00ff88] focus:outline-none focus:border-[#00ff88] transition" />
            <p class="text-[#00ff88]/20 text-xs mt-1">Fiyat bu kadar düşünce al</p>
          </div>
          <div>
            <label class="text-red-400/40 text-xs block mb-2">SATIŞ EŞİĞİ (%)</label>
            <input v-model.number="form.sell_threshold" type="number" step="0.1"
              class="w-full bg-[#0a0a0f] border border-red-500/30 rounded-lg px-4 py-3 text-red-400 focus:outline-none focus:border-red-400 transition" />
            <p class="text-red-400/20 text-xs mt-1">Fiyat bu kadar artınca sat</p>
          </div>
        </div>
      </div>

      <!-- Stop Loss -->
      <div class="border border-yellow-500/20 bg-yellow-500/5 rounded-lg p-5">
        <label class="text-yellow-500/50 text-xs tracking-widest block mb-3">STOP LOSS (%)</label>
        <input v-model.number="form.stop_loss" type="number" step="0.1"
          class="w-full bg-[#0a0a0f] border border-yellow-500/30 rounded-lg px-4 py-3 text-yellow-400 focus:outline-none focus:border-yellow-400 transition" />
        <p class="text-yellow-500/20 text-xs mt-1">Fiyat bu kadar düşerse pozisyonu kapat</p>
      </div>

      <!-- İşlem Miktarı -->
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-5">
        <label class="text-[#00ff88]/50 text-xs tracking-widest block mb-3">İŞLEM MİKTARI (USDT)</label>
        <input v-model.number="form.trade_amount" type="number" step="1"
          class="w-full bg-[#0a0a0f] border border-[#00ff88]/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00ff88] transition" />
      </div>

      <!-- Max İşlem -->
      <div class="border border-[#00ff88]/20 bg-[#00ff88]/5 rounded-lg p-5">
        <label class="text-[#00ff88]/50 text-xs tracking-widest block mb-3">GÜNLÜK MAX İŞLEM</label>
        <input v-model.number="form.max_daily_trades" type="number" step="1"
          class="w-full bg-[#0a0a0f] border border-[#00ff88]/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00ff88] transition" />
      </div>

      <!-- Live Toggle -->
      <div class="border border-red-500/20 bg-red-500/5 rounded-lg p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white font-bold tracking-widest text-sm">GERÇEK İŞLEM MODU</p>
            <p class="text-red-400/40 text-xs mt-1">Aktif edilirse gerçek para ile işlem yapılır</p>
          </div>
          <button @click="form.live_trading = !form.live_trading"
            :class="form.live_trading ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-gray-700'"
            class="w-14 h-7 rounded-full transition-all relative">
            <span :class="form.live_trading ? 'translate-x-7' : 'translate-x-1'"
              class="absolute top-1 w-5 h-5 bg-white rounded-full transition-transform block shadow-lg"></span>
          </button>
        </div>
        <div v-if="form.live_trading" class="mt-3 border border-red-500/30 rounded-lg p-3 text-red-300 text-xs tracking-widest">
          ⚠ DİKKAT: GERÇEK PARA İLE İŞLEM YAPILACAK
        </div>
      </div>

      <!-- Kaydet -->
      <button @click="saveConfig"
        :class="saved ? 'bg-[#00ff88] text-black' : 'bg-[#00ff88]/10 border border-[#00ff88]/30 text-[#00ff88] hover:bg-[#00ff88] hover:text-black'"
        class="w-full py-4 rounded-lg font-bold tracking-widest text-sm transition-all">
        {{ saved ? '✓ KAYDEDİLDİ' : 'KAYDET' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../api.js'

const saved = ref(false)
const form = ref({
  symbol: 'BTCUSDT', buy_threshold: -1.0, sell_threshold: 1.0,
  stop_loss: -5.0, trade_amount: 10, max_daily_trades: 10, live_trading: false,
})

const fetchConfig = async () => {
  const res = await apiFetch('/api/status')
  if (!res) return
  const data = await res.json()
  Object.assign(form.value, {
    symbol: data.symbol, buy_threshold: data.buy_threshold,
    sell_threshold: data.sell_threshold, stop_loss: data.stop_loss,
    trade_amount: data.trade_amount, max_daily_trades: data.max_daily_trades,
    live_trading: data.live_trading
  })
}

const saveConfig = async () => {
  await apiFetch('/api/config', { method: 'POST', body: JSON.stringify(form.value) })
  saved.value = true
  setTimeout(() => saved.value = false, 2000)
}

onMounted(fetchConfig)
</script>