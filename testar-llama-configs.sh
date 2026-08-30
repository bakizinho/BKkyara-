#!/data/data/com.termux/files/usr/bin/bash

set -u

SERVER="$HOME/kyara-ai/llama.cpp/build/bin/llama-server"
MODEL="$HOME/kyara-ai/models/qwen2.5-0.5b-instruct-q4_k_m.gguf"

echo "=============================================="
echo "🌸 KYARA — TESTE DE COMPATIBILIDADE LLAMA"
echo "=============================================="

if [ ! -x "$SERVER" ]; then
    echo "❌ llama-server não encontrado:"
    echo "$SERVER"
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    echo "❌ Modelo não encontrado:"
    echo "$MODEL"
    exit 1
fi

echo
echo "SERVER:"
echo "$SERVER"

echo
echo "MODEL:"
echo "$MODEL"

echo
echo "===== VERSÃO ====="
"$SERVER" --version 2>&1 | head -40 || true

echo
echo "===== PARANDO SERVIDORES ANTIGOS ====="
pkill -f 'llama-server' 2>/dev/null || true
sleep 2

run_test() {
    NAME="$1"
    shift

    PORT=8080

    LOG="$HOME/nazuna/llama-test-${NAME}.log"

    echo
    echo "=============================================="
    echo "🧪 TESTE: $NAME"
    echo "=============================================="

    rm -f "$LOG"

    "$SERVER" \
        -m "$MODEL" \
        --host 127.0.0.1 \
        --port "$PORT" \
        "$@" \
        >"$LOG" 2>&1 &

    PID=$!

    echo "PID=$PID"
    echo "LOG=$LOG"

    sleep 2

    if ! kill -0 "$PID" 2>/dev/null; then
        echo "❌ PROCESSO MORREU"

        echo
        echo "----- LOG -----"
        cat "$LOG" 2>/dev/null | tail -80

        return 1
    fi

    echo "✅ PROCESSO CONTINUA EXECUTANDO"

    for i in $(seq 1 10); do
        if curl -fsS -m 2 \
            http://127.0.0.1:8080/health \
            >/dev/null 2>&1; then

            echo
            echo "🎉 SERVIDOR ONLINE!"
            echo

            curl -sS \
                http://127.0.0.1:8080/v1/models

            echo
            echo
            echo "PID=$PID"

            echo
            echo "===== TESTE DE CHAT ====="

            curl -sS -m 60 \
                http://127.0.0.1:8080/v1/chat/completions \
                -H "Content-Type: application/json" \
                -d '{
                    "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é Kyara, uma assistente pessoal de inteligência artificial. Responda em português brasileiro de forma natural."
                        },
                        {
                            "role": "user",
                            "content": "Oi Kyara, tudo bem?"
                        }
                    ],
                    "max_tokens": 64,
                    "temperature": 0.7,
                    "stream": false
                }'

            echo
            echo
            echo "=============================================="
            echo "✅ CONFIGURAÇÃO FUNCIONANDO: $NAME"
            echo "=============================================="

            echo
            echo "Para manter este servidor:"
            echo "PID=$PID"

            return 0
        fi

        sleep 1
    done

    echo
    echo "❌ SERVIDOR NÃO ABRIU A PORTA"

    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null || true
    fi

    echo
    echo "----- LOG -----"
    cat "$LOG" 2>/dev/null | tail -100

    return 1
}

# ============================================================
# TESTE 1 — MÍNIMO
# ============================================================

if run_test "01-minimo" \
    -c 512 \
    -ngl 0 \
    --threads 1 \
    --parallel 1
then
    exit 0
fi

pkill -f 'llama-server' 2>/dev/null || true
sleep 2

# ============================================================
# TESTE 2 — 1024 CONTEXTO
# ============================================================

if run_test "02-ctx1024" \
    -c 1024 \
    -ngl 0 \
    --threads 1 \
    --parallel 1
then
    exit 0
fi

pkill -f 'llama-server' 2>/dev/null || true
sleep 2

# ============================================================
# TESTE 3 — 2048 CONTEXTO / 2 THREADS
# ============================================================

if run_test "03-ctx2048" \
    -c 2048 \
    -ngl 0 \
    --threads 2 \
    --parallel 1
then
    exit 0
fi

pkill -f 'llama-server' 2>/dev/null || true
sleep 2

# ============================================================
# TESTE 4 — SEM --parallel
# ============================================================

if run_test "04-sem-parallel" \
    -c 1024 \
    -ngl 0 \
    --threads 2
then
    exit 0
fi

pkill -f 'llama-server' 2>/dev/null || true
sleep 2

echo
echo "=============================================="
echo "❌ NENHUMA CONFIGURAÇÃO FUNCIONOU"
echo "=============================================="

echo
echo "Logs disponíveis:"
ls -lh "$HOME/nazuna"/llama-test-*.log 2>/dev/null || true

exit 1
