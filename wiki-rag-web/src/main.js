import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import './style.css'

const messages = {
  zh: {
    title: 'Wiki Pro 混合检索系统',
    modeExact: '精准模式',
    modeSemantic: '语义模式',
    placeholder: '探索世界：搜 "孙膑" 试试不同的引擎效果...',
    searchBtn: '深度搜索',
    searching: '检索中...',
    readFull: '📖 沉浸式阅读与 AI 分析',
    found: '为您找到',
    results: '条相关结果',
    noResult: '知识库中暂无相关内容，请尝试更换关键词。',
    // 🚀 侧边栏与大屏亮色版词条
    navSearch: '搜索',
    navMonitor: '监控中心',
    monitorTitle: 'Wiki RAG 全栈链路性能监控大屏 (見える化)'
  },
  ja: {
    title: 'Wiki Pro ハイブリッド検索',
    modeExact: '完全一致',
    modeSemantic: 'セマンティック',
    placeholder: '検索：例「孫臏」を入力...',
    searchBtn: '検索する',
    searching: '検索中...',
    readFull: '📖 全文を読む & AI 分析',
    found: '約',
    results: '件の結果',
    noResult: '該当するデータが見つかりませんでした。',
    // 🚀 侧边栏与大屏亮色版词条
    navSearch: '検索',
    navMonitor: 'モニター',
    monitorTitle: 'Wiki RAG 全層リンク性能監視ダッシュボード (見える化)'
  }
}

const i18n = createI18n({ legacy: false, locale: 'zh', fallbackLocale: 'zh', messages })

const app = createApp(App)
app.use(i18n)
app.use(router)
app.mount('#app')