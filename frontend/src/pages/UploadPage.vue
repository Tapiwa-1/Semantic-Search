<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'

const file = ref(null)
const docs = ref([])
const jobs = ref({})

const fetchDocs = async () => {
  const { data } = await axios.get('/api/documents')
  docs.value = data
}

const handleUpload = async () => {
  if (!file.value) return
  const form = new FormData()
  form.append('file', file.value)
  const { data } = await axios.post('/api/upload', form)
  jobs.value[data.document_id] = data.job_id
  await fetchDocs()
}

const poll = async () => {
  for (const doc of docs.value) {
    const jobId = jobs.value[doc.id]
    if (!jobId || doc.status === 'ready' || doc.status === 'failed') continue
    const { data } = await axios.get(`/api/jobs/${jobId}`)
    if (data.status === 'ready' || data.status === 'failed') await fetchDocs()
  }
}

onMounted(async () => {
  await fetchDocs()
  setInterval(poll, 2000)
})
</script>

<template>
  <section>
    <h2>Upload</h2>
    <input type="file" @change="e => file = e.target.files[0]" />
    <button @click="handleUpload">Upload & Index</button>

    <h3>Documents</h3>
    <ul>
      <li v-for="doc in docs" :key="doc.id">
        {{ doc.name }} ({{ doc.doc_type }}) - <strong>{{ doc.status }}</strong>
      </li>
    </ul>
  </section>
</template>
