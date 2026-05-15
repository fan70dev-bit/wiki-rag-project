<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <button @click="$router.push('/')" class="mb-6 text-gray-500 hover:text-indigo-600 flex items-center gap-2 font-medium">
      &larr; 返回搜索结果
    </button>

    <div v-if="loading" class="text-center py-20 text-xl text-gray-400 animate-pulse">正在加载原文...</div>
    
    <div v-else-if="article" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="lg:col-span-2 bg-white p-8 rounded-2xl shadow-sm border border-gray-100 relative">
        <h1 class="text-4xl font-bold text-gray-900 mb-8 border-b pb-4">{{ article.title }}</h1>
        <div class="prose prose-lg text-gray-700 leading-loose whitespace-pre-wrap mb-10">
          {{ article.full_text }}
        </div>
        
        <div class="border-t pt-8 mt-8">
          <button @click="generateSummary" :disabled="summarizing" class="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-4 rounded-xl font-bold text-lg hover:shadow-lg transition flex justify-center items-center gap-2 disabled:opacity-70">
            <span v-if="summarizing" class="animate-spin">🌀</span>
            {{ summarizing ? 'AI 正在深度研读全文...' : '✨ 一键生成全文总结' }}
          </button>
          
          <div v-if="summaryResult" class="mt-6 bg-indigo-50 p-6 rounded-xl border border-indigo-100">
            <h3 class="font-bold text-indigo-900 mb-3 text-lg">📝 全文要点速览：</h3>
            <p class="text-gray-800 leading-relaxed whitespace-pre-wrap">{{ summaryResult }}</p>
          </div>
        </div>
      </div>

      <div class="lg:col-span-1">
        <div class="sticky top-24 bg-gray-900 rounded-2xl shadow-xl border border-gray-800 flex flex-col h-[80vh] overflow-hidden">
          
          <div class="p-4 bg-gray-800 border-b border-gray-700 flex items-center gap-3">
            <span class="text-2xl">🤖</span>
            <div>
              <h3 class="font-bold text-white">AI 研读助手</h3>
              <p class="text-xs text-gray-400">将文中不懂的片段发给我，我来帮你分析</p>
            </div>
          </div>

          <div class="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-900">
            <div v-if="chats.length === 0" class="text-center text-gray-500 mt-10 text-sm">
              请在此粘贴文章片段或提出你的疑问...
            </div>
            
            <div v-for="(chat, idx) in chats" :key="idx" :class="chat.role === 'user' ? 'text-right' : 'text-left'">
              <div :class="chat.role === 'user' ? 'inline-block bg-indigo-600 text-white p-3 rounded-l-xl rounded-tr-xl text-sm max-w-[85%] text-left' : 'inline-block bg-gray-700 text-white p-3 rounded-r-xl rounded-tl-xl text-sm max-w-[90%] border border-gray-600'">
                <div class="markdown-body" v-html="marked.parse(chat.content || '')"></div>
              </div>
            </div>
            <div v-if="chatting" class="text-left"><span class="inline-block bg-gray-800 text-gray-400 p-3 rounded-r-xl rounded-tl-xl text-sm animate-pulse">思考中...</span></div>
          </div>

          <div class="p-4 bg-gray-800 border-t border-gray-700">
            <textarea v-model="chatInput" @keyup.enter.exact="sendChat" rows="3" placeholder="例如：分析一下这句‘三军可夺帅也’的意思..." class="w-full bg-gray-900 text-white border border-gray-700 rounded-xl p-3 text-sm focus:ring-1 focus:ring-indigo-500 focus:outline-none resize-none mb-3"></textarea>
            <button @click="sendChat" :disabled="!chatInput.trim() || chatting" class="w-full bg-indigo-600 text-white py-2 rounded-lg font-bold hover:bg-indigo-700 transition disabled:bg-gray-600">
              发送分析请求
            </button>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const route = useRoute()
const API_BASE = import.meta.env.VITE_API_BASE

const article = ref(null)
const loading = ref(true)

const summarizing = ref(false)
const summaryResult = ref('')

const chatInput = ref('')
const chatting = ref(false)
const chats = ref([])

onMounted(async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/search/detail/${route.params.id}`)
    if (res.data.status === 'success') article.value = res.data.data
  } finally {
    loading.value = false
  }
})

/**
 * 🚀 核心流式读取函数封装
 */
const fetchStreamingData = async (queryText, onChunk) => {
  const res = await fetch(`${API_BASE}/api/ai/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: queryText,
      context: article.value.full_text
    })
  })

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value, { stream: true })
    const lines = chunk.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const dataStr = line.replace(/^data: /, '').trim()
        if (dataStr === '[DONE]') continue // 结束信号
        try {
          const data = JSON.parse(dataStr)
          const content = data.choices[0]?.delta?.content
          if (content) onChunk(content) // 把解析出的字传出去
        } catch (e) {
          // 忽略不完整的 JSON 截断错误
        }
      }
    }
  }
}

// 🚀 流式：一键总结功能
const generateSummary = async () => {
  summarizing.value = true
  summaryResult.value = '' // 清空上次的结果
  
  try {
    await fetchStreamingData(
      "请详细总结这篇文章的核心主旨，并以无序列表的方式列出3-5个关键知识点。",
      (chunk) => { summaryResult.value += chunk } // 打字机效果：一点点追加
    )
  } catch (e) {
    summaryResult.value = "生成失败，请检查网络或 API Key。"
  } finally {
    summarizing.value = false
  }
}

// 🚀 流式：侧边栏对话功能
const sendChat = async () => {
  if (!chatInput.value.trim() || chatting.value) return
  
  const userMsg = chatInput.value
  chats.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatting.value = true

  // 先在界面上推入一个空的 AI 回复框，占据位置
  const aiMsgIndex = chats.value.length
  chats.value.push({ role: 'ai', content: '' })

  try {
    await fetchStreamingData(
      `用户提出了一个问题或提供了一个片段：“${userMsg}”。请结合参考文本的内容为其解答。`,
      (chunk) => {
        // 打字机效果：精确定位到刚刚创建的 AI 回复框，不断追加文字
        chats.value[aiMsgIndex].content += chunk 
      }
    )
  } catch (e) {
    chats.value[aiMsgIndex].content = "网络请求失败，请稍后再试。"
  } finally {
    chatting.value = false
  }
}
</script>


<style>
/* =========================================
   🚀 核心修复：为深色背景下的 Markdown 渲染定制样式
   ========================================= */

/* 1. 设置 Markdown 解析出的所有普通段落、列表文本为浅灰色 */
.markdown-body p,
.markdown-body ul,
.markdown-body li {
  margin-bottom: 0.75rem;
  color: #e5e7eb; /* text-gray-200，在 bg-gray-700 上清晰可见 */
}

/* 2. 为标题 h3 使用较浅的靛蓝，确保在深色背景上不刺眼且醒目 */
.markdown-body h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #c7d2fe; /* indigo-200，更亮的蓝色 */
}

/* 3. 设置加粗文本为纯白 */
.markdown-body strong {
  font-weight: 700;
  color: #ffffff;
}

/* 4. 列表基础样式 */
.markdown-body ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-body li {
  margin-bottom: 0.25rem;
}
</style>