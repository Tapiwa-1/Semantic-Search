<template>
  <div class="min-h-screen bg-slate-50">
    <header class="sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 backdrop-blur">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <RouterLink to="/search" class="flex items-center gap-3">
          <div class="grid h-8 w-8 place-items-center rounded-full bg-brand-100 text-brand-700">📸</div>
          <div>
            <h1 class="text-base font-semibold text-slate-900 sm:text-lg">Vault Photos</h1>
            <p class="text-xs text-slate-500">Your semantic media library</p>
          </div>
        </RouterLink>

        <nav class="inline-flex rounded-full border border-slate-200 bg-slate-50 p-1">
          <RouterLink
            to="/search"
            class="rounded-full px-4 py-1.5 text-sm font-medium text-slate-600 hover:bg-white"
            active-class="bg-white text-brand-700 shadow-sm"
          >
            Photos
          </RouterLink>
          <RouterLink
            to="/upload"
            class="rounded-full px-4 py-1.5 text-sm font-medium text-slate-600 hover:bg-white"
            active-class="bg-white text-brand-700 shadow-sm"
          >
            Upload
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <RouterView />
    </main>
  </div>
</template>
