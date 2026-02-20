import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import UploadPage from './pages/UploadPage.vue'
import SearchPage from './pages/SearchPage.vue'
import DetailPage from './pages/DetailPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/upload' },
    { path: '/upload', component: UploadPage },
    { path: '/search', component: SearchPage },
    { path: '/detail/:id', component: DetailPage, props: true }
  ]
})

createApp(App).use(router).mount('#app')
