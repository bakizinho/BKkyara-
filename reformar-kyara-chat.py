from pathlib import Path
from datetime import datetime
import re

ROOT = Path.home() / "nazuna"
IA = ROOT / "dados/src/funcs/private/ia.js"

if not IA.exists():
    raise SystemExit("❌ ia.js não encontrado.")

text = IA.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = IA.with_name(f"ia.js.backup-chat-{timestamp}")
backup.write_text(text, encoding="utf-8")

print(f"💾 Backup: {backup}")

# ============================================================
# 1. CONFIGURAÇÃO
# ============================================================

text = re.sub(
    r"const AI_MAX_TOKENS\s*=\s*\d+\s*;",
    "const AI_MAX_TOKENS = 160;",
    text,
    count=1
)

text = re.sub(
    r"const AI_TEMPERATURE\s*=\s*[\d.]+\s*;",
    "const AI_TEMPERATURE = 0.82;",
    text,
    count=1
)

# ============================================================
# 2. NOVO MOTOR CONVERSACIONAL
# ============================================================

marker = "// ============================================================================\n// LOCAL AI"

if marker not in text:
    raise SystemExit("❌ Marcador LOCAL AI não encontrado.")

novo_motor = r'''
// ============================================================================
// KYARA — MOTOR CONVERSACIONAL ESTRUTURADO
// ============================================================================

const KYARA_CHAT_URL = `${LOCAL_AI_URL}/v1/chat/completions`;

const KYARA_MAX_HISTORY = 10;

function normalizarKyaraTexto(texto) {
  if (typeof texto !== 'string') return '';

  let t = texto
    .replace(/\r/g, '')
    .replace(/\0/g, '')
    .trim();

  // Remove prefixos de roteiro que modelos pequenos costumam criar.
  t = t.replace(
    /^(Kyara|Assistente|Assistant|Resposta|Resposta da Kyara)\s*:\s*/i,
    ''
  );

  // Remove cercas de markdown isoladas.
  t = t.replace(/^```(?:text|txt)?\s*/i, '');
  t = t.replace(/\s*```$/i, '');

  return t.trim();
}

function limitarHistoricoKyara(lista = []) {
  if (!Array.isArray(lista)) return [];

  return lista
    .filter(item => item && typeof item === 'object')
    .slice(-KYARA_MAX_HISTORY);
}

function construirKyaraSystemPrompt({
  personalidade = '',
  intencao = '',
  memoria = {},
  contexto = {}
} = {}) {

  return `
Você é Kyara, uma assistente pessoal de inteligência artificial que conversa pelo WhatsApp.

IDENTIDADE:
- Nome: Kyara.
- Fala português brasileiro.
- Tem uma personalidade espontânea, curiosa, divertida e inteligente.
- Não precisa usar emoji em toda resposta.
- Não precisa usar gírias em toda resposta.
- Não deve fingir ser uma pessoa humana real.
- Se perguntarem diretamente se você é uma IA, diga claramente que sim.

REGRA MAIS IMPORTANTE:
RESPONDA A MENSAGEM ATUAL.

Não responda uma pergunta diferente.
Não invente uma pergunta.
Não peça informações que já estão na mensagem.
Não mude de assunto sem motivo.

COMPORTAMENTO:
- Se a mensagem for simples, responda de forma simples.
- Se a mensagem pedir explicação, explique.
- Se pedir opinião, dê opinião.
- Se pedir informação, forneça a informação que conhece.
- Se não souber, diga que não sabe.
- Se houver ambiguidade real, faça somente uma pergunta curta.
- Não faça perguntas apenas para continuar a conversa.
- Não termine automaticamente com "posso ajudar em mais alguma coisa?".
- Não diga "entendi sua pergunta" sem necessidade.
- Não repita a pergunta do usuário.
- Não transforme toda resposta em lista.
- Não invente fatos.

ESTILO WHATSAPP:
Escreva naturalmente.
Varie o tamanho das frases.
Use pontuação normal.
Pode usar "kkk", "mds", "oxe", "ué", "mano", "sério?" quando realmente combinar.
Não force essas expressões.
Emojis são opcionais.

PRECISÃO:
Não invente nomes, fatos, datas ou informações.
Não finja saber algo que não sabe.

INTENÇÃO DETECTADA:
${String(intencao || 'CONVERSA')}

MEMÓRIA DISPONÍVEL:
${JSON.stringify(memoria).slice(0, 3000)}

CONTEXTO:
${JSON.stringify(contexto).slice(0, 3000)}

PERSONALIDADE EXTRA:
${String(personalidade || '').slice(0, 2000)}

FORMATO DA RESPOSTA:
Retorne SOMENTE a mensagem que Kyara enviaria ao usuário.
Não escreva:
"Kyara:"
"Assistente:"
"Resposta:"
"Usuário:"
"Mensagem:"
Não escreva análise.
Não escreva instruções.
Não escreva JSON.
`.trim();
}

async function makeKyaraChatRequest({
  mensagem,
  historico = [],
  personalidade = '',
  intencao = 'CONVERSA',
  memoria = {},
  contexto = {}
} = {}) {

  if (!mensagem || typeof mensagem !== 'string') {
    throw new Error('Mensagem Kyara inválida.');
  }

  const messages = [
    {
      role: 'system',
      content: construirKyaraSystemPrompt({
        personalidade,
        intencao,
        memoria,
        contexto
      })
    }
  ];

  for (const item of limitarHistoricoKyara(historico)) {

    if (
      item.role !== 'user' &&
      item.role !== 'assistant'
    ) {
      continue;
    }

    const content =
      typeof item.content === 'string'
        ? item.content.trim()
        : '';

    if (!content) continue;

    messages.push({
      role: item.role,
      content
    });
  }

  messages.push({
    role: 'user',
    content: mensagem.trim()
  });

  console.log(
    `🧠 [KYARA CHAT] intenção=${intencao} histórico=${messages.length - 2}`
  );

  try {

    const response = await axios.post(
      KYARA_CHAT_URL,
      {
        model: LOCAL_AI_MODEL,
        messages,
        max_tokens: AI_MAX_TOKENS,
        temperature: AI_TEMPERATURE,
        top_p: 0.90,
        top_k: 30,
        min_p: 0.05,
        repeat_penalty: 1.12,
        stream: false
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: AI_TIMEOUT,
        validateStatus: status =>
          status >= 200 && status < 300
      }
    );

    const content =
      response?.data?.choices?.[0]?.message?.content ||
      response?.data?.choices?.[0]?.text ||
      '';

    const resposta = normalizarKyaraTexto(content);

    if (!resposta) {
      throw new Error('Modelo retornou resposta vazia.');
    }

    return {
      data: {
        choices: [
          {
            message: {
              content: resposta
            }
          }
        ]
      }
    };

  } catch (error) {

    console.warn(
      '⚠️ [KYARA CHAT] Falha no /v1/chat/completions:',
      error?.message || error
    );

    // ========================================================
    // FALLBACK PARA /completion
    // ========================================================

    const promptFallback = `
${construirKyaraSystemPrompt({
  personalidade,
  intencao,
  memoria,
  contexto
})}

CONVERSA RECENTE:
${limitarHistoricoKyara(historico)
  .map(x =>
    `${x.role === 'user' ? 'Usuário' : 'Kyara'}: ${x.content}`
  )
  .join('\n')}

MENSAGEM ATUAL:
${mensagem}

KYARA:
`.trim();

    const fallback =
      await makeLocalAIRequest(
        promptFallback,
        AI_MAX_TOKENS,
        AI_TEMPERATURE,
        1
      );

    const content =
      fallback?.data?.content ||
      fallback?.data?.choices?.[0]?.text ||
      fallback?.data?.choices?.[0]?.message?.content ||
      '';

    const resposta =
      normalizarKyaraTexto(content);

    if (!resposta) {
      throw new Error(
        'Fallback também retornou resposta vazia.'
      );
    }

    return {
      data: {
        choices: [
          {
            message: {
              content: resposta
            }
          }
        ]
      }
    };
  }
}

'''

text = text.replace(
    marker,
    novo_motor + "\n" + marker,
    1
)

# ============================================================
# 3. EXPOR FUNÇÃO
# ============================================================

export_marker = "processUserMessages as makeAssistentRequest"

if export_marker in text:
    text = text.replace(
        export_marker,
        "processUserMessages as makeAssistentRequest",
        1
    )

# Adiciona export nomeado perto do final.
if "export { makeKyaraChatRequest" not in text:
    text += """

export {
  makeKyaraChatRequest
};
"""

IA.write_text(text, encoding="utf-8")

print("✅ Motor conversacional instalado.")
print("✅ /v1/chat/completions configurado.")
print("✅ Fallback /completion preservado.")
print("✅ Histórico limitado.")
print("✅ Prompt estruturado.")
print("✅ Respostas limpas.")
print("✅ Backup criado.")
