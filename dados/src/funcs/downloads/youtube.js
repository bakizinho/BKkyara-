import { execFile } from 'child_process'
import { promisify } from 'util'
import fs from 'fs'
import os from 'os'
import path from 'path'

const execFileAsync = promisify(execFile)

function limparNome(nome) {
  return String(nome || 'audio')
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120) || 'audio'
}

function segundos(duracao) {
  if (typeof duracao === 'number') return duracao

  const partes = String(duracao || '').split(':').map(Number)

  if (partes.some(Number.isNaN)) return 0

  if (partes.length === 3) {
    return partes[0] * 3600 + partes[1] * 60 + partes[2]
  }

  if (partes.length === 2) {
    return partes[0] * 60 + partes[1]
  }

  return partes[0] || 0
}

function formatarDuracao(valor) {
  const total = segundos(valor)

  if (!total) return 'Desconhecida'

  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = Math.floor(total % 60)

  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }

  return `${m}:${String(s).padStart(2, '0')}`
}

async function executarYtDlp(args) {
  try {
    const { stdout, stderr } = await execFileAsync(
      'yt-dlp',
      args,
      {
        maxBuffer: 10 * 1024 * 1024
      }
    )

    return {
      stdout: stdout?.trim() || '',
      stderr: stderr?.trim() || ''
    }

  } catch (error) {
    const mensagem =
      error?.stderr?.trim() ||
      error?.stdout?.trim() ||
      error?.message ||
      'Erro desconhecido do yt-dlp'

    throw new Error(mensagem)
  }
}

function extrairJson(stdout) {
  const linhas = String(stdout)
    .split('\n')
    .map(l => l.trim())
    .filter(Boolean)

  for (const linha of linhas) {
    try {
      return JSON.parse(linha)
    } catch {}
  }

  throw new Error('yt-dlp não retornou informações válidas')
}

/**
 * Pesquisa no YouTube sem API.
 *
 * Exemplo:
 * search('Back to Black')
 */
async function search(query) {
  try {
    if (!query?.trim()) {
      return {
        ok: false,
        msg: 'Digite o nome do vídeo ou música.'
      }
    }

    const resultado = await executarYtDlp([
      '--no-playlist',
      '--flat-playlist',
      '--dump-single-json',
      `ytsearch1:${query.trim()}`
    ])

    const dados = extrairJson(resultado.stdout)

    const video = dados?.entries?.[0]

    if (!video?.id) {
      return {
        ok: false,
        msg: 'Nenhum vídeo encontrado.'
      }
    }

    const url =
      video.webpage_url ||
      video.url ||
      `https://www.youtube.com/watch?v=${video.id}`

    return {
      ok: true,
      data: {
        videoId: video.id,
        url,
        title: video.title || 'Vídeo sem título',
        description: video.description || '',
        thumbnail:
          video.thumbnail ||
          `https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`,
        seconds: segundos(video.duration),
        timestamp: formatarDuracao(video.duration),
        views: video.view_count || 0,
        ago: video.upload_date || '',
        author: {
          name: video.uploader || video.channel || 'YouTube'
        }
      }
    }

  } catch (err) {
    console.error('[YOUTUBE SEARCH]', err)

    return {
      ok: false,
      msg: 'Não foi possível pesquisar no YouTube: ' + err.message
    }
  }
}

/**
 * Baixa áudio e converte para MP3 usando yt-dlp + FFmpeg.
 */
async function mp3(url) {
  const pasta = path.join(
    process.cwd(),
    '.tmp-youtube',
    `audio-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  )

  fs.mkdirSync(pasta, {
    recursive: true
  })

  try {
    const saida = path.join(
      pasta,
      'audio.%(ext)s'
    )

    await executarYtDlp([
      '--no-playlist',
      '--no-warnings',
      '-f',
      'bestaudio/best',
      '--extract-audio',
      '--audio-format',
      'mp3',
      '--audio-quality',
      '128K',
      '--no-part',
      '--output',
      saida,
      url
    ])

    const arquivos = fs.readdirSync(pasta)

    const arquivo = arquivos.find(
      nome => nome.toLowerCase().endsWith('.mp3')
    )

    if (!arquivo) {
      throw new Error('O áudio não foi gerado pelo FFmpeg.')
    }

    const caminho = path.join(pasta, arquivo)
    const buffer = fs.readFileSync(caminho)

    if (!buffer.length) {
      throw new Error('O arquivo de áudio ficou vazio.')
    }

    return {
      ok: true,
      buffer,
      title: 'YouTube Audio',
      thumbnail: '',
      filename: 'audio.mp3'
    }

  } catch (err) {
    console.error('[YOUTUBE MP3]', err)

    return {
      ok: false,
      msg: err.message
    }

  } finally {
    try {
      fs.rmSync(pasta, {
        recursive: true,
        force: true
      })
    } catch {}
  }
}

/**
 * Baixa vídeo MP4 usando yt-dlp + FFmpeg.
 */
async function mp4(url) {
  const pasta = fs.mkdtempSync(
    path.join(os.tmpdir(), 'nazuna-youtube-video-')
  )

  try {
    const saida = path.join(pasta, 'video.%(ext)s')

    await executarYtDlp([
      '--no-playlist',
      '--no-warnings',
      '-f',
      'bv*+ba/b',
      '--merge-output-format',
      'mp4',
      '--no-part',
      '--output',
      saida,
      url
    ])

    const arquivos = fs.readdirSync(pasta)

    const arquivo = arquivos.find(
      nome => nome.toLowerCase().endsWith('.mp4')
    )

    if (!arquivo) {
      throw new Error('O vídeo MP4 não foi gerado.')
    }

    const caminho = path.join(pasta, arquivo)
    const buffer = fs.readFileSync(caminho)

    if (!buffer.length) {
      throw new Error('O arquivo de vídeo ficou vazio.')
    }

    let titulo = 'YouTube Video'

    try {
      const info = await executarYtDlp([
        '--no-playlist',
        '--print',
        '%(title)s',
        url
      ])

      titulo = info.stdout.split('\n')[0]?.trim() || titulo
    } catch {}

    return {
      ok: true,
      buffer,
      title: titulo,
      thumbnail: '',
      filename: `${limparNome(titulo)}.mp4`
    }

  } catch (err) {
    console.error('[YOUTUBE MP4]', err)

    return {
      ok: false,
      msg: err.message
    }

  } finally {
    try {
      fs.rmSync(pasta, {
        recursive: true,
        force: true
      })
    } catch {}
  }
}

export {
  search,
  mp3,
  mp4
}

export const ytmp3 = mp3
