import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Article from './views/Article.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/article/:id', name: 'article', component: Article, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router