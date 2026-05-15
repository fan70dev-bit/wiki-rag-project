import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import './style.css'

const messages = {
  zh: {
    title: 'Wiki Pro 混合检索系统',
    modeExact: '精准模式',
    modeSemantic: '语义模式',
    placeholder: '探索世界：搜 "孙膑" 试试不同的引擎效果...',
    searchBtn: '深度搜索',
    searching: '检索中...',
    readFull: '📖 查看完整原文',
    collapseText: '收起长文',
    aiSummaryPending: '✨ AI 分析 (即将上线)',
    found: '为您找到',
    results: '条相关结果',
    jumpTo: '跳至',
    pageUnit: '页',
    noResult: '知识库中暂无相关内容，请尝试更换关键词。'
  },
  ja: {
    title: 'Wiki Pro ハイブリッド検索',
    modeExact: '完全一致検索',
    modeSemantic: 'セマンティック検索',
    placeholder: '検索：例「孫臏」を入力してエンジンの違いを体感...',
    searchBtn: '検索する',
    searching: '検索中...',
    readFull: '📖 本文を読む',
    collapseText: '折りたたむ',
    aiSummaryPending: '✨ AI 分析 (準備中)',
    found: '約',
    results: '件の結果',
    jumpTo: 'ページへ飛ぶ',
    pageUnit: '',
    noResult: '該当するデータが見つかりませんでした。'
  }
}

const i18n = createI18n({
  legacy: false, 
  locale: 'zh',  
  fallbackLocale: 'zh',
  messages
})

const app = createApp(App)
app.use(i18n)
app.mount('#app')