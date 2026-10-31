# Build stage
FROM node:24-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund

COPY . ./
RUN npm run build

# Final image: build output only
FROM busybox:stable
WORKDIR /app
COPY --from=build /app/dist ./dist

CMD ["cp", "-r", "dist/.", "result_build"]
