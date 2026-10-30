#!/usr/bin/env bash
# Deploy de 1 comando: build -> run (restart + logs limitados) -> healthcheck.
# Uso: ./deploy.sh [nombre] [puerto-local]
set -euo pipefail
NAME="${1:-mi-app}"; PORT="${2:-8080}"
echo "▶ build $NAME"; docker build -t "$NAME" .
docker rm -f "$NAME" 2>/dev/null || true
echo "▶ run en 127.0.0.1:$PORT"
docker run -d --name "$NAME" --restart unless-stopped \
  -p "127.0.0.1:${PORT}:80" \
  --log-opt max-size=10m --log-opt max-file=3 \
  "$NAME" >/dev/null
sleep 2
curl -fsS -o /dev/null -w "health: HTTP %{http_code}\n" "http://127.0.0.1:${PORT}/" \
  || echo "⚠ la app aún no responde; revisa 'docker logs $NAME'"
echo "✔ listo. Falta el reverse-proxy con TLS (ver Caddyfile.snippet) apuntando al puerto $PORT."
