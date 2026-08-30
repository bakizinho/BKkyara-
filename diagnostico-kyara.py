from pathlib import Path
import re

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"
CORE = ROOT / "dados/src/core/kyara.js"
INDEX = ROOT / "dados/src/index.js"
EXPORTS = ROOT / "dados/src/funcs/exports.js"
KYARA_OLD = ROOT / "dados/src/funcs/private/ia_kyara.js"

print("=" * 75)
print("🌸 KYARA — DIAGNÓSTICO PROFUNDO")
print("=" * 75)

arquivos = {
    "IA PRINCIPAL": IA,
    "CORE": CORE,
    "INDEX": INDEX,
    "EXPORTS": EXPORTS,
    "IA_KYARA": KYARA_OLD,
}

for nome, path in arquivos.items():
    print()
    print(f"📄 {nome}")
    print(f"   {path}")
    print(f"   existe: {path.exists()}")

    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        print(f"   linhas: {len(text.splitlines())}")
        print(f"   bytes : {len(text.encode('utf-8'))}")

print()
print("=" * 75)
print("🔎 MOTOR PRINCIPAL")
print("=" * 75)

if IA.exists():
    text = IA.read_text(encoding="utf-8", errors="ignore")

    checks = {
        "makeCognimaRequest": r"\bmakeCognimaRequest\b",
        "makeLocalAIRequest": r"\bmakeLocalAIRequest\b",
        "processUserMessages": r"\bprocessUserMessages\b",
        "AI_MAX_TOKENS": r"AI_MAX_TOKENS",
        "AI_TEMPERATURE": r"AI_TEMPERATURE",
        "/completion": r"['\"]/completion['\"]",
        "/v1/chat/completions": r"/v1/chat/completions",
        "historico": r"\bhistorico\b",
        "limparRespostaKyara": r"\blimparRespostaKyara\b",
        "promptConversacional": r"\bpromptConversacional\b",
        "KYARA_NATURAL_RULES": r"KYARA_NATURAL_RULES",
        "KYARA_PERSONALITY_SYSTEM": r"KYARA_PERSONALITY_SYSTEM",
    }

    for nome, pattern in checks.items():
        encontrados = len(re.findall(pattern, text, re.I))
        estado = "✅" if encontrados else "❌"
        print(f"{estado} {nome}: {encontrados}")

print()
print("=" * 75)
print("🔎 CORE")
print("=" * 75)

if CORE.exists():
    text = CORE.read_text(encoding="utf-8", errors="ignore")

    for termo in [
        "kyaraCore",
        "entenderIntencao",
        "montarContexto",
        "makeAssistentRequest",
        "mensagemComContexto",
    ]:
        print(
            ("✅" if termo in text else "❌"),
            termo
        )

print()
print("=" * 75)
print("🔎 INDEX")
print("=" * 75)

if INDEX.exists():
    text = INDEX.read_text(encoding="utf-8", errors="ignore")

    print(
        "kyaraCore:",
        text.count("kyaraCore")
    )

    print(
        "makeAssistentRequest:",
        text.count("makeAssistentRequest")
    )

print()
print("=" * 75)
print("🔎 EXPORTS")
print("=" * 75)

if EXPORTS.exists():
    text = EXPORTS.read_text(encoding="utf-8", errors="ignore")

    print(
        "Ponte processUserMessages:",
        "processUserMessages" in text
    )

    print(
        "Ponte makeCognimaRequest:",
        "makeCognimaRequest" in text
    )

print()
print("=" * 75)
print("🌸 DIAGNÓSTICO FINALIZADO")
print("=" * 75)
