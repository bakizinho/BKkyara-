#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/nazuna"
GAMES_DIR="$BASE/src/html-games/games"
SERVER_FILE="$BASE/src/html-games/server.js"

clear

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              🎮 NAZUNA — INVENTÁRIO DE JOGOS            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# VERIFICAÇÃO DO PROJETO
# ============================================================

if [ ! -d "$BASE" ]; then
  echo "❌ Projeto Nazuna não encontrado:"
  echo "   $BASE"
  exit 1
fi

if [ ! -d "$GAMES_DIR" ]; then
  echo "❌ Pasta de jogos não encontrada:"
  echo "   $GAMES_DIR"
  exit 1
fi

# ============================================================
# DEPENDÊNCIAS DO PACKAGE.JSON
# ============================================================

echo "📦 DEPENDÊNCIAS DO NAZUNA"
echo "──────────────────────────────────────────────────────────"

if [ -f "$BASE/package.json" ]; then

  node --input-type=module <<'NODE'
import fs from "fs";

const file = process.env.HOME + "/nazuna/package.json";

try {
  const pkg = JSON.parse(fs.readFileSync(file, "utf8"));

  const deps = {
    ...(pkg.dependencies || {}),
    ...(pkg.devDependencies || {})
  };

  const names = Object.keys(deps).sort();

  if (!names.length) {
    console.log("  • Nenhuma dependência externa encontrada.");
  } else {
    for (const name of names) {
      console.log(`  • ${name} ${deps[name]}`);
    }
  }

} catch (error) {
  console.log("❌ Erro ao ler package.json");
  console.log("   " + error.message);
}
NODE

else
  echo "⚠️ package.json não encontrado."
fi

echo ""

# ============================================================
# FUNÇÃO: DESCOBRIR PACOTES INSTALADOS
# ============================================================

