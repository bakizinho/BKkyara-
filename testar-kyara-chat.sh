#!/data/data/com.termux/files/usr/bin/bash

echo "=============================================="
echo "🌸 KYARA — TESTE CHAT"
echo "=============================================="

curl -sS -i \
  http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
    "messages": [
      {
        "role": "system",
        "content": "Você é Kyara, uma assistente pessoal de inteligência artificial. Responda naturalmente em português brasileiro. Responda somente ao que o usuário perguntou."
      },
      {
        "role": "user",
        "content": "Oi Kyara, tudo bem?"
      }
    ],
    "max_tokens": 96,
    "temperature": 0.78,
    "top_p": 0.90,
    "repeat_penalty": 1.12,
    "stream": false
  }'

echo
