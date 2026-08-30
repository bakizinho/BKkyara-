from pathlib import Path
import re
from datetime import datetime

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"

text = IA.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(f"ia.js.backup-history-{timestamp}")
backup.write_text(text, encoding="utf-8")

# Procura a função updateHistorico.
m = re.search(
    r"function\s+updateHistorico\s*\(",
    text
)

if not m:
    print("⚠️ updateHistorico não encontrado.")
    print("Backup:", backup)
    raise SystemExit(0)

print("✅ updateHistorico encontrado na linha aproximada:",
      text[:m.start()].count("\n") + 1)

print()
print("⚠️ Nenhuma alteração automática será feita nesta etapa.")
print("O histórico precisa ser analisado para não destruir a memória existente.")
print("Backup:", backup)
