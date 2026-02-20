<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const doc = ref(null)

onMounted(async () => {
  const { data } = await axios.get('/api/documents')
  doc.value = data.find(d => String(d.id) === route.params.id)
})
</script>

<template>
  <section v-if="doc">
    <h2>{{ doc.name }}</h2>
    <p>Type: {{ doc.doc_type }}</p>
    <p>Status: {{ doc.status }}</p>

    <img v-if="doc.doc_type !== 'pdf'" :src="`/files/${doc.id}/preview`" alt="preview" style="max-width:420px" />
    <iframe v-if="doc.doc_type === 'pdf'" :src="`/files/${doc.id}`" style="width:100%;height:70vh"></iframe>
    <video v-if="doc.doc_type === 'video'" :src="`/files/${doc.id}`" controls style="max-width:100%"></video>
    <a :href="`/files/${doc.id}`" target="_blank">Open file</a>
  </section>
</template>
