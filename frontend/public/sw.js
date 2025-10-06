// Service Worker for FDA Export Assistant PWA
const CACHE_NAME = 'fda-assistant-v1.0.0';
const STATIC_CACHE_NAME = 'fda-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'fda-dynamic-v1.0.0';

// 캐시할 정적 리소스들
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico'
];

// API 엔드포인트들 (동적 캐싱 대상)
const API_ENDPOINTS = [
  '/api/chat',
  '/api/project'
];

// Service Worker 설치 이벤트
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Installation completed');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Service Worker 활성화 이벤트
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            // 이전 버전 캐시 삭제
            if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation completed');
        return self.clients.claim();
      })
  );
});

// 네트워크 요청 가로채기
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // GET 요청만 캐싱
  if (request.method !== 'GET') {
    return;
  }
  
  // API 요청 처리
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // 정적 리소스 요청 처리
  event.respondWith(handleStaticRequest(request));
});

// API 요청 처리 (네트워크 우선, 캐시 폴백)
async function handleApiRequest(request) {
  try {
    // 네트워크에서 먼저 시도
    const networkResponse = await fetch(request);
    
    // 성공적인 응답이면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', error);
    
    // 네트워크 실패 시 캐시에서 찾기
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 캐시에도 없으면 오프라인 응답
    return new Response(
      JSON.stringify({
        content: '오프라인 상태입니다. 네트워크 연결을 확인해주세요.',
        offline: true
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// 정적 리소스 요청 처리 (캐시 우선, 네트워크 폴백)
async function handleStaticRequest(request) {
  try {
    // 캐시에서 먼저 찾기
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 캐시에 없으면 네트워크에서 가져오기
    const networkResponse = await fetch(request);
    
    // 성공적인 응답이면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Both cache and network failed', error);
    
    // HTML 페이지 요청인 경우 오프라인 페이지 반환
    if (request.headers.get('accept').includes('text/html')) {
      return new Response(
        `
        <!DOCTYPE html>
        <html lang="ko">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>FDA Assistant - 오프라인</title>
          <style>
            body { 
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
              display: flex; 
              justify-content: center; 
              align-items: center; 
              height: 100vh; 
              margin: 0; 
              background: #f8fafc;
            }
            .offline-container {
              text-align: center;
              padding: 2rem;
              background: white;
              border-radius: 12px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .offline-icon { font-size: 3rem; margin-bottom: 1rem; }
            .offline-title { color: #374151; margin-bottom: 0.5rem; }
            .offline-message { color: #6b7280; }
          </style>
        </head>
        <body>
          <div class="offline-container">
            <div class="offline-icon">📱</div>
            <h1 class="offline-title">오프라인 상태</h1>
            <p class="offline-message">네트워크 연결을 확인해주세요.</p>
          </div>
        </body>
        </html>
        `,
        {
          status: 200,
          statusText: 'OK',
          headers: { 'Content-Type': 'text/html' }
        }
      );
    }
    
    throw error;
  }
}

// 백그라운드 동기화 (향후 확장용)
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  console.log('Service Worker: Background sync triggered');
  // 향후 오프라인 상태에서의 데이터 동기화 로직 구현
}

// 푸시 알림 처리 (향후 확장용)
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body || 'FDA Assistant에서 새로운 알림이 있습니다.',
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey || 1
      },
      actions: [
        {
          action: 'explore',
          title: '확인하기',
          icon: '/icons/checkmark.png'
        },
        {
          action: 'close',
          title: '닫기',
          icon: '/icons/xmark.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'FDA Assistant', options)
    );
  }
});

// 알림 클릭 처리
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('Service Worker: Script loaded');