check_package() {

  PKG="$1"

  # Remove prefixos comuns
  CLEAN="$PKG"

  case "$CLEAN" in
    node:*)
      CLEAN="${CLEAN#node:}"
      ;;
  esac

  # Pacotes @scope/pacote
  if [[ "$CLEAN" == @*/* ]]; then
    PACKAGE_PATH="$BASE/node_modules/$CLEAN"
  else
    PACKAGE_PATH="$BASE/node_modules/$CLEAN"
  fi

  if [ -d "$PACKAGE_PATH" ]; then
    echo "│    ✅ $CLEAN — instalado"
  else
    echo "│    ❌ $CLEAN — NÃO encontrado"
  fi
}

# ============================================================
# CONTADOR
# ============================================================

COUNT=0

echo "══════════════════════════════════════════════════════════"
echo "🎮 JOGOS ENCONTRADOS"
echo "══════════════════════════════════════════════════════════"
echo ""

# ============================================================
# ANALISA CADA HTML
# ============================================================

for FILE in "$GAMES_DIR"/*.html; do

  [ -e "$FILE" ] || continue

  NAME="$(basename "$FILE" .html)"

  COUNT=$((COUNT + 1))

  echo "┌──────────────────────────────────────────────────────────"
  echo "│ 🎮 ARQUIVO: $NAME.html"
  echo "├──────────────────────────────────────────────────────────"

  # ----------------------------------------------------------
  # TITLE
  # ----------------------------------------------------------

  TITLE=$(grep -oiE '<title[^>]*>[^<]+' "$FILE" \
    | head -1 \
    | sed -E 's/<title[^>]*>//I')

  if [ -n "$TITLE" ]; then
    echo "│ 🏷️  Título: $TITLE"
  else
    echo "│ 🏷️  Título: $NAME"
  fi

  # ----------------------------------------------------------
  # H1
  # ----------------------------------------------------------

  H1=$(grep -oiE '<h1[^>]*>[^<]+' "$FILE" \
    | head -1 \
    | sed -E 's/<h1[^>]*>//I')

  if [ -n "$H1" ]; then
    echo "│ 🎨 Nome visual: $H1"
  fi

  # ----------------------------------------------------------
  # DESCRIÇÃO
  # ----------------------------------------------------------

  DESCRIPTION=$(grep -oiE \
    '<meta[^>]+name=["'\'']description["'\''][^>]+content=["'\''][^"'\'']+' \
    "$FILE" \
    | head -1 \
    | sed -E 's/.*content=["'\'']([^"'\'']+).*/\1/I')

  if [ -n "$DESCRIPTION" ]; then
    echo "│ 📝 Descrição: $DESCRIPTION"
  fi

  # ----------------------------------------------------------
  # CANVAS
  # ----------------------------------------------------------

  if grep -qi '<canvas' "$FILE"; then
    echo "│ 🎨 Canvas: SIM"
  else
    echo "│ 🎨 Canvas: NÃO"
  fi

  # ----------------------------------------------------------
  # JAVASCRIPT
  # ----------------------------------------------------------

  if grep -qi '<script' "$FILE"; then
    echo "│ ⚙️  JavaScript: SIM"
  else
    echo "│ ⚙️  JavaScript: NÃO"
  fi

  # ----------------------------------------------------------
  # CSS
  # ----------------------------------------------------------

  if grep -qi '<style' "$FILE"; then
    echo "│ 🎨 CSS interno: SIM"
  else
    echo "│ 🎨 CSS interno: NÃO"
  fi

  # ----------------------------------------------------------
  # BIBLIOTECAS EXTERNAS
  # ----------------------------------------------------------

  echo "│"
  echo "│ 📦 BIBLIOTECAS EXTERNAS:"

  EXTERNAL_URLS=$(grep -oE \
    'https?://[^"'\'']+' \
    "$FILE" \
    | sort -u)

  if [ -n "$EXTERNAL_URLS" ]; then

    echo "$EXTERNAL_URLS" | while read -r URL; do
      echo "│    🌐 $URL"
    done

  else
    echo "│    • Nenhuma biblioteca externa detectada"
  fi

  # ----------------------------------------------------------
  # IMPORTS JAVASCRIPT
  # ----------------------------------------------------------

  echo "│"
  echo "│ 📥 IMPORTS JAVASCRIPT:"

  IMPORTS=$(grep -oE \
    '(from[[:space:]]+["'\''][^"'\'']+["'\'']|import[[:space:]]*["'\''][^"'\'']+["'\''])' \
    "$FILE" \
    | sort -u)

  if [ -n "$IMPORTS" ]; then

    echo "$IMPORTS" | while read -r LINE; do

      DEP=$(echo "$LINE" \
        | sed -nE 's/.*from[[:space:]]*["'\'']([^"'\'']+)["'\''].*/\1/p')

      if [ -z "$DEP" ]; then
        DEP=$(echo "$LINE" \
          | sed -nE 's/.*import[[:space:]]*["'\'']([^"'\'']+)["'\''].*/\1/p')
      fi

      if [[ "$DEP" == "."* || "$DEP" == "/"* ]]; then
        echo "│    🧩 Interno: $DEP"
      else
        echo "│    📦 Externo: $DEP"
      fi

    done

  else
    echo "│    • Nenhum import detectado"
  fi

  # ----------------------------------------------------------
  # REQUIRE
  # ----------------------------------------------------------

  REQUIRES=$(grep -oE \
    'require\(["'\''][^"'\'']+["'\'']\)' \
    "$FILE" \
    | sed -E 's/require\(["'\'']([^"'\'']+)["'\'']\)/\1/' \
    | sort -u)

  if [ -n "$REQUIRES" ]; then

    echo "│"
    echo "│ 📦 REQUIRE:"

    echo "$REQUIRES" | while read -r DEP; do

      if [[ "$DEP" == "."* || "$DEP" == "/"* ]]; then
        echo "│    🧩 Interno: $DEP"
      else
        echo "│    📦 Externo: $DEP"
      fi

    done
  fi

  # ----------------------------------------------------------
  # STORAGE / LOCALSTORAGE
  # ----------------------------------------------------------

  if grep -qiE 'localStorage|sessionStorage|indexedDB' "$FILE"; then
    echo "│"
    echo "│ 💾 ARMAZENAMENTO:"
    echo "│    ✅ Usa armazenamento local do navegador"
  fi

  # ----------------------------------------------------------
  # ÁUDIO
  # ----------------------------------------------------------

  if grep -qiE '<audio|Audio\(|new Audio' "$FILE"; then
    echo "│"
    echo "│ 🔊 ÁUDIO:"
    echo "│    ✅ Sistema de áudio detectado"
  fi

  # ----------------------------------------------------------
  # TOUCH
  # ----------------------------------------------------------

  if grep -qiE \
    'touchstart|touchmove|touchend|pointerdown|pointerup' \
    "$FILE"; then

    echo "│"
    echo "│ 📱 CONTROLE:"
    echo "│    ✅ Controles touch/pointer detectados"
  fi

  # ----------------------------------------------------------
  # TECLADO
  # ----------------------------------------------------------

  if grep -qiE \
    'keydown|keyup|keypress' \
    "$FILE"; then

    echo "│"
    echo "│ ⌨️  TECLADO:"
    echo "│    ✅ Controles por teclado detectados"
  fi

  # ----------------------------------------------------------
  # SERVIDOR / INTEGRAÇÃO NAZUNA
  # ----------------------------------------------------------

  if [ -f "$SERVER_FILE" ]; then

    if grep -qi "$NAME" "$SERVER_FILE"; then
      echo "│"
      echo "│ 🔌 SERVIDOR NAZUNA:"
      echo "│    ✅ Jogo registrado no server.js"
    else
      echo "│"
      echo "│ 🔌 SERVIDOR NAZUNA:"
      echo "│    ⚠️ Nome não encontrado no server.js"
    fi

  fi

  # ----------------------------------------------------------
  # ARQUIVOS RELACIONADOS
  # ----------------------------------------------------------

  echo "│"
  echo "│ 📁 ARQUIVOS RELACIONADOS:"

  RELATED=$(grep -Ril \
    "$NAME" \
    "$BASE/src/html-games" \
    --include="*.js" \
    --include="*.json" \
    2>/dev/null \
    | sed "s|$BASE/||" \
    | head -20)

  if [ -n "$RELATED" ]; then
    echo "$RELATED" | while read -r R; do
      echo "│    • $R"
    done
  else
    echo "│    • Nenhum arquivo relacionado encontrado"
  fi

  # ----------------------------------------------------------
  # TAMANHO
  # ----------------------------------------------------------

  SIZE=$(du -h "$FILE" 2>/dev/null | awk '{print $1}')

  echo "│"
  echo "│ 📏 Tamanho: $SIZE"

  # ----------------------------------------------------------
  # TIPO
  # ----------------------------------------------------------

  echo "│"
  echo "│ 🧱 Tipo: HTML GAME"

  if grep -qi '<canvas' "$FILE"; then
    echo "│ 🎮 Motor: HTML5 Canvas"
  elif grep -qiE '<button|onclick|addEventListener' "$FILE"; then
    echo "│ 🎮 Motor: HTML/JavaScript"
  else
    echo "│ 🎮 Motor: HTML"
  fi

  echo "└──────────────────────────────────────────────────────────"
  echo ""

done

# ============================================================
# RESUMO
# ============================================================

echo "══════════════════════════════════════════════════════════"
echo "📊 RESUMO DO NAZUNA"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "🎮 Total de jogos HTML: $COUNT"
echo ""

# ============================================================
# LISTA SIMPLES
# ============================================================

echo "🎮 LISTA RÁPIDA"
echo "──────────────────────────────────────────────────────────"

if [ "$COUNT" -gt 0 ]; then

  NUM=0

  for FILE in "$GAMES_DIR"/*.html; do

    [ -e "$FILE" ] || continue

    NUM=$((NUM + 1))

    NAME="$(basename "$FILE" .html)"

    TITLE=$(grep -oiE '<title[^>]*>[^<]+' "$FILE" \
      | head -1 \
      | sed -E 's/<title[^>]*>//I')

    [ -z "$TITLE" ] && TITLE="$NAME"

    echo "  $NUM. 🎮 $NAME — $TITLE"

  done

else

  echo "  ⚠️ Nenhum jogo encontrado."

fi

echo ""

# ============================================================
# ARQUIVOS DO SISTEMA DE JOGOS
# ============================================================

echo "🧩 SISTEMA HTML-GAMES"
echo "──────────────────────────────────────────────────────────"

if [ -f "$SERVER_FILE" ]; then
  echo "  ✅ server.js encontrado"
  echo "     $SERVER_FILE"
else
  echo "  ⚠️ server.js não encontrado"
fi

HELPER="$GAMES_DIR/_htmlGameCommand.js"

if [ -f "$HELPER" ]; then
  echo "  ✅ _htmlGameCommand.js encontrado"
  echo "     $HELPER"
else
  echo "  ⚠️ _htmlGameCommand.js não encontrado"
fi

echo ""

# ============================================================
# DEPENDÊNCIAS NODE INSTALADAS
# ============================================================

echo "📦 STATUS DO NODE_MODULES"
echo "──────────────────────────────────────────────────────────"

if [ -d "$BASE/node_modules" ]; then

  echo "  ✅ node_modules existe"

  if [ -f "$BASE/package.json" ]; then

    node --input-type=module <<'NODE'
import fs from "fs";

const base = process.env.HOME + "/nazuna";
const pkgFile = base + "/package.json";

try {

  const pkg = JSON.parse(fs.readFileSync(pkgFile, "utf8"));

  const deps = {
    ...(pkg.dependencies || {}),
    ...(pkg.devDependencies || {})
  };

  let installed = 0;
  let missing = 0;

  for (const name of Object.keys(deps)) {

    if (fs.existsSync(base + "/node_modules/" + name)) {
      installed++;
    } else {
      missing++;
    }

  }

  console.log(`  ✅ Dependências instaladas: ${installed}`);
  console.log(`  ❌ Dependências ausentes: ${missing}`);

} catch (error) {

  console.log("  ⚠️ Não foi possível verificar todas as dependências.");

}

NODE

  fi

else

  echo "  ❌ node_modules não existe"

fi

echo ""

# ============================================================
# FINAL
# ============================================================

echo "══════════════════════════════════════════════════════════"
echo "✅ ANÁLISE DO NAZUNA CONCLUÍDA"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "📂 Jogos:"
echo "   $GAMES_DIR"
echo ""
echo "📂 Projeto:"
echo "   $BASE"
echo ""
