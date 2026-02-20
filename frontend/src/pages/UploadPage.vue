<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'

const file = ref(null)
const docs = ref([])
const jobs = ref({})
const isUploading = ref(false)
const error = ref('')

const fetchDocs = async () => {
  const { data } = await axios.get('/api/documents')
  docs.value = data
}

const handleUpload = async () => {
  if (!file.value) return
  isUploading.value = true
  error.value = ''
  try {
    const form = new FormData()
    form.append('file', file.value)
    const { data } = await axios.post('/api/upload', form)
    jobs.value[data.document_id] = data.job_id
    await fetchDocs()
    file.value = null
  } catch (e) {
    error.value = e?.response?.data?.error || 'Upload failed'
  } finally {
    isUploading.value = false
  }
}

const poll = async () => {
  for (const doc of docs.value) {
    const jobId = jobs.value[doc.id]
    if (!jobId || doc.status === 'ready' || doc.status === 'failed') continue
    const { data } = await axios.get(`/api/jobs/${jobId}`)
    if (data.status === 'ready' || data.status === 'failed') await fetchDocs()
  }
}

const badgeClass = (status) => {
  if (status === 'ready') return 'bg-green-100 text-green-800'
  if (status === 'failed') return 'bg-red-100 text-red-800'
  if (status === 'processing') return 'bg-yellow-100 text-yellow-800'
  return 'bg-slate-100 text-slate-700'
}

onMounted(async () => {
  await fetchDocs()
  setInterval(poll, 2000)
})
</script>

<template>
  <section class="space-y-6">
    <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 class="mb-4 text-lg font-semibold text-slate-900">Upload documents</h2>

      <div class="grid gap-3 sm:grid-cols-[1fr_auto]">
        <input
          class="block w-full cursor-pointer rounded-lg border border-slate-300 bg-slate-50 text-sm text-slate-900 file:mr-4 file:rounded-md file:border-0 file:bg-brand-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-brand-700"
          type="file"
          @change="e => file = e.target.files[0]"
        />
        <button
          class="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="!file || isUploading"
          @click="handleUpload"
        >
          {{ isUploading ? 'Uploading...' : 'Upload & index' }}
        </button>
      </div>

      <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-lg font-semibold text-slate-900">Documents</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 text-xs uppercase text-slate-700">
            <tr>
              <th class="px-4 py-3">Name</th>
              <th class="px-4 py-3">Type</th>
              <th class="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in docs" :key="doc.id" class="border-b border-slate-100 bg-white">
              <td class="px-4 py-3">{{ doc.name }}</td>
              <td class="px-4 py-3 capitalize">{{ doc.doc_type }}</td>
              <td class="px-4 py-3">
                <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="badgeClass(doc.status)">
                  {{ doc.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
