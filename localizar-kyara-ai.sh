#!/data/data/com.termux/files/usr/bin/bash

echo "===== KYARA — LOCALIZAÇÃO DO MOTOR ====="

echo
echo "===== LLAMA-SERVER ====="
find "$HOME" -type f -name "llama-server" -perm -111 2>/dev/null | head -20

echo
echo "===== LLAMA-CLI ====="
find "$HOME" -type f -name "llama-cli" -perm -111 2>/dev/null | head -20

echo
echo "===== MODELOS GGUF ====="
find "$HOME" -type f \( -name "*.gguf" -o -name "*.GGUF" \) 2>/dev/null | head -50

echo
echo "===== PROCESSOS ====="
ps -ef | grep -E 'llama-server|llama-cli' | grep -v grep || true

echo
echo "===== PORTA 8080 ====="
curl -sS -m 3 http://127.0.0.1:8080/health || true

echo
echo "===== FIM ====="
