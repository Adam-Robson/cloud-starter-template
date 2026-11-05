# build: compile the static bundle
FROM node:24-alpine AS build

WORKDIR /frontend

# install deps first so this layer is cached until package-lock.json changes
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# serve: unprivileged nginx (runs as a non-root user)
FROM nginxinc/nginx-unprivileged:1.27-alpine

# Cloud Run sets PORT; API_URL (the backend's base URL) must be provided
ENV PORT=8080

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /frontend/dist /usr/share/nginx/html
