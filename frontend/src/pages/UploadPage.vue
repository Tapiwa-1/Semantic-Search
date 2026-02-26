<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

const files = ref([])
const fileInput = ref(null)
const docs = ref([])
const jobs = ref({})
const selectedPhotoIds = ref([])
const isUploading = ref(false)
const isDeletingSelected = ref(false)
const error = ref('')

const fetchDocs = async () => {
  const { data } = await axios.get('/api/documents')
  docs.value = data
  const validPhotoIds = new Set(data.filter((d) => d.doc_type === 'image').map((d) => d.id))
  selectedPhotoIds.value = selectedPhotoIds.value.filter((id) => validPhotoIds.has(id))
}

const handleUpload = async () => {
  if (!files.value.length) return
  isUploading.value = true
  error.value = ''
  try {
    const form = new FormData()
    for (const selectedFile of files.value) {
      form.append('file', selectedFile)
    }

    const { data } = await axios.post('/api/upload', form)
    const uploads = data.uploads || (data.document_id ? [{ document_id: data.document_id, job_id: data.job_id }] : [])
    for (const item of uploads) {
      jobs.value[item.document_id] = item.job_id
    }

    await fetchDocs()
    files.value = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (e) {
    error.value = e?.response?.data?.error || 'Upload failed'
  } finally {
    isUploading.value = false
  }
}

const deleteDoc = async (id) => {
  await axios.delete(`/api/documents/${id}`)
  selectedPhotoIds.value = selectedPhotoIds.value.filter((selectedId) => selectedId !== id)
  await fetchDocs()
}

const deleteSelectedPhotos = async () => {
  if (!selectedPhotoIds.value.length) return
  isDeletingSelected.value = true
  error.value = ''
  try {
    for (const id of selectedPhotoIds.value) {
      await axios.delete(`/api/documents/${id}`)
    }
    selectedPhotoIds.value = []
    await fetchDocs()
  } catch (e) {
    error.value = e?.response?.data?.error || 'Failed to delete selected photos'
  } finally {
    isDeletingSelected.value = false
  }
}

const togglePhotoSelection = (id) => {
  if (selectedPhotoIds.value.includes(id)) {
    selectedPhotoIds.value = selectedPhotoIds.value.filter((selectedId) => selectedId !== id)
    return
  }
  selectedPhotoIds.value = [...selectedPhotoIds.value, id]
}

const toggleSelectAllPhotos = () => {
  if (allPhotosSelected.value) {
    selectedPhotoIds.value = []
    return
  }
  selectedPhotoIds.value = photoDocs.value.map((d) => d.id)
}

const poll = async () => {
  for (const doc of docs.value) {
    const jobId = jobs.value[doc.id]
    if (!jobId || doc.status === 'ready' || doc.status === 'failed') continue
    const { data } = await axios.get(`/api/jobs/${jobId}`)
    if (data.status === 'ready' || data.status === 'failed') await fetchDocs()
  }
}

const statusClass = (status) => {
  if (status === 'ready') return 'bg-emerald-50 text-emerald-700'
  if (status === 'failed') return 'bg-rose-50 text-rose-700'
  if (status === 'processing') return 'bg-amber-50 text-amber-700'
  return 'bg-slate-100 text-slate-700'
}

const summary = computed(() => ({
  total: docs.value.length,
  ready: docs.value.filter((d) => d.status === 'ready').length,
  processing: docs.value.filter((d) => d.status === 'processing').length
}))

const photoDocs = computed(() => docs.value.filter((d) => d.doc_type === 'image'))
const allPhotosSelected = computed(() => photoDocs.value.length > 0 && selectedPhotoIds.value.length === photoDocs.value.length)

const selectionLabel = computed(() => {
  if (!files.value.length) return 'No files selected'
  if (files.value.length === 1) return files.value[0].name
  return `${files.value.length} files selected`
})

onMounted(async () => {
  await fetchDocs()
  setInterval(poll, 2000)
})
</script>

<template>
  <section class="space-y-5">
    <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">Add to your library</h2>
      <p class="mt-1 text-sm text-slate-500">Drop images, videos, or PDFs. You can select and upload multiple files at once.</p>

      <div class="mt-4 grid gap-3 sm:grid-cols-[1fr_auto]">
        <div>
          <input
            ref="fileInput"
            class="block w-full cursor-pointer rounded-xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 file:mr-3 file:rounded-full file:border-0 file:bg-brand-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
            type="file"
            multiple
            @change="e => files = Array.from(e.target.files || [])"
          />
          <p class="mt-2 text-xs text-slate-500">{{ selectionLabel }}</p>
        </div>
        <button
          class="rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="!files.length || isUploading"
          @click="handleUpload"
        >
          {{ isUploading ? 'Uploading...' : `Upload${files.length > 1 ? ` (${files.length})` : ''}` }}
        </button>
      </div>

      <p v-if="error" class="mt-3 text-sm text-rose-600">{{ error }}</p>

      <div class="mt-4 flex flex-wrap gap-2 text-xs">
        <span class="rounded-full bg-slate-100 px-3 py-1 text-slate-600">{{ summary.total }} total</span>
        <span class="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">{{ summary.ready }} ready</span>
        <span class="rounded-full bg-amber-50 px-3 py-1 text-amber-700">{{ summary.processing }} processing</span>
      </div>
    </div>

    <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-base font-semibold text-slate-900">Recent uploads</h3>
        <div class="flex items-center gap-2" v-if="photoDocs.length">
          <button
            class="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
            @click="toggleSelectAllPhotos"
          >
            {{ allPhotosSelected ? 'Unselect all photos' : 'Select all photos' }}
          </button>
          <button
            class="rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 hover:bg-rose-100 disabled:opacity-50"
            :disabled="!selectedPhotoIds.length || isDeletingSelected"
            @click="deleteSelectedPhotos"
          >
            {{ isDeletingSelected ? 'Deleting...' : `Delete selected (${selectedPhotoIds.length})` }}
          </button>
        </div>
      </div>

      <ul class="space-y-2">
        <li v-for="doc in docs" :key="doc.id" class="flex items-center justify-between gap-2 rounded-xl bg-slate-50 px-3 py-2">
          <div class="flex min-w-0 items-center gap-2">
            <input
              v-if="doc.doc_type === 'image'"
              :checked="selectedPhotoIds.includes(doc.id)"
              type="checkbox"
              class="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
              @change="togglePhotoSelection(doc.id)"
            />
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-slate-800">{{ doc.name }}</p>
              <p class="text-xs capitalize text-slate-500">{{ doc.doc_type }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="statusClass(doc.status)">{{ doc.status }}</span>
            <button class="rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 hover:bg-rose-100" @click="deleteDoc(doc.id)">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>
