<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-xl w-full max-w-sm">
      <h1 class="text-white text-2xl font-bold mb-6 text-center">🤖 Trading Bot</h1>
      
      <div v-if="error" class="bg-red-500/20 text-red-400 text-sm p-3 rounded-lg mb-4">
        {{ error }}
      </div>

      <div class="mb-4">
        <label class="text-gray-400 text-sm mb-1 block">Kullanıcı Adı</label>
        <input
          v-model="username"
          type="text"
          class="w-full bg-gray-700 text-white p-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="handleLogin"
        />
      </div>

      <div class="mb-6">
        <label class="text-gray-400 text-sm mb-1 block">Şifre</label>
        <input
          v-model="password"
          type="password"
          class="w-full bg-gray-700 text-white p-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="handleLogin"
        />
      </div>

      <button
        @click="handleLogin"
        :disabled="loading"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold p-3 rounded-lg transition disabled:opacity-50"
      >
        {{ loading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Hata')
    localStorage.setItem('token', data.token)
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>