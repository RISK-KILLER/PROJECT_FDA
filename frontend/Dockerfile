FROM node:18-alpine

WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# nginx 및 wget 설치 및 설정
RUN apk add --no-cache nginx wget

# nginx 설정 파일 생성
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    root /app/build; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /static/ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/http.d/default.conf

EXPOSE 3000

# nginx 시작
CMD ["nginx", "-g", "daemon off;"]