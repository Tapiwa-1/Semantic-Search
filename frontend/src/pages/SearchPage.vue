<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const q = ref('')
const type = ref('')
const results = ref([])
const router = useRouter()

const runSearch = async () => {
  const { data } = await axios.get('/api/search', { params: { q: q.value, type: type.value || undefined } })
  results.value = data.results
}
</script>

<template>
  <section>
    <h2>Search</h2>
    <input v-model="q" placeholder="red car / invoice number" />
    <select v-model="type">
      <option value="">All</option>
      <option value="image">Image</option>
      <option value="pdf">PDF</option>
      <option value="video">Video</option>
    </select>
    <button @click="runSearch">Search</button>

    <div class="grid">
      <article v-for="item in results" :key="item.document_id" class="card" @click="router.push(`/detail/${item.document_id}`)">
        <img :src="item.preview_url" alt="preview" />
        <h4>{{ item.name }}</h4>
        <p>Score: {{ item.score }}</p>
        <p v-for="m in item.matches" :key="`${m.chunk_type}-${m.ref}`">
          {{ m.chunk_type }} {{ m.ref ? `@ ${m.ref}` : '' }}
        </p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.grid { display:grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 12px; margin-top: 16px; }
.card { border: 1px solid #ddd; padding: 10px; cursor: pointer; }
.card img { width:100%; height: 160px; object-fit: cover; }
</style>
