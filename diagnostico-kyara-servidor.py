from pathlib import Path
import subprocess
import urllib.request
import urllib.error
import json
import re

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"
CORE = ROOT / "dados/src/core/kyara.js"
INDEX = ROOT / "dados/src/index.js"
LLAMA = ROOT / "llama.cpp"

print("=" * 78)
print("🌸 KYARA — DIAGNÓSTICO REAL DO PIPELINE")
print("=" * 78)

def request(method, url, data=None):
    try:
        req = urllib.request.Request(
            url,
            method=method,
            headers={"Content-Type": "application/json"}
        )

        body = None
        if data is not None:
            body = json.dumps(data).encode()

        with urllib.request.urlopen(req, data=body, timeout=8) as r:
            raw = r.read().decode("utf-8", errors="replace")
            return r.status, raw

    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, raw

    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def show_endpoint(name, method, url, data=None):
    print()
    print(f"🔌 {name}")
    print(f"   {method} {url}")

    status, body = request(method, url, data)

    print(f"   HTTP: {status}")

    if body:
        print("   RESPOSTA:")
        print(body[:3000])
    else:
        print("   ⚠️ Nenhum corpo retornado.")

# ----------------------------------------------------------------------
# ARQUIVOS
# ----------------------------------------------------------------------

print()
print("📁 ARQUIVOS")

for label, path in [
    ("IA", IA),
    ("CORE", CORE),
    ("INDEX", INDEX),
    ("LLAMA.CPP", LLAMA),
]:
    print(f"{'✅' if path.exists() else '❌'} {label}: {path}")

# ----------------------------------------------------------------------
# PROCESSOS
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("🧠 PROCESSOS LLAMA")
print("=" * 78)

try:
    result = subprocess.run(
        ["sh", "-c", "ps -ef | grep -E 'llama-server|llama-cli' | grep -v grep"],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print(result.stdout)
    else:
        print("❌ Nenhum llama-server/llama-cli encontrado.")
except Exception as e:
    print("⚠️ Não foi possível consultar processos:", e)

# ----------------------------------------------------------------------
# PORTA
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("🌐 SERVIDOR 127.0.0.1:8080")
print("=" * 78)

show_endpoint(
    "ROOT",
    "GET",
    "http://127.0.0.1:8080/"
)

show_endpoint(
    "HEALTH",
    "GET",
    "http://127.0.0.1:8080/health"
)

show_endpoint(
    "MODELS",
    "GET",
    "http://127.0.0.1:8080/v1/models"
)

show_endpoint(
    "PROPS",
    "GET",
    "http://127.0.0.1:8080/props"
)

# ----------------------------------------------------------------------
# TESTE CHAT
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("💬 TESTE CHAT")
print("=" * 78)

chat = {
    "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
    "messages": [
        {
            "role": "system",
            "content": (
                "Você é Kyara. "
                "Responda em português brasileiro. "
                "Responda somente à pergunta do usuário. "
                "Não faça perguntas desnecessárias."
            )
        },
        {
            "role": "user",
            "content": "Oi Kyara, tudo bem?"
        }
    ],
    "max_tokens": 80,
    "temperature": 0.75,
    "stream": False
}

show_endpoint(
    "CHAT COMPLETIONS",
    "POST",
    "http://127.0.0.1:8080/v1/chat/completions",
    chat
)

# ----------------------------------------------------------------------
# TESTE COMPLETION
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("📝 TESTE COMPLETION")
print("=" * 78)

completion = {
    "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
    "prompt": (
        "Você é Kyara, uma assistente pessoal.\n"
        "Usuário: Oi Kyara, tudo bem?\n"
        "Kyara:"
    ),
    "n_predict": 80,
    "temperature": 0.75,
    "stream": False
}

show_endpoint(
    "COMPLETION",
    "POST",
    "http://127.0.0.1:8080/completion",
    completion
)

# ----------------------------------------------------------------------
# IA.JS
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("🔎 IA.JS")
print("=" * 78)

if IA.exists():
    text = IA.read_text(encoding="utf-8", errors="ignore")

    patterns = [
        "makeKyaraChatRequest",
        "makeCognimaRequest",
        "makeLocalAIRequest",
        "processUserMessages",
        "AI_MAX_TOKENS",
        "KYARA_CHAT_URL",
        "v1/chat/completions",
        "localhost:8080",
        "127.0.0.1:8080",
        "limparRespostaKyara",
        "promptConversacional",
    ]

    for p in patterns:
        print(f"{'✅' if p in text else '❌'} {p}")

    print()
    print("📌 CHAMADAS PARA makeCognimaRequest:")

    for m in re.finditer(r"makeCognimaRequest\s*\(", text):
        line = text[:m.start()].count("\n") + 1
        print("   linha", line)

    print()
    print("📌 CHAMADAS PARA makeKyaraChatRequest:")

    for m in re.finditer(r"makeKyaraChatRequest\s*\(", text):
        line = text[:m.start()].count("\n") + 1
        print("   linha", line)

# ----------------------------------------------------------------------
# CORE
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("🧩 CORE")
print("=" * 78)

if CORE.exists():
    text = CORE.read_text(encoding="utf-8", errors="ignore")

    for p in [
        "kyaraCore",
        "entenderIntencao",
        "montarContexto",
        "mensagemComContexto",
        "makeAssistentRequest",
    ]:
        print(f"{'✅' if p in text else '❌'} {p}")

# ----------------------------------------------------------------------
# INDEX
# ----------------------------------------------------------------------

print()
print("=" * 78)
print("📱 INDEX")
print("=" * 78)

if INDEX.exists():
    text = INDEX.read_text(encoding="utf-8", errors="ignore")

    print("kyaraCore:", text.count("kyaraCore"))
    print("makeAssistentRequest:", text.count("makeAssistentRequest"))

    for m in re.finditer(r"kyaraCore\s*\(", text):
        line = text[:m.start()].count("\n") + 1
        print("   kyaraCore() linha", line)

print()
print("=" * 78)
print("🌸 DIAGNÓSTICO TERMINADO")
print("=" * 78)
