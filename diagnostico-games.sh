#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/nazuna"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║             🎮 NAZUNA — DIAGNÓSTICO GAMES               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "📁 ESTRUTURA DO DADOS/SRC"
echo "──────────────────────────────────────────────────────────"

find "$BASE/dados/src" -maxdepth 4 -type f \
  \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" \) \
  2>/dev/null \
  | sort

echo ""
echo "══════════════════════════════════════════════════════════"
echo "🚀 START.JS"
echo "══════════════════════════════════════════════════════════"

if [ -f "$BASE/dados/src/.scripts/start.js" ]; then
  sed -n '1,260p' "$BASE/dados/src/.scripts/start.js"
else
  echo "❌ start.js não encontrado"
fi

echo ""
echo "══════════════════════════════════════════════════════════"
echo "🔎 CARREGADORES DE COMANDOS"
echo "══════════════════════════════════════════════════════════"

grep -RniE \
  'commands|command|readdir|readdirSync|import\(|require\(|handler|message|prefix' \
  "$BASE/dados/src" \
  --include="*.js" \
  --include="*.mjs" \
  --include="*.cjs" \
  2>/dev/null \
  | head -300

echo ""
echo "══════════════════════════════════════════════════════════"
echo "🎮 REFERÊNCIAS A HTML-GAMES"
echo "══════════════════════════════════════════════════════════"

grep -RniE \
  'html-games|gameLoader|startHtmlGameServer|breakout|richsnake|richxo|rich2048|pianorich|pong|dino' \
  "$BASE" \
  --include="*.js" \
  --include="*.mjs" \
  --include="*.cjs" \
  2>/dev/null \
  | head -300

echo ""
echo "══════════════════════════════════════════════════════════"
echo "🎮 HTML GAMES"
echo "══════════════════════════════════════════════════════════"

find "$BASE/src/html-games" -maxdepth 3 -type f \
  2>/dev/null \
  | sort

echo ""
echo "══════════════════════════════════════════════════════════"
echo "📦 PACKAGE"
echo "══════════════════════════════════════════════════════════"

node -e "
const p=require('./package.json');
console.log('Nome:',p.name);
console.log('Versão:',p.version);
console.log('Start:',p.scripts?.start);
console.log('Main:',p.main);
"

echo ""
echo "══════════════════════════════════════════════════════════"
echo "✅ DIAGNÓSTICO TERMINADO"
echo "══════════════════════════════════════════════════════════"
