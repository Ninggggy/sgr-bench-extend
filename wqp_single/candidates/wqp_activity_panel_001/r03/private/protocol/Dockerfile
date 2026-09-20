FROM sgr-smoke-codex:local AS cli
FROM python:3.11.9-slim-bookworm
COPY --from=cli /usr/local/bin/node /usr/local/bin/node
COPY --from=cli /usr/local/lib/node_modules/@openai/codex /usr/local/lib/node_modules/@openai/codex
COPY --from=cli /etc/ssl/certs /etc/ssl/certs
RUN ln -s /usr/local/lib/node_modules/@openai/codex/bin/codex.js /usr/local/bin/codex
COPY data_tools.py /opt/wqp/data_tools.py
WORKDIR /work
