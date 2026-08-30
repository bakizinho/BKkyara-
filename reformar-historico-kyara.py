from pathlib import Path
from datetime import datetime
import re

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"

text = IA.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(
    f"ia.js.backup-history-final-{timestamp}"
)

backup.write_text(text, encoding="utf-8")

print("💾 Backup:", backup)

# ----------------------------------------------------------------------
# Encontrar updateHistorico
# ----------------------------------------------------------------------

m = re.search(
    r"function\s+updateHistorico\s*\(",
    text
)

if not m:
    raise SystemExit(
        "❌ updateHistorico não encontrado."
    )

start = m.start()

# Encontrar o próximo bloco de função em nível simples.
# Em vez de tentar adivinhar o corpo antigo, usamos uma região
# delimitada pelo próximo comentário de seção.
next_section = re.search(
    r"\n//\s*=+\n",
    text[m.end():]
)

if not next_section:
    raise SystemExit(
        "❌ Não foi possível delimitar updateHistorico com segurança."
    )

end = m.end() + next_section.start()

nova_funcao = r'''
function updateHistorico(
  grupoUserId,
  role,
  texto,
  nome = null
) {
  if (!grupoUserId) return;
  if (typeof texto !== 'string') return;

  const content = texto.trim();

  if (!content) return;

  if (!historico[grupoUserId]) {
    historico[grupoUserId] = [];
  }

  if (role !== 'user' && role !== 'assistant') {
    return;
  }

  historico[grupoUserId].push({
    role,
    content,
    nome: nome || null,
    timestamp: Date.now()
  });

  // Mantém somente as últimas 10 mensagens.
  historico[grupoUserId] =
    historico[grupoUserId].slice(-10);
}

'''

text = text[:start] + nova_funcao + text[end:]

IA.write_text(text, encoding="utf-8")

print("✅ updateHistorico substituído.")
print("✅ Histórico agora usa roles user/assistant.")
print("✅ Máximo de 10 mensagens.")
print("💾 Backup:", backup)
