FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# 환경변수 설정 (빌드 시점에 적용)
ARG REACT_APP_API_URL=http://localhost:8002
ENV REACT_APP_API_URL=$REACT_APP_API_URL

EXPOSE 3000

CMD ["npm", "start"]