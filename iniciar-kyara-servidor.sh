#!/data/data/com.termux/files/usr/bin/bash

set -u

echo "=============================================="
echo "🌸 KYARA — INICIAR SERVIDOR LOCAL"
echo "=============================================="

SERVER=""

for candidato in \
    "$HOME/kyara-ai/llama.cpp/build/bin/llama-server" \
    "$HOME/kyara-ai/llama.cpp/build/llama-server" \
    "$HOME/kyara-ai/llama.cpp/llama-server" \
    "$HOME/llama.cpp/build/bin/llama-server" \
    "$HOME/llama.cpp/build/llama-server" \
    "$HOME/llama.cpp/llama-server"
do
    if [ -x "$candidato" ]; then
        SERVER="$candidato"
        break
    fi
done

if [ -z "$SERVER" ]; then
    SERVER="$(find "$HOME" -type f -name llama-server -perm -111 2>/dev/null | head -n 1)"
fi

if [ -z "$SERVER" ]; then
    echo "❌ llama-server não encontrado."
    exit 1
fi

MODEL=""

for candidato in \
    "$HOME/kyara-ai/models/qwen2.5-0.5b-instruct-q4_k_m.gguf" \
    "$HOME/kyara-ai/model/qwen2.5-0.5b-instruct-q4_k_m.gguf" \
    "$HOME/kyara-ai/qwen2.5-0.5b-instruct-q4_k_m.gguf" \
    "$HOME/nazuna/qwen2.5-0.5b-instruct-q4_k_m.gguf"
do
    if [ -f "$candidato" ]; then
        MODEL="$candidato"
        break
    fi
done

if [ -z "$MODEL" ]; then
    MODEL="$(find "$HOME" -type f \( -name 'qwen2.5-0.5b-instruct-q4_k_m.gguf' -o -iname '*qwen*0.5b*.gguf' \) 2>/dev/null | head -n 1)"
fi

if [ -z "$MODEL" ]; then
    echo "❌ Modelo Qwen não encontrado."
    exit 1
fi

pkill -f 'llama-server' 2>/dev/null || true
sleep 1

echo "SERVER=$SERVER"
echo "MODEL=$MODEL"
echo

"$SERVER" \
    -m "$MODEL" \
    --host 127.0.0.1 \
    --port 8080 \
    -c 2048 \
    -ngl 0 \
    --threads 4 \
    --parallel 1 \
    > "$HOME/nazuna/kyara-llama-server.log" 2>&1 &

PID=$!

echo "$PID" > "$HOME/nazuna/kyara-llama-server.pid"

echo "PID=$PID"
echo "LOG=$HOME/nazuna/kyara-llama-server.log"

echo
echo "Aguardando servidor..."

for i in $(seq 1 30); do
    if curl -fsS -m 2 http://127.0.0.1:8080/health >/dev/null 2>&1; then
        echo
        echo "✅ SERVIDOR ONLINE"
        echo
        curl -sS http://127.0.0.1:8080/v1/models
        exit 0
    fi

    sleep 1
done

echo
echo "❌ Servidor não respondeu."
echo
tail -80 "$HOME/nazuna/kyara-llama-server.log"
exit 1
