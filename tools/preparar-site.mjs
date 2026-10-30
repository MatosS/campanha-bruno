import fs from "node:fs/promises"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { createHash } from "node:crypto"
import { createRequire } from "node:module"

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const site = path.join(root, "site")
const source = path.join(root, "conteudo")
const target = path.join(site, "content")
const require = createRequire(path.join(site, "package.json"))
const YAML = require("yaml")
const marker = path.join(site, ".campanha-stage.json")
const posix = (s) => s.split(path.sep).join("/")
const hash = (s) => createHash("sha256").update(s).digest("hex")
async function* files(dir) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) yield* files(full)
    else if (entry.isFile()) yield full
  }
}

// Only this explicitly generated directory can be cleared. Never write to conteudo/.
if (target !== path.resolve(root, "site/content")) throw new Error("Destino de preparação inválido")
const previous = await fs.readdir(target).catch(() => [])
const owned = await fs.access(marker).then(() => true, () => false)
if (!owned && previous.some((s) => s !== ".gitkeep")) throw new Error("A pasta site/content contém arquivos não gerados")
await fs.rm(target, { recursive: true, force: true })
await fs.mkdir(target, { recursive: true })
await fs.writeFile(marker, JSON.stringify({ source: posix(source), generated: posix(target) }))

const manifest = { source: "conteudo/", quartz: "5.0.0", notes: [], attachments: 0, externalFiles: [], broken: [] }
const copies = new Map()
for await (const full of files(source)) {
  const rel = posix(path.relative(source, full))
  const dest = path.join(target, rel)
  await fs.mkdir(path.dirname(dest), { recursive: true })
  const bytes = await fs.readFile(full)
  if (!rel.endsWith(".md")) {
    await fs.writeFile(dest, bytes)
    manifest.attachments++
    continue
  }
  const raw = bytes.toString("utf8")
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/)
  if (!match) throw new Error(`Metadados ausentes: ${rel}`)
  const meta = YAML.parse(match[1])
  if (meta.publico === false) continue
  meta.title = meta.titulo || path.basename(rel, ".md")
  meta.lang = "pt-BR"
  if (meta.atualizado) meta.modified = meta.atualizado
  if (rel.startsWith("Fontes/")) meta.tags = [...(meta.tags || []), "acervo-fonte"]
  if (rel.startsWith("Pendencias/")) meta.tags = [...(meta.tags || []), "acervo-revisao"]
  if (meta.tipo === "indice") meta.tags = [...(meta.tags || []), "navegacao"]
  let body = raw.slice(match[0].length)
  // Quartz renders the title itself; keep the same title without duplicating the H1.
  body = body.replace(/^\s*# [^\r\n]+\r?\n/, "\n")
  body = body.replace(/(!?\[[^\]\n]*\]\()(<[^>\n]*>|[^)\n]+)(\))/g, (all, before, href, after) => {
    const bare = href.startsWith("<") ? href.slice(1, -1) : href
    if (/^(?:[a-z]+:|#|\/\/)/i.test(bare)) return all
    const [file, anchor] = bare.split(/#(.*)/s)
    let decoded
    try { decoded = decodeURIComponent(file) } catch { return all }
    const resolved = path.resolve(path.dirname(full), decoded)
    if (resolved === source || resolved.startsWith(source + path.sep)) {
      const localTarget = posix(path.relative(source, resolved))
      return before + "<" + localTarget + (anchor ? "#" + anchor : "") + ">" + after
    }
    if (!resolved.startsWith(root + path.sep)) {
      manifest.broken.push({ from: rel, href: bare, reason: "fora do projeto" })
      return all
    }
    const local = posix(path.relative(root, resolved))
    let staged = "Acervo/Arquivos/" + local
    if (staged.endsWith(".md")) staged += ".txt"
    copies.set(resolved, staged)
    return before + "<" + staged + (anchor ? "#" + anchor : "") + ">" + after
  })
  await fs.writeFile(dest, "---\n" + YAML.stringify(meta).trimEnd() + "\n---\n" + body)
  manifest.notes.push({ path: rel, sha256: hash(bytes), title: meta.title })
}
for (const [from, staged] of copies) {
  try {
    const dest = path.join(target, staged)
    await fs.mkdir(path.dirname(dest), { recursive: true })
    await fs.copyFile(from, dest)
    manifest.externalFiles.push({ from: posix(path.relative(root, from)), to: staged })
  } catch (err) { manifest.broken.push({ from: posix(path.relative(root, from)), reason: err.code }) }
}
await fs.writeFile(path.join(target, "index.md"), `---
title: Atlas das campanhas
tipo: indice
campanhas: [fash, glim]
description: Explore as conexões entre personagens, lugares e acontecimentos das campanhas de Fash e Glim.
cssclasses: [atlas-home]
---

## Duas épocas, uma história

[[Campanhas/Glim|Glim — a campanha em andamento]] · [[Campanhas/Fash|Fash — setenta anos antes]]

Comece por uma conexão no grafo ou pesquise um nome. As cores distinguem os tipos de nota; os filtros de campanha seguem as épocas documentadas nas notas.

[[Sessoes/Indice|Ler os diários de Glim]] · [[Inicio|Consultar os índices da base]] · [[Fontes/Indice|Abrir as fontes]] · [[Pendencias/Indice|Revisão de continuidade]]
`)
await fs.mkdir(path.join(root, "docs/site"), { recursive: true })
await fs.writeFile(path.join(root, "docs/site/conteudo-manifesto.json"), JSON.stringify(manifest, null, 2) + "\n")
if (manifest.broken.length) throw new Error(`Há ${manifest.broken.length} arquivos externos ausentes; consulte docs/site/conteudo-manifesto.json`)
console.log(JSON.stringify({ notes: manifest.notes.length, attachments: manifest.attachments, externalFiles: copies.size, originalsChanged: 0 }))
