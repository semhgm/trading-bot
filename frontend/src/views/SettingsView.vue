<template>
  <div class="min-h-screen bg-gray-950 text-white p-6">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-8">
      <router-link to="/" class="text-gray-400 hover:text-white transition">← Dashboard</router-link>
      <h1 class="text-2xl font-bold">Ayarlar</h1>
    </div>

    <!-- Config Form -->
    <div class="max-w-xl space-y-4">

      <!-- Symbol -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <label class="text-gray-400 text-sm block mb-2">Varlık (Symbol)</label>
        <select v-model="form.symbol" class="w-full bg-gray-800 rounded-lg px-4 py-3 text-white border border-gray-700 focus:outline-none">
          <option>BTCUSDT</option>
          <option>ETHUSDT</option>
          <option>SOLUSDT</option>
          <option>XAUTUSDT</option>
        </select>
      </div>

      <!-- Alış / Satış Eşiği -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <label class="text-gray-400 text-sm block mb-4">Eşik Değerleri</label>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-gray-500 text-xs block mb-1">Alış Eşiği (%)</label>
            <input v-model.number="form.buy_threshold" type="number" step="0.1"
              class="w-full bg-gray-800 rounded-lg px-4 py-3 text-green-400 border border-gray-700 focus:outline-none" />
            <p class="text-gray-600 text-xs mt-1">Fiyat bu kadar düşünce al</p>
          </div>
          <div>
            <label class="text-gray-500 text-xs block mb-1">Satış Eşiği (%)</label>
            <input v-model.number="form.sell_threshold" type="number" step="0.1"
              class="w-full bg-gray-800 rounded-lg px-4 py-3 text-red-400 border border-gray-700 focus:outline-none" />
            <p class="text-gray-600 text-xs mt-1">Fiyat bu kadar artınca sat</p>
          </div>
        </div>
      </div>

      <!-- Stop Loss -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <label class="text-gray-400 text-sm block mb-2">Stop Loss (%)</label>
        <input v-model.number="form.stop_loss" type="number" step="0.1"
          class="w-full bg-gray-800 rounded-lg px-4 py-3 text-yellow-400 border border-gray-700 focus:outline-none" />
        <p class="text-gray-600 text-xs mt-1">Fiyat bu kadar düşerse pozisyonu kapat</p>
      </div>

      <!-- İşlem Miktarı -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <label class="text-gray-400 text-sm block mb-2">İşlem Miktarı (USDT)</label>
        <input v-model.number="form.trade_amount" type="number" step="1"
          class="w-full bg-gray-800 rounded-lg px-4 py-3 text-white border border-gray-700 focus:outline-none" />
        <p class="text-gray-600 text-xs mt-1">Her işlemde kullanılacak USDT miktarı</p>
      </div>

      <!-- Günlük Max İşlem -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <label class="text-gray-400 text-sm block mb-2">Günlük Max İşlem</label>
        <input v-model.number="form.max_daily_trades" type="number" step="1"
          class="w-full bg-gray-800 rounded-lg px-4 py-3 text-white border border-gray-700 focus:outline-none" />
      </div>

      <!-- Live Trading Toggle -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white font-medium">Gerçek İşlem Modu</p>
            <p class="text-gray-500 text-sm mt-1">Aktif edilirse gerçek para ile işlem yapılır</p>
          </div>
          <button @click="form.live_trading = !form.live_trading"
            :class="form.live_trading ? 'bg-red-600' : 'bg-gray-700'"
            class="w-14 h-7 rounded-full transition relative">
            <span :class="form.live_trading ? 'translate-x-7' : 'translate-x-1'"
              class="absolute top-1 w-5 h-5 bg-white rounded-full transition-transform block"></span>
          </button>
        </div>
        <div v-if="form.live_trading" class="mt-3 bg-red-900 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
          ⚠️ Dikkat: Gerçek para ile işlem yapılacak!
        </div>
      </div>

      <!-- Kaydet -->
      <button @click="saveConfig"
        class="w-full bg-blue-600 hover:bg-blue-500 rounded-xl py-4 font-semibold text-lg transition">
        {{ saved ? '✓ Kaydedildi' : 'Kaydet' }}
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const saved = ref(false)
const form = ref({
  symbol: 'BTCUSDT',
  buy_threshold: -1.0,
  sell_threshold: 1.0,
  stop_loss: -5.0,
  trade_amount: 10,
  max_daily_trades: 10,
  live_trading: false,
})

const fetchConfig = async () => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/api/status`)

  const data = await res.json()
  form.value.symbol = data.symbol
  form.value.buy_threshold = data.buy_threshold
  form.value.sell_threshold = data.sell_threshold
  form.value.stop_loss = data.stop_loss
  form.value.trade_amount = data.trade_amount
  form.value.max_daily_trades = data.max_daily_trades
  form.value.live_trading = data.live_trading
}

const saveConfig = async () => {
  await fetch(`${import.meta.env.VITE_API_URL}/api/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  })
  saved.value = true
  setTimeout(() => saved.value = false, 2000)
}

onMounted(fetchConfig)
</script>