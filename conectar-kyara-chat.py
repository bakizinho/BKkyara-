from pathlib import Path
import re
from datetime import datetime

ROOT = Path.home() / "nazuna"

IA = ROOT / "dados/src/funcs/private/ia.js"
CORE = ROOT / "dados/src/core/kyara.js"

if not IA.exists():
    raise SystemExit("❌ ia.js não encontrado.")

text = IA.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(f"ia.js.backup-connect-{timestamp}")
backup.write_text(text, encoding="utf-8")

# ============================================================
# LOCALIZAR CHAMADA ATUAL
# ============================================================

padrao = re.compile(
    r"""const response\s*=\s*await\s+makeCognimaRequest\s*\(
\s*LOCAL_AI_MODEL,
\s*contexto,
\s*systemPrompt,
\s*historico\[userId\]\s*\|\|\s*\[\],
\s*1
\s*\);""",
    re.MULTILINE
)

if not padrao.search(text):
    print("⚠️ Chamada antiga não encontrada exatamente.")
    print("O script NÃO vai modificar o bloco automaticamente.")
    print("Backup criado:", backup)
    raise SystemExit(0)

novo = """const intencaoAtual =
        contexto?.intencao ||
        'CONVERSA';

      const respostaChat =
        await makeKyaraChatRequest({
          mensagem: msg.texto,
          historico: historico[userId] || [],
          personalidade: systemPrompt,
          intencao: intencaoAtual,
          memoria: userContext,
          contexto: {
            nome: msg.nome_enviou,
            grupo: msg.nome_grupo || null,
            horario: hour
          }
        });

      const response = respostaChat;"""

text = padrao.sub(novo, text, count=1)

# ============================================================
# PROTEGER CONTRA USO DE CONTEXTO COMO PERGUNTA
# ============================================================

text = text.replace(
"""const contexto =
        JSON.stringify({
          usuario:
            msg.nome_enviou,

          memoria:
            userContext,

          mensagem:
            msg.texto,

          horario:
            hour,

          grupo:
            msg.nome_grupo || null
        });""",
"""const contexto =
        {
          usuario: msg.nome_enviou,
          memoria: userContext,
          mensagem: msg.texto,
          horario: hour,
          grupo: msg.nome_grupo || null,
          intencao: 'CONVERSA'
        };""",
1
)

# ============================================================
# SYSTEM PROMPT NÃO DEVE SER USADO COMO MENSAGEM DO USUÁRIO
# ============================================================

IA.write_text(text, encoding="utf-8")

print("✅ processUserMessages conectado ao motor conversacional.")
print("✅ Contexto mantido separado da mensagem.")
print("💾 Backup:", backup)
