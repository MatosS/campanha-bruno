import http from "node:http"
import fs from "node:fs"
import path from "node:path"
import handler from "serve-handler"
import { build, site } from "./build.mjs"

if (!process.argv.includes("--no-build") && !build()) process.exit(1)
const port = Number(process.env.PORT || 8080)
const output = path.join(site, "public")
const server = http.createServer((req, res) => handler(req, res, {
  public: output, cleanUrls: true, directoryListing: false,
  headers: [{ source: "**", headers: [{ key: "Cache-Control", value: "no-store" }] }],
}))
server.on("error", err => { console.error(err.message); process.exitCode = 1 })
server.listen(port, "127.0.0.1", () => {
  console.log(`Prévia local: http://127.0.0.1:${port}`)
  fs.writeFileSync(path.join(site, ".preview.json"), JSON.stringify({ pid: process.pid, port, url: `http://127.0.0.1:${port}`, started: new Date().toISOString() }))
})
let timer
function rebuild() {
  clearTimeout(timer)
  timer = setTimeout(() => {
    console.log("Alterações encontradas. Atualizando a prévia…")
    if (build()) console.log("Prévia atualizada. Recarregue o navegador.")
    else console.error("Falha ao atualizar. Veja o erro acima.")
  }, 700)
}
const watchers = [
  fs.watch(path.resolve(site, "../conteudo"), { recursive: true }, rebuild),
  fs.watch(path.join(site, "campanha"), { recursive: true }, rebuild),
  fs.watch(path.join(site, "quartz/styles/custom.scss"), rebuild),
  fs.watch(path.join(site, "quartz.config.yaml"), rebuild),
  fs.watch(path.join(site, "quartz.ts"), rebuild),
]
function close() { watchers.forEach(w => w.close()); clearTimeout(timer); server.close(); process.exit(0) }
process.on("SIGINT", close);process.on("SIGTERM", close)
