from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path("dados/src")
IA = ROOT / "funcs/private/ia.js"

if not IA.exists():
    raise SystemExit("❌ ia.js não encontrado.")

print()
print("=" * 70)
print("🌸 KYARA — REFORMA PROFUNDA DO MOTOR DE CONVERSA")
print("=" * 70)

# ============================================================
# BACKUP
# ============================================================

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(f"ia.js.backup-motor-{stamp}")
shutil.copy2(IA, backup)

print(f"💾 Backup criado: {backup}")

text = IA.read_text(encoding="utf-8")

# ============================================================
# 1. CONFIGURAÇÃO DO MOTOR
# ============================================================

text, n = re.subn(
    r"const AI_MAX_TOKENS = \d+;",
    "const AI_MAX_TOKENS = 96;",
    text,
    count=1
)

if n:
    print("✅ AI_MAX_TOKENS: 24 → 96")
else:
    print("⚠️ AI_MAX_TOKENS não encontrado")

# ============================================================
# 2. TEMPERATURA
# ============================================================

text, n = re.subn(
    r"const AI_TEMPERATURE = [0-9.]+;",
    "const AI_TEMPERATURE = 0.78;",
    text,
    count=1
)

if n:
    print("✅ Temperatura ajustada")

# ============================================================
# 3. NOVAS REGRAS DE CONVERSA
# ============================================================

marker = "// KYARA NATURAL CONVERSATION RULES"

if marker in text:

    start = text.index("const KYARA_NATURAL_RULES = `")
    end = text.index("`;", start) + 2

    new_rules = r'''const KYARA_NATURAL_RULES = `
KYARA — REGRAS DE CONVERSA

IDENTIDADE
Você é Kyara, uma assistente pessoal de IA.
Seu nome é Kyara.
Você conversa em português brasileiro.

PERSONALIDADE
- extrovertida
- curiosa
- divertida
- inteligente
- espontânea
- carinhosa quando apropriado
- pode demonstrar surpresa, dúvida, entusiasmo ou discordância

REGRA MAIS IMPORTANTE
RESPONDA PRIMEIRO À MENSAGEM ATUAL.

Antes de responder:
1. descubra o que a pessoa está perguntando;
2. identifique o assunto principal;
3. use o histórico apenas para entender o contexto;
4. responda exatamente ao que foi perguntado.

NÃO CONFUNDA:
- mensagem anterior com mensagem atual;
- contexto com pergunta;
- informação de memória com uma nova pergunta;
- exemplo dado pelo usuário com uma ordem;
- comentário do usuário com uma pergunta.

RESPOSTA
- Se a pergunta estiver clara, responda diretamente.
- Não peça confirmação sem necessidade.
- Não faça uma pergunta no final só para continuar conversa.
- Não diga "entendi" automaticamente.
- Não repita a pergunta.
- Não mude de assunto.
- Não invente informações.
- Se não souber, diga que não sabe.
- Se houver informação suficiente, não peça mais dados.

NATURALIDADE
Escreva como uma conversa normal no WhatsApp.

Evite:
"Claro! Com certeza!"
"Entendi perfeitamente sua pergunta."
"Espero que isso tenha ajudado."
"Posso ajudar em mais alguma coisa?"

Não use essas frases automaticamente.

Pode usar:
"kkk"
"mds"
"oxe"
"ué"
"sério?"
"slk"
"vdd"

Mas somente quando combinar com a situação.

EXPRESSIVIDADE
A resposta não precisa ser fria.

Pode demonstrar:
- surpresa;
- curiosidade;
- entusiasmo;
- humor;
- dúvida;
- opinião;
- preocupação apropriada.

Mas não exagere.

INFORMAÇÃO
Quando a pessoa pedir informação:
- entregue a informação;
- explique de maneira simples;
- dê exemplos quando forem úteis;
- não responda apenas com uma frase vazia.

Quando a pergunta for simples:
responda curto.

Quando a pergunta for complexa:
explique melhor.

CONVERSA
Não transforme tudo em lista.
Não transforme tudo em piada.
Não faça perguntas desnecessárias.
Não invente fatos para parecer inteligente.
Não finja saber algo que não sabe.

IDENTIDADE SOBRE IA
Se perguntarem diretamente se você é uma IA:
diga claramente que sim.

Não fale espontaneamente sobre:
- tokens;
- prompts;
- servidores;
- APIs;
- algoritmos;
- código;
- modelo;
- sistema interno.

`;
'''

    text = text[:start] + new_rules + text[end:]

    print("✅ Regras naturais reconstruídas")

else:
    print("⚠️ Bloco KYARA_NATURAL_RULES não localizado")

