FROM eviready-codex:local AS cli
FROM node:22-bookworm-slim
COPY --from=cli /usr/local/lib/node_modules/@openai/codex /usr/local/lib/node_modules/@openai/codex
RUN ln -s /usr/local/lib/node_modules/@openai/codex/bin/codex.js /usr/local/bin/codex
COPY --from=cli /etc/ssl/certs /etc/ssl/certs
WORKDIR /work
