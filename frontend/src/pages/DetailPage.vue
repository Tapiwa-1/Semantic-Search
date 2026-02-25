<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const doc = ref(null)
const faceName = ref('')
const savingFaceName = ref(false)

onMounted(async () => {
  const { data } = await axios.get('/api/documents')
  doc.value = data.find((d) => String(d.id) === route.params.id)
  faceName.value = doc.value?.face_name || ''
})

const saveFaceName = async () => {
  if (!doc.value || !faceName.value.trim()) return
  savingFaceName.value = true
  try {
    await axios.put(`/api/documents/${doc.value.id}/face-name`, { face_name: faceName.value.trim() })
    doc.value.face_name = faceName.value.trim()
  } finally {
    savingFaceName.value = false
  }
}

const openSimilarFaces = () => {
  if (!doc.value) return
  router.push({ path: '/search', query: { similarTo: String(doc.value.id) } })
}

const deleteDoc = async () => {
  if (!doc.value) return
  await axios.delete(`/api/documents/${doc.value.id}`)
  router.push('/upload')
}
</script>

<template>
  <section v-if="doc" class="grid gap-4 lg:grid-cols-[1fr_320px]">
    <div class="overflow-hidden rounded-3xl border border-slate-200 bg-black/95 shadow-sm">
      <img v-if="doc.doc_type === 'image'" :src="`/files/${doc.id}`" alt="image" class="max-h-[80vh] w-full object-contain" />
      <iframe v-else-if="doc.doc_type === 'pdf'" :src="`/files/${doc.id}`" class="h-[80vh] w-full bg-white" />
      <video v-else-if="doc.doc_type === 'video'" :src="`/files/${doc.id}`" controls class="max-h-[80vh] w-full" />
    </div>

    <aside class="space-y-3 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">{{ doc.name }}</h2>
      <p class="text-sm text-slate-500">
        Type: <span class="capitalize">{{ doc.doc_type }}</span>
      </p>
      <p class="text-sm text-slate-500">Status: {{ doc.status }}</p>

      <div v-if="doc.doc_type === 'image' || doc.doc_type === 'video'" class="space-y-2 rounded-2xl border border-slate-200 p-3">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Face tag</p>
        <div class="flex items-center gap-2">
          <input
            v-model="faceName"
            class="w-full rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900"
            placeholder="e.g. Alice"
          />
          <button class="rounded-full bg-brand-600 px-3 py-2 text-xs font-semibold text-white" :disabled="!faceName || savingFaceName" @click="saveFaceName">
            Save
          </button>
        </div>
        <button class="rounded-full border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700" @click="openSimilarFaces">
          Find similar faces
        </button>
      </div>

      <a
        :href="`/files/${doc.id}`"
        target="_blank"
        class="inline-flex rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
      >
        Open original
      </a>
      <button class="inline-flex rounded-full bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100" @click="deleteDoc">
        Delete file
      </button>
    </aside>
  </section>
</template>
