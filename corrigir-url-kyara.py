from pathlib import Path
import re
from datetime import datetime

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"

if not IA.exists():
    raise SystemExit("❌ ia.js não encontrado.")

text = IA.read_text(encoding="utf-8")

backup = IA.with_name(
    f"ia.js.backup-url-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
)
backup.write_text(text, encoding="utf-8")

# Remove definição anterior.
text = re.sub(
    r"const\s+KYARA_CHAT_URL\s*=\s*[^;]+;",
    "const KYARA_CHAT_URL = 'http://127.0.0.1:8080/v1/chat/completions';",
    text,
    count=1
)

if "const KYARA_CHAT_URL" not in text:
    marcador = "// ============================================================================\n// KYARA — MOTOR CONVERSACIONAL"
    if marcador in text:
        text = text.replace(
            marcador,
            "const KYARA_CHAT_URL = 'http://127.0.0.1:8080/v1/chat/completions';\n\n" + marcador,
            1
        )
    else:
        text = (
            "const KYARA_CHAT_URL = 'http://127.0.0.1:8080/v1/chat/completions';\n"
            + text
        )

IA.write_text(text, encoding="utf-8")

print("✅ KYARA_CHAT_URL corrigida.")
print("http://127.0.0.1:8080/v1/chat/completions")
print("💾 Backup:", backup)
