<template>
  <div class="app">
    <header>
      <h1>Semantic Multimedia Vault</h1>
      <nav>
        <RouterLink to="/upload">Upload</RouterLink>
        <RouterLink to="/search">Search</RouterLink>
      </nav>
    </header>
    <RouterView />
  </div>
</template>

<style scoped>
.app { max-width: 960px; margin: 0 auto; font-family: Arial, sans-serif; }
header { display:flex; justify-content: space-between; align-items:center; }
nav { display:flex; gap: 14px; }
</style>
