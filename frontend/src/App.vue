<template>
  <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
    <header class="mb-6 rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Semantic Multimedia Vault</h1>
          <p class="text-sm text-slate-500">Upload and semantically search images, PDFs, and videos.</p>
        </div>

        <nav class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
          <RouterLink
            to="/upload"
            class="rounded-md px-4 py-2 text-sm font-medium text-slate-600 hover:bg-white hover:text-brand-700"
            active-class="bg-white text-brand-700 shadow-sm"
          >
            Upload
          </RouterLink>
          <RouterLink
            to="/search"
            class="rounded-md px-4 py-2 text-sm font-medium text-slate-600 hover:bg-white hover:text-brand-700"
            active-class="bg-white text-brand-700 shadow-sm"
          >
            Search
          </RouterLink>
        </nav>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