# ============================================================
# 4. STOP TOKENS
# ============================================================

old_stop = """          stop: [
            '\\nUsuário:',
            '\\nUser:',
            '\\nKyara:',
            '\\nAssistente:',
            '\\nSYSTEM:',
            '\\n---'
          ]"""

new_stop = """          stop: [
            '\\nUsuário:',
            '\\nUser:',
            '\\nAssistente:',
            '\\nSYSTEM:',
            '\\n###',
            '\\n---'
          ]"""

if old_stop in text:
    text = text.replace(old_stop, new_stop, 1)
    print("✅ Stop tokens corrigidos")
else:
    print("⚠️ Bloco de stop tokens não encontrado")

# ============================================================
# 5. PROMPT DE CONTEXTO MAIS CLARO
# ============================================================

old_context = """      const contexto =
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
        });"""

new_context = """      const historicoRecente =
        (historico[userId] || [])
          .slice(-6);

      const contexto =
        JSON.stringify({
          tarefa: "responder_mensagem",
          usuario: msg.nome_enviou || "usuário",
          grupo: msg.nome_grupo || null,
          horario: hour,

          memoria: userContext,

          historico_recente: historicoRecente,

          mensagem_atual: msg.texto,

          instrucao:
            "Responda SOMENTE à mensagem_atual. " +
            "Use historico_recente e memoria apenas como contexto. " +
            "Não faça perguntas desnecessárias."
        });"""

if old_context in text:
    text = text.replace(old_context, new_context, 1)
    print("✅ Contexto reorganizado")
else:
    print("⚠️ Contexto antigo não encontrado")

# ============================================================
# 6. REFORÇO ANTES DA CHAMADA LOCAL
# ============================================================

old_call = """      const response =
        await makeCognimaRequest(
          LOCAL_AI_MODEL,
          contexto,
          systemPrompt,
          historico[userId] || [],
          1
        );"""

new_call = """      const promptConversacional =
        `${systemPrompt}

${KYARA_NATURAL_RULES}

DADOS DA CONVERSA:
${contexto}

REGRA FINAL:
Responda diretamente à mensagem_atual.
Não responda ao histórico.
Não crie uma pergunta desnecessária.
Não invente informação.
Seja natural, clara e útil.

RESPOSTA:`;

      const response =
        await makeCognimaRequest(
          LOCAL_AI_MODEL,
          promptConversacional,
          null,
          [],
          1
        );"""

if old_call in text:
    text = text.replace(old_call, new_call, 1)
    print("✅ Chamada do modelo reorganizada")
else:
    print("⚠️ Chamada principal não encontrada")

# ============================================================
# 7. LIMPEZA DE RESPOSTA
# ============================================================

marker = "// ================================================================\n      // RESPOSTA"

if marker in text and "function limparRespostaKyara" not in text:

    helper = r'''
// ============================================================================
// LIMPEZA DE RESPOSTA DA KYARA
// ============================================================================

function limparRespostaKyara(texto) {
  if (typeof texto !== 'string') return '';

  let resposta = texto
    .replace(/^["']|["']$/g, '')
    .replace(/^Kyara:\s*/i, '')
    .replace(/^Assistente:\s*/i, '')
    .trim();

  // Remove estruturas artificiais comuns
  resposta = resposta
    .replace(/^Resposta:\s*/i, '')
    .replace(/^Mensagem:\s*/i, '')
    .trim();

  // Evita respostas absurdamente repetitivas
  resposta = resposta.replace(
    /(\b.{3,80}\b)(?:\s+\1){2,}/gi,
    '$1'
  );

  return resposta.trim();
}

'''

    text = text.replace(
        "// ============================================================================\n// PROCESSAMENTO PRINCIPAL",
        helper + "// ============================================================================\n// PROCESSAMENTO PRINCIPAL",
        1
    )

    print("✅ Limpador de respostas adicionado")

# ============================================================
# 8. APLICAR LIMPEZA NO CONTENT
# ============================================================

old_content = """      const content =
        response
          ?.data
          ?.choices?.[0]
          ?.message?.content;"""

new_content = """      const content =
        limparRespostaKyara(
          response
            ?.data
            ?.choices?.[0]
            ?.message?.content || ''
        );"""

if old_content in text:
    text = text.replace(old_content, new_content, 1)
    print("✅ Limpeza aplicada ao resultado")

# ============================================================
# 9. VALIDAÇÃO
# ============================================================

IA.write_text(text, encoding="utf-8")

print()
print("=" * 70)
print("🧪 REFORMA GRAVADA")
print("=" * 70)
print()
print("Arquivo:", IA)
print("Backup :", backup)
print()

