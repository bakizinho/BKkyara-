#!/data/data/com.termux/files/usr/bin/bash

echo "=== CONFIGURAR GRADIUM ==="
echo

printf "Cole sua API Key do Gradium: "
read -r GRADIUM_API_KEY

if [ -z "$GRADIUM_API_KEY" ]; then
  echo "❌ API Key vazia."
  exit 1
fi

export GRADIUM_API_KEY
export GRADIUM_VOICE_ID="KgC2Nqnjj48NUiyV"

echo
echo "✅ API Key carregada."
echo "🎙️ Voice ID: $GRADIUM_VOICE_ID"
echo

node dados/src/funcs/tts/testar-voz.js

STATUS=$?

echo

if [ "$STATUS" -eq 0 ]; then
  echo "✅ TESTE CONCLUÍDO"
else
  echo "❌ TESTE FALHOU"
fi

exit "$STATUS"
