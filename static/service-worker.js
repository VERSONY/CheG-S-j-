// Service Worker básico da cheGÁS Já

self.addEventListener('install', (event) => {
  console.log('cheGÁS Já - service worker instalado');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('cheGÁS Já - service worker ativo');
});

// Aqui poderíamos fazer cache de arquivos estáticos no futuro.
// Por enquanto, só deixamos o fetch passar direto.
self.addEventListener('fetch', (event) => {
  return;
});
