from pathlib import Path
from datetime import datetime
import re

ROOT = Path.home() / "nazuna"

IA = ROOT / "dados/src/funcs/private/ia.js"

if not IA.exists():
    raise SystemExit("❌ ia.js não encontrado.")

text = IA.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(
    f"ia.js.backup-final-connect-{timestamp}"
)

backup.write_text(text, encoding="utf-8")

print("💾 Backup:", backup)

# ----------------------------------------------------------------------
# Encontrar processUserMessages
# ----------------------------------------------------------------------

inicio = re.search(
    r"async\s+function\s+processUserMessages\s*\(",
    text
)

if not inicio:
    raise SystemExit(
        "❌ processUserMessages não encontrado."
    )

print(
    "✅ processUserMessages encontrado na linha:",
    text[:inicio.start()].count("\n") + 1
)

# ----------------------------------------------------------------------
# Localizar chamada makeCognimaRequest
# ----------------------------------------------------------------------

padrao = re.compile(
    r"""
    const\s+response\s*=\s*
    await\s+makeCognimaRequest\s*\(
        \s*LOCAL_AI_MODEL\s*, 
        \s*contexto\s*, 
        \s*systemPrompt\s*, 
        \s*historico\[userId\]\s*\|\|\s*\[\]\s*, 
        \s*1\s*
    \);
    """,
    re.MULTILINE | re.VERBOSE
)

m = padrao.search(text)

if not m:

    print()
    print("⚠️ A chamada antiga NÃO foi encontrada.")
    print()
    print("Chamadas existentes:")

    for x in re.finditer(
        r"makeCognimaRequest\s*\(",
        text
    ):
        line = text[:x.start()].count("\n") + 1
        print("  linha", line)

    print()
    print("❌ Nada foi alterado.")
    print("Backup:", backup)

    raise SystemExit(0)

# ----------------------------------------------------------------------
# Nova chamada
# ----------------------------------------------------------------------

novo = """const respostaChat =
        await makeKyaraChatRequest({
          mensagem: msg.texto,
          historico: historico[userId] || [],
          personalidade: personality,
          intencao: contexto?.intencao || 'CONVERSA',
          memoria: userContext,
          contexto: {
            usuario: msg.nome_enviou,
            grupo: msg.nome_grupo || null,
            horario: hour,
            mensagem: msg.texto
          }
        });

      const response = respostaChat;"""

text = text[:m.start()] + novo + text[m.end():]

IA.write_text(text, encoding="utf-8")

print()
print("✅ CHAMADA PRINCIPAL REFORMADA")
print("   processUserMessages → makeKyaraChatRequest")
print("   mensagem atual enviada separadamente")
print("   histórico enviado separadamente")
print("   memória enviada separadamente")
print("   contexto enviado separadamente")
print()
print("💾 Backup:", backup)
