#!/data/data/com.termux/files/usr/bin/bash

set -u

echo "🌸 Iniciando servidor Kyara..."

./iniciar-kyara-servidor.sh

STATUS=$?

if [ "$STATUS" -ne 0 ]; then
    echo "❌ Servidor Kyara não iniciou."
    exit "$STATUS"
fi

echo
echo "🌸 Servidor confirmado."
echo "🌸 Iniciando Nazuna..."
echo

node dados/src/.scripts/start.js
