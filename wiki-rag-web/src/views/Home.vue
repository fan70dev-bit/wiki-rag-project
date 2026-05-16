<template>
  <main class="max-w-4xl mx-auto pt-16 px-6 pb-24">
    <div class="text-center mb-12">
      <h1 class="text-5xl font-black tracking-tight text-slate-900 mb-4">
        {{ t('title') }}
      </h1>
      <p class="text-slate-400 font-medium">基于分布式 Kafka 与双引擎混合索引的智能知识库</p>
    </div>

    <div class="bg-white p-2 rounded-3xl shadow-2xl shadow-slate-200 border border-slate-100 mb-10 flex flex-col sm:flex-row gap-2">
      <div class="flex-1 flex items-center px-4 gap-3">
        <select v-model="searchMode" class="bg-transparent text-sm font-bold text-indigo-600 focus:outline-none cursor-pointer">
          <option value="title">精准模式 (SQLite)</option>
          <option value="vector">语义模式 (ChromaDB)</option>
        </select>
        <div class="w-px h-6 bg-slate-200"></div>
        <input v-model="query" @keyup.enter="doSearch(1)" type="text" :placeholder="t('placeholder')" 
               class="flex-1 py-4 bg-transparent text-slate-800 placeholder-slate-400 focus:outline-none text-lg">
      </div>
      <button @click="doSearch(1)" :disabled="loading" 
              class="bg-indigo-600 text-white px-10 py-4 rounded-2xl hover:bg-indigo-700 transition-all font-bold disabled:bg-slate-300">
        {{ loading ? '搜索中...' : '深度搜索' }}
      </button>
    </div>

    <div v-if="articles.length > 0" class="space-y-6">
      
      <div class="flex justify-between items-center px-2 py-1 text-sm text-slate-400 font-medium border-b border-slate-100 pb-3">
        <div>
          {{ t('found') }} <span class="font-extrabold text-slate-800">{{ totalResults }}</span> {{ t('results') }}
        </div>
        <div class="flex items-center gap-1.5 bg-slate-100/80 px-3 py-1.5 rounded-xl border border-slate-200/40 text-xs font-bold text-slate-600 shadow-sm">
          <span class="flex h-2 w-2 relative">
            <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          ⏱️ 引擎响应耗时: <span class="text-indigo-600 font-extrabold">{{ searchTime }}</span> ms
        </div>
      </div>

      <div v-for="article in articles" :key="article.id" class="bg-white p-8 rounded-3xl border border-slate-100 hover:shadow-xl transition-all group">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">{{ article.title }}</h2>
          <span class="text-xs font-bold px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full border border-emerald-100">匹配度: {{ article.match_rate }}</span>
        </div>
        <p class="text-slate-500 leading-relaxed mb-6 line-clamp-2">{{ article.summary }}</p>
        <router-link :to="`/article/${article.id}`" class="text-indigo-600 font-bold hover:underline">阅读全文 &rarr;</router-link>
      </div>
    </div>

    <div v-else-if="searched && articles.length === 0" class="text-center py-20 bg-white rounded-3xl border border-slate-100 shadow-sm mt-8">
      <div class="text-5xl mb-4 opacity-70">📭</div>
      <p class="text-lg text-slate-400 font-semibold mb-1">{{ t('noResult') }}</p>
      <p class="text-xs text-slate-300">可以尝试更换关键词或切换检索模式</p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const API_BASE = import.meta.env.VITE_API_BASE
const query = ref('')
const searchMode = ref('vector')
const articles = ref([])
const loading = ref(false)
const searched = ref(false)
const totalResults = ref(0)
const searchTime = ref('0.00') // 🚀 新增：记录单次检索延迟状态

const doSearch = async (page = 1) => {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = false

  // 🚀 核心逻辑：捕获发起网络请求前的精准时间戳
  const startTime = performance.now()

  try {
    const res = await axios.get(`${API_BASE}/api/search`, {
      params: { q: query.value, mode: searchMode.value, page, size: 10 }
    })
    articles.value = res.data.data
    totalResults.value = res.data.total
    searched.value = true
  } catch (error) {
    console.error(error)
  } finally {
    // 🚀 核心逻辑：计算请求完成后的网络总时延并保留两位小数
    const endTime = performance.now()
    searchTime.value = (endTime - startTime).toFixed(2)
    loading.value = false
  }
}
</script>