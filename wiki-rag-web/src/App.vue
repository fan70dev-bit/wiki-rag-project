<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-800">
    <header class="bg-white shadow-sm p-4 flex justify-between items-center sticky top-0 z-50">
      <router-link to="/" class="text-xl font-bold text-indigo-600 hover:text-indigo-800 transition">
        Wiki RAG Pro
      </router-link>
      <button @click="toggleLang" class="bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-100 transition font-medium text-sm border border-indigo-100">
        {{ locale === 'zh' ? '🌐 日本語版' : '🌐 切换至中文' }}
      </button>
    </header>

    <router-view v-slot="{ Component }">
      <keep-alive include="Home">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()
const toggleLang = () => { locale.value = locale.value === 'zh' ? 'ja' : 'zh' }
</script>