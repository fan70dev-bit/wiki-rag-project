<template>
  <main class="max-w-4xl mx-auto pt-10 px-6 pb-20">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-3">{{ t('title') }}</h1>
    </div>

    <div class="bg-white p-4 rounded-2xl shadow-lg border border-gray-100 mb-8">
      <div class="flex gap-4 mb-4 justify-center">
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="radio" v-model="searchMode" value="title" class="text-blue-600 w-4 h-4">
          <span :class="searchMode === 'title' ? 'font-bold text-blue-600' : 'text-gray-500'">{{ t('modeExact') }}</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="radio" v-model="searchMode" value="vector" class="text-blue-600 w-4 h-4">
          <span :class="searchMode === 'vector' ? 'font-bold text-blue-600' : 'text-gray-500'">{{ t('modeSemantic') }}</span>
        </label>
      </div>
      <div class="flex gap-3">
        <input v-model="query" @keyup.enter="doSearch(1)" type="text" :placeholder="t('placeholder')" class="flex-1 p-3 rounded-xl bg-gray-50 border focus:ring-2 focus:ring-blue-500 text-lg transition">
        <button @click="doSearch(1)" :disabled="loading" class="bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 transition font-bold disabled:bg-gray-400">
          {{ loading ? t('searching') : t('searchBtn') }}
        </button>
      </div>
    </div>

    <div v-if="articles.length > 0">
      <div class="mb-4 text-sm text-gray-500 px-2">{{ t('found') }} <span class="font-bold text-blue-600 text-base">{{ totalResults }}</span> {{ t('results') }}</div>
      <div class="space-y-6">
        <div v-for="article in articles" :key="article.id" class="bg-white p-6 rounded-2xl shadow-sm border hover:shadow-md transition">
          <div class="flex justify-between items-start mb-3">
            <h2 class="text-2xl font-bold text-gray-800">{{ article.title }}</h2>
            <div class="flex gap-2">
              <span class="text-xs px-3 py-1 rounded-full font-semibold border bg-green-50 text-green-700">匹配度: {{ article.match_rate }}</span>
            </div>
          </div>
          <p class="text-gray-600 leading-relaxed mb-4">{{ article.summary }}...</p>
          
          <router-link :to="`/article/${article.id}`" class="inline-block text-sm text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-5 py-2.5 rounded-lg font-bold transition">
            {{ t('readFull') }} &rarr;
          </router-link>
        </div>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center items-center gap-2 mt-10">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1 || loading" class="px-3 py-2 rounded border">&laquo;</button>
        <button v-for="p in displayedPages" :key="p" @click="changePage(p)" :class="['w-10 h-10 rounded border', currentPage === p ? 'bg-blue-600 text-white' : 'bg-white hover:bg-gray-50']">{{ p }}</button>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages || loading" class="px-3 py-2 rounded border">&raquo;</button>
      </div>
    </div>

    <div v-else-if="searched && articles.length === 0" class="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm mt-8">
      <div class="text-6xl mb-4">📭</div>
      <p class="text-xl text-gray-500 font-medium">{{ t('noResult') }}</p>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const API_BASE = import.meta.env.VITE_API_BASE

const query = ref('')
const searchMode = ref('vector')
const articles = ref([])
const loading = ref(false)
const searched = ref(false) // 🚀 新增搜索状态标记
const currentPage = ref(1)
const pageSize = 10
const totalResults = ref(0)
const totalPages = computed(() => Math.ceil(totalResults.value / pageSize))

const displayedPages = computed(() => {
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  let pages = []
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const doSearch = async (page = 1) => {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = false
  currentPage.value = page
  
  console.log('🔗 准备发起请求，API地址是:', API_BASE) // 调试日志

  try {
    const res = await axios.get(`${API_BASE}/api/search`, {
      params: { q: query.value, mode: searchMode.value, page: currentPage.value, size: pageSize }
    })
    
    console.log('✅ 收到后端响应:', res.data) // 调试日志

    if (res.data.status === 'success') {
      articles.value = res.data.data
      totalResults.value = res.data.total
    }
  } catch (error) {
    console.error('❌ 请求彻底失败:', error)
    // 🚀 如果网络出问题，直接弹窗警告
    alert(`网络请求失败！\n1. 请检查虚拟机后端是否正在运行\n2. 请确认 .env 里的 VITE_API_BASE 是否正确\n当前地址: ${API_BASE}`)
  } finally {
    loading.value = false
    searched.value = true // 标记请求结束
  }
}

const changePage = (page) => { if (page >= 1 && page <= totalPages.value) doSearch(page) }
</script>