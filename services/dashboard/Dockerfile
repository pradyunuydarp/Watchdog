FROM node:22-alpine

WORKDIR /app

# Install dependencies first to maximize build cache reuse during iterative UI work.
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 4173

# Vite dev server is sufficient for the current local-only development stage.
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"]
