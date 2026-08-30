from pathlib import Path
import re

IA = Path.home() / "nazuna/dados/src/funcs/private/ia.js"

text = IA.read_text(encoding="utf-8")

print("===== KYARA EXPORT =====")

defs = len(re.findall(r"\bfunction\s+makeKyaraChatRequest\b", text))
exports = len(re.findall(r"\bmakeKyaraChatRequest\b", text))

print("Definições:", defs)
print("Referências:", exports)

m = re.search(
    r"export\s*\{[\s\S]*?makeKyaraChatRequest[\s\S]*?\};",
    text
)

if m:
    print("✅ Export encontrado:")
    print(m.group(0))
else:
    print("❌ Export nomeado NÃO encontrado.")
