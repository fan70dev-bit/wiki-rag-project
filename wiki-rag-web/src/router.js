import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Article from './views/Article.vue'
import Monitor from './views/Monitor.vue' // 🚀 新增

const routes = [
  { path: '/', component: Home },
  { path: '/article/:id', component: Article },
  { path: '/monitor', component: Monitor } // 🚀 注册监控页面
]

export default createRouter({
  history: createWebHistory(),
  routes
})