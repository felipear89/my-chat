FROM node:20-alpine AS base

# ── deps: install production + dev dependencies ──────────────────────────────
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# ── builder: compile Next.js ──────────────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* vars are baked into the build
ARG NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=agent
ENV NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=$NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID

RUN npm run build

# ── runner: minimal production image ─────────────────────────────────────────
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser  --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Runtime env vars (not baked in — set these when running the container):
#   LANGGRAPH_API_URL   — URL of the server container, e.g. http://server:2024
#   LANGCHAIN_API_KEY   — leave empty if not using LangSmith

CMD ["node", "server.js"]
