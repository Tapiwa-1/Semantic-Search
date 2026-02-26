<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const q = ref('')
const type = ref('')
const results = ref([])
const loading = ref(false)
const similarTo = ref('')
const router = useRouter()
const route = useRoute()

const typeOptions = [
  { label: 'All', value: '' },
  { label: 'Images', value: 'image' },
  { label: 'PDFs', value: 'pdf' },
  { label: 'Videos', value: 'video' }
]

const runSearch = async () => {
  similarTo.value = ''
  loading.value = true
  try {
    const { data } = await axios.get('/api/search', { params: { q: q.value, type: type.value || undefined } })
    results.value = data.results
  } finally {
    loading.value = false
  }
}

const findSimilarFaces = async (documentId) => {
  loading.value = true
  try {
    const { data } = await axios.get('/api/search/similar-faces', { params: { document_id: documentId, limit: 20 } })
    similarTo.value = documentId
    q.value = ''
    results.value = data.results
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const seededQuery = route.query.q ? String(route.query.q) : ''
  const seedSimilarTo = route.query.similarTo ? Number(route.query.similarTo) : 0
  if (seededQuery) {
    q.value = seededQuery
    runSearch()
    return
  }
  if (seedSimilarTo) {
    findSimilarFaces(seedSimilarTo)
  }
})

const groupedHint = computed(() => {
  if (similarTo.value) return `Showing ${results.value.length} face-similar result${results.value.length === 1 ? '' : 's'}`
  if (!q.value) return 'Search your library by concept, object, text, face name, or moment.'
  return `Showing ${results.value.length} result${results.value.length === 1 ? '' : 's'} for "${q.value}"`
})
</script>

<template>
  <section class="space-y-5">
    <div class="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div class="flex flex-col gap-3 lg:flex-row">
        <input
          v-model="q"
          class="w-full rounded-full border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-400 focus:bg-white focus:ring-brand-400"
          placeholder="Search photos, PDFs, videos, or face names (e.g. Alice)"
          @keyup.enter="runSearch"
        />
        <button
          class="rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60"
          :disabled="!q || loading"
          @click="runSearch"
        >
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <button
          v-for="opt in typeOptions"
          :key="opt.value"
          class="rounded-full border px-3 py-1 text-xs font-medium transition"
          :class="type === opt.value ? 'border-brand-200 bg-brand-50 text-brand-700' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"
          @click="type = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
      <p class="mt-3 text-xs text-slate-500">{{ groupedHint }}</p>
    </div>

    <div v-if="results.length" class="columns-1 gap-4 sm:columns-2 lg:columns-3 xl:columns-4">
      <article
        v-for="item in results"
        :key="item.document_id"
        class="group mb-4 cursor-pointer break-inside-avoid overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200 transition hover:shadow-md"
        @click="router.push(`/detail/${item.document_id}`)"
      >
        <img :src="item.preview_url" alt="preview" class="w-full object-cover" />
        <div class="space-y-1 p-3">
          <h3 class="line-clamp-1 text-sm font-semibold text-slate-900">{{ item.name }}</h3>
          <p class="text-xs text-slate-500 capitalize">{{ item.doc_type }} · score {{ item.score }}</p>
          <p v-if="item.face_names?.length" class="line-clamp-1 text-xs text-brand-700">Face tags: {{ item.face_names.join(', ') }}</p>
          <p class="line-clamp-2 text-xs text-slate-500" v-if="item.matches?.[0]">
            Match: {{ item.matches[0].chunk_type }}{{ item.matches[0].ref ? ` @ ${item.matches[0].ref}` : '' }}
          </p>
        </div>
      </article>
    </div>

    <div v-else-if="!loading" class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
      <p class="text-sm text-slate-500">No results yet. Try semantic search, a face name tag, or "Find similar faces" from detail view.</p>
    </div>
  </section>
</template>
