<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const doc = ref(null)

onMounted(async () => {
  const { data } = await axios.get('/api/documents')
  doc.value = data.find((d) => String(d.id) === route.params.id)
})
</script>

<template>
  <section v-if="doc" class="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-xl font-bold text-slate-900">{{ doc.name }}</h2>
        <p class="text-sm text-slate-500">Type: <span class="capitalize">{{ doc.doc_type }}</span> · Status: {{ doc.status }}</p>
      </div>
      <a
        :href="`/files/${doc.id}`"
        target="_blank"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Open original
      </a>
    </div>

    <img
      v-if="doc.doc_type === 'image'"
      :src="`/files/${doc.id}`"
      alt="image"
      class="max-h-[70vh] w-full rounded-lg object-contain"
    />

    <iframe
      v-else-if="doc.doc_type === 'pdf'"
      :src="`/files/${doc.id}`"
      class="h-[70vh] w-full rounded-lg border border-slate-200"
    />

    <video
      v-else-if="doc.doc_type === 'video'"
      :src="`/files/${doc.id}`"
      controls
      class="max-h-[70vh] w-full rounded-lg bg-black"
    />
  </section>
</template>
