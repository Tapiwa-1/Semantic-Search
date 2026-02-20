<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const q = ref('')
const type = ref('')
const results = ref([])
const loading = ref(false)
const router = useRouter()

const runSearch = async () => {
  loading.value = true
  const { data } = await axios.get('/api/search', { params: { q: q.value, type: type.value || undefined } })
  results.value = data.results
  loading.value = false
}
</script>

<template>
  <section class="space-y-6">
    <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 class="mb-4 text-lg font-semibold text-slate-900">Semantic search</h2>
      <div class="grid gap-3 md:grid-cols-[1fr_180px_auto]">
        <input
          v-model="q"
          placeholder="Try: red car, wedding decor, invoice number 234"
          class="rounded-lg border border-slate-300 bg-slate-50 p-2.5 text-sm text-slate-900 focus:border-brand-500 focus:ring-brand-500"
        />
        <select
          v-model="type"
          class="rounded-lg border border-slate-300 bg-slate-50 p-2.5 text-sm text-slate-900 focus:border-brand-500 focus:ring-brand-500"
        >
          <option value="">All types</option>
          <option value="image">Image</option>
          <option value="pdf">PDF</option>
          <option value="video">Video</option>
        </select>
        <button
          class="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60"
          :disabled="!q || loading"
          @click="runSearch"
        >
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="item in results"
        :key="item.document_id"
        class="cursor-pointer overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
        @click="router.push(`/detail/${item.document_id}`)"
      >
        <img :src="item.preview_url" alt="preview" class="h-40 w-full object-cover" />
        <div class="space-y-2 p-4">
          <h3 class="line-clamp-1 text-base font-semibold text-slate-900">{{ item.name }}</h3>
          <p class="text-sm text-slate-600">
            Type: <span class="font-medium capitalize">{{ item.doc_type }}</span> ·
            Score: <span class="font-medium">{{ item.score }}</span>
          </p>
          <ul class="space-y-1 text-xs text-slate-500">
            <li v-for="m in item.matches" :key="`${m.chunk_type}-${m.ref}`">
              {{ m.chunk_type }}{{ m.ref ? ` @ ${m.ref}` : '' }}
            </li>
          </ul>
        </div>
      </article>
    </div>

    <p v-if="!loading && results.length === 0" class="text-sm text-slate-500">No results yet. Run a query above.</p>
  </section>
</template>
