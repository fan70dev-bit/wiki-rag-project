<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-800 pb-20">
    <header class="bg-white shadow-sm p-4 flex justify-between items-center sticky top-0 z-50">
      <div class="text-xl font-bold text-indigo-600">Wiki RAG Pro</div>
      <button @click="toggleLang" class="bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-100 transition font-medium text-sm border border-indigo-100">
        {{ locale === 'zh' ? '🌐 日本語版インターフェース' : '🌐 切换至中文' }}
      </button>
    </header>

    <main class="max-w-4xl mx-auto pt-10 px-6">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-3">
          {{ t('title') }}
        </h1>
      </div>

      <div class="bg-white p-4 rounded-2xl shadow-lg border border-gray-100 mb-8">
        <div class="flex gap-4 mb-4 justify-center">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" v-model="searchMode" value="title" class="text-blue-600 focus:ring-blue-500 w-4 h-4">
            <span :class="searchMode === 'title' ? 'font-bold text-blue-600' : 'text-gray-500'">{{ t('modeExact') }} (SQLite)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" v-model="searchMode" value="vector" class="text-blue-600 focus:ring-blue-500 w-4 h-4">
            <span :class="searchMode === 'vector' ? 'font-bold text-blue-600' : 'text-gray-500'">{{ t('modeSemantic') }} (ChromaDB)</span>
          </label>
        </div>

        <div class="flex gap-3">
          <input v-model="query" @keyup.enter="doSearch(1)" type="text" :placeholder="t('placeholder')" 
                 class="flex-1 p-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg transition">
          <button @click="doSearch(1)" :disabled="loading" 
                  class="bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 transition font-bold disabled:bg-gray-400">
            {{ loading ? t('searching') : t('searchBtn') }}
          </button>
        </div>
      </div>

      <div v-if="articles.length > 0">
        
        <div class="mb-4 text-sm text-gray-500 px-2">
          {{ t('found') }} <span class="font-bold text-blue-600 text-base">{{ totalResults }}</span> {{ t('results') }}
        </div>

        <div class="space-y-5">
          <div v-for="(article, index) in articles" :key="index" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
            <div class="flex justify-between items-start mb-2">
              <h2 class="text-2xl font-bold text-gray-800">{{ article.title }}</h2>
              <div class="flex gap-2">
                <span class="text-xs px-3 py-1 rounded-full font-semibold border bg-green-50 text-green-700 border-green-200">
                  匹配度: {{ article.match_rate }}
                </span>
                <span class="text-xs px-3 py-1 rounded-full font-semibold border"
                      :class="searchMode === 'title' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-purple-50 text-purple-700 border-purple-200'">
                  ID: {{ article.id }}
                </span>
              </div>
            </div>
            
            <p class="text-gray-600 leading-relaxed mb-4" v-if="!article.fullText">{{ article.summary }}...</p>
            
            <div v-if="article.fullText" class="bg-gray-50 p-5 rounded-xl text-gray-700 leading-loose mb-4 border border-gray-200 max-h-96 overflow-y-auto whitespace-pre-wrap text-sm">
              {{ article.fullText }}
            </div>

            <div class="flex gap-3">
              <button @click="loadFullText(article)" :disabled="article.loadingFull"
                      class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition flex items-center gap-2">
                <span v-if="article.loadingFull" class="animate-spin">⏳</span>
                <span>{{ article.fullText ? t('collapseText') : t('readFull') }}</span>
              </button>
              <button class="text-sm text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-4 py-2 rounded-lg font-medium transition cursor-not-allowed opacity-50">
                {{ t('aiSummaryPending') }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="totalPages > 1" class="flex justify-center items-center gap-2 mt-10">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1 || loading" 
                  class="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30 font-medium bg-white transition">
            &laquo;
          </button>
          
          <div class="flex gap-1">
            <button v-for="p in displayedPages" :key="p" @click="changePage(p)" :disabled="loading"
                    :class="['w-10 h-10 rounded-lg font-bold transition border', 
                             currentPage === p ? 'bg-blue-600 text-white border-blue-600 shadow-md' : 'bg-white text-gray-600 hover:bg-gray-50 border-gray-200']">
              {{ p }}
            </button>
          </div>

          <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages || loading" 
                  class="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30 font-medium bg-white transition">
            &raquo;
          </button>

          <div class="ml-4 flex items-center gap-2 text-sm text-gray-500">
            <span>{{ t('jumpTo') }}</span>
            <input type="number" v-model.number="jumpPage" @keyup.enter="changePage(jumpPage)" 
                   class="w-14 p-1.5 border border-gray-300 rounded-lg text-center focus:ring-2 focus:ring-blue-500 focus:outline-none">
            <span>{{ t('pageUnit') }}</span>
          </div>
        </div>

      </div>

      <div v-else-if="searched && articles.length === 0" class="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm mt-8">
        <div class="text-6xl mb-4">📭</div>
        <p class="text-xl text-gray-500 font-medium">{{ t('noResult') }}</p>
        <p class="text-sm text-gray-400 mt-2">试试降低标准，或者换个引擎搜索</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t, locale } = useI18n()

// ⚠️ 你的 CentOS 虚拟机 IP
const API_BASE = 'http://192.168.244.131:8000'

// 状态
const query = ref('')
const searchMode = ref('title') // 默认精准搜索
const articles = ref([])
const loading = ref(false)
const searched = ref(false)

// 分页状态
const currentPage = ref(1)
const pageSize = 10
const totalResults = ref(0)
const jumpPage = ref(1)

// 计算总页数
const totalPages = computed(() => Math.ceil(totalResults.value / pageSize))

// 计算显示的页码（滑动窗口，最多显示5个页码按钮）
const displayedPages = computed(() => {
  let pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  
  if (end - start < 4) {
    start = Math.max(1, end - 4)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const toggleLang = () => {
  locale.value = locale.value === 'zh' ? 'ja' : 'zh'
}

const doSearch = async (page = 1) => {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = false
  currentPage.value = page
  jumpPage.value = page
  
  try {
    const res = await axios.get(`${API_BASE}/api/search`, {
      params: { q: query.value, mode: searchMode.value, page: currentPage.value, size: pageSize }
    })
    
    if (res.data.status === 'success') {
      articles.value = res.data.data.map(a => ({ ...a, fullText: null, loadingFull: false }))
      totalResults.value = res.data.total // 读取后端返回的真实总数
    }
  } catch (error) {
    alert(locale.value === 'zh' ? '网络错误，请检查后端 API。' : 'ネットワークエラー。')
  } finally {
    loading.value = false
    searched.value = true
  }
}

const changePage = (page) => {
  // 拦截非法页码
  if (page < 1 || page > totalPages.value) return
  doSearch(page)
}

const loadFullText = async (article) => {
  if (article.fullText) {
    article.fullText = null
    return
  }
  
  article.loadingFull = true
  try {
    const res = await axios.get(`${API_BASE}/api/search/detail/${article.id}`)
    if (res.data.status === 'success') {
      article.fullText = res.data.data.full_text
    }
  } catch (error) {
    alert(locale.value === 'zh' ? '获取原文失败' : '詳細データの取得に失敗しました')
  } finally {
    article.loadingFull = false
  }
}
</script>