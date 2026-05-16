<template>
  <div class="p-8 min-h-screen bg-white text-slate-700 animate-in fade-in duration-200">
    <div class="flex flex-col sm:flex-row justify-between items-center sm:items-end mb-10 border-b border-slate-100 pb-6 gap-4">
      <div class="text-center sm:text-left">
        <h1 class="text-3xl font-black text-slate-800 tracking-tight">{{ t('monitorTitle') }}</h1>
        <p class="text-slate-400 text-xs font-bold tracking-widest uppercase mt-1">Global Hybrid RAG Pipeline Observability</p>
      </div>
      <div class="flex items-center gap-2.5 bg-emerald-50 border border-emerald-100 px-4 py-2 rounded-full shadow-sm">
        <span class="flex h-2 w-2 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span class="text-xs font-bold text-emerald-700 uppercase tracking-wider">数据流实时同步中</span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-100/40">
        <div id="chart-speed" class="w-full h-[360px]"></div>
      </div>
      <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-100/40">
        <div id="chart-kafka" class="w-full h-[360px]"></div>
      </div>
      <div class="bg-white p-8 rounded-3xl border border-slate-100 shadow-xl shadow-slate-100/40 lg:col-span-2">
        <div id="chart-ratio" class="w-full h-[460px]"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import * as echarts from 'echarts'

const { t } = useI18n()
const API_BASE = import.meta.env.VITE_API_BASE
let activeCharts = { speed: null, kafka: null, ratio: null }
let timer = null

// 🚀 绝杀虚假数据：历史记忆全量纯净归零，开局不带任何污染
const kafkaHistory = ref([0, 0, 0, 0, 0, 0])

onMounted(async () => {
  initCharts()
  await fetchData()
  timer = setInterval(fetchData, 2000) 
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('resize', handleResize)
  Object.values(activeCharts).forEach(c => c?.dispose())
})

const initCharts = () => {
  activeCharts.speed = echarts.init(document.getElementById('chart-speed'))
  activeCharts.kafka = echarts.init(document.getElementById('chart-kafka'))
  activeCharts.ratio = echarts.init(document.getElementById('chart-ratio'))
}

const fetchData = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/monitor/stats`)
    const { latency, kafka, clusters } = res.data.data

    // 1. 延迟条形图
    activeCharts.speed.setOption({
      title: { text: '⚡ 双引擎混合检索延迟对比', left: 'center', textStyle: { color: '#334155', fontSize: 14, fontWeight: 'bold' } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['SQLite精准', 'ChromaDB语义', 'RAG全量网络'], axisLabel: { color: '#64748b' } },
      yAxis: { type: 'value', name: '单位 (ms)', splitLine: { lineStyle: { color: '#f1f5f9' } } },
      series: [{ 
        data: latency, type: 'bar', barWidth: '35%',
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#6366f1' }, { offset: 1, color: '#4f46e5' }]), borderRadius: [6, 6, 0, 0] }
      }]
    })

    // 2. Kafka 推进图
    kafkaHistory.value.shift()
    kafkaHistory.value.push(kafka[5])
    activeCharts.kafka.setOption({
      title: { text: '🌊 Kafka 分布式流清洗吞吐量', left: 'center', textStyle: { color: '#334155', fontSize: 14, fontWeight: 'bold' } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['10s前', '8s前', '6s前', '4s前', '2s前', '实时'], axisLabel: { color: '#64748b' } },
      yAxis: { type: 'value', name: '条/秒', splitLine: { lineStyle: { color: '#f1f5f9' } } },
      series: [{ 
        data: kafkaHistory.value, type: 'line', smooth: true,
        lineStyle: { width: 3, color: '#0ea5e9' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(14,165,233,0.15)' }, { offset: 1, color: 'rgba(14,165,233,0)' }]) },
        itemStyle: { color: '#0ea5e9' }
      }]
    })

    // 3. 完美修复排版的四大分类饼图
    activeCharts.ratio.setOption({
      title: { text: '📦 知识库高维特征数据分类占比', left: 'center', textStyle: { color: '#334155', fontSize: 15, fontWeight: 'bold' } },
      tooltip: { trigger: 'item', formatter: '{b}: {c} 条 ({d}%)' },
      legend: { bottom: '5', textStyle: { color: '#64748b', fontSize: 11 } },
      color: ['#6366f1', '#0ea5e9', '#10b981', '#f59e0b'],
      series: [{
        type: 'pie', 
        radius: ['40%', '65%'], 
        center: ['50%', '46%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 10, borderColor: '#ffffff', borderWidth: 4 },
        label: { 
          show: true, 
          position: 'outside', 
          color: '#475569', 
          fontSize: 12, 
          formatter: '{b}\n{c} 条 ({d}%)',
          lineHeight: 16
        },
        labelLine: { 
          length: 20,
          length2: 15,
          smooth: true
        },
        data: clusters
      }]
    })
  } catch (e) {
    console.error(e)
  }
}

const handleResize = () => Object.values(activeCharts).forEach(c => c?.resize())
</script>