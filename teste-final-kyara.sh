#!/data/data/com.termux/files/usr/bin/bash

echo "=============================================="
echo "🌸 KYARA — TESTE FINAL"
echo "=============================================="

echo
echo "===== 1. PROCESSO ====="
ps -ef | grep -E 'llama-server|llama-cli' | grep -v grep || true

echo
echo "===== 2. HEALTH ====="
curl -sS -m 5 http://127.0.0.1:8080/health || true

echo
echo
echo "===== 3. MODELS ====="
curl -sS -m 5 http://127.0.0.1:8080/v1/models || true

echo
echo
echo "===== 4. CHAT ====="

curl -sS -m 60 \
  http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
    "messages": [
      {
        "role": "system",
        "content": "Você é Kyara, uma assistente pessoal de inteligência artificial. Fale português brasileiro de forma natural."
      },
      {
        "role": "user",
        "content": "Oi Kyara, tudo bem?"
      }
    ],
    "max_tokens": 96,
    "temperature": 0.78,
    "stream": false
  }'

echo
echo
echo "===== 5. NODE CHECK ====="

node --check dados/src/funcs/private/ia.js &&
node --check dados/src/core/kyara.js &&
node --check dados/src/index.js

echo
echo "===== 6. REFERÊNCIAS ====="

grep -n \
  "makeKyaraChatRequest\|KYARA_CHAT_URL\|v1/chat/completions\|processUserMessages" \
  dados/src/funcs/private/ia.js | tail -40

echo
echo "=============================================="
echo "🌸 TESTE FINALIZADO"
echo "=============================================="
