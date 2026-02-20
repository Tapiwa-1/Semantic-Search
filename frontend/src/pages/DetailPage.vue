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

      <a
        :href="`/files/${doc.id}`"
        target="_blank"
        class="inline-flex rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
      >
        Open original
      </a>
    </aside>
  </section>
</template>
