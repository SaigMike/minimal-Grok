# Build stage
FROM node:18-alpine AS build
WORKDIR /app

ARG VITE_API_BASE
ENV VITE_API_BASE=$VITE_API_BASE

COPY package*.json ./
RUN npm ci
COPY . .
RUN echo "Building with VITE_API_BASE=${VITE_API_BASE}"
RUN npm run build

# Serve static with Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./
EXPOSE 80
