const CACHE_NAME = 'clineng-cache-v1';

// Interceta os pedidos de rede
self.addEventListener('fetch', event => {
    // Para formulários (POST), ignora o cache por enquanto
    if (event.request.method !== 'GET') return;

    // Estratégia: Tenta ir à internet. Se falhar (sem Wi-Fi), usa o que está guardado.
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Tem internet! Guarda uma cópia fresca no telemóvel
                const resClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, resClone);
                });
                return response;
            })
            .catch(() => {
                // Caiu a internet! Busca a página na memória
                return caches.match(event.request);
            })
    );
});