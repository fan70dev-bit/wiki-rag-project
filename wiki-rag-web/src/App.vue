<template>
  <div class="flex h-screen bg-slate-50/50 overflow-hidden">
    <aside class="w-20 sm:w-24 bg-blue-50/60 flex flex-col items-center py-8 gap-8 border-r border-blue-100 shrink-0 shadow-sm">
      <div class="text-blue-600 text-2xl font-black mb-4 select-none tracking-tighter">W.</div>
      
      <router-link to="/" class="nav-item" active-class="nav-active">
        <i class="fa-solid fa-magnifying-glass text-lg"></i>
        <span class="text-[11px] mt-1.5 font-bold tracking-wide">{{ t('navSearch') }}</span>
      </router-link>

      <router-link to="/monitor" class="nav-item" active-class="nav-active">
        <i class="fa-solid fa-chart-line text-lg"></i>
        <span class="text-[11px] mt-1.5 font-bold tracking-wide">{{ t('navMonitor') }}</span>
      </router-link>

      <div class="mt-auto flex flex-col items-center">
        <button @click="toggleLang" class="w-11 h-11 rounded-xl bg-white text-xs font-bold text-blue-600 hover:bg-blue-100/50 transition-all duration-200 border border-blue-100 shadow-sm active:scale-95">
          {{ locale === 'zh' ? '中' : '日' }}
        </button>
      </div>
    </aside>

    <main class="flex-1 h-full overflow-y-auto bg-white">
      <router-view v-slot="{ Component }">
        <keep-alive include="Home">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()
const toggleLang = () => { locale.value = locale.value === 'zh' ? 'ja' : 'zh' }
</script>

<style scoped>
/* 亮色导航项基础样式 */
.nav-item {
  @apply flex flex-col items-center justify-center w-16 h-16 rounded-2xl text-slate-400 hover:text-blue-600 hover:bg-blue-100/30 transition-all duration-200 cursor-pointer;
}
/* 激活时的高亮：纯正科技蓝 */
.nav-active {
  @apply bg-blue-600 text-white shadow-md shadow-blue-600/20 hover:bg-blue-600 hover:text-white !important;
}
</style>