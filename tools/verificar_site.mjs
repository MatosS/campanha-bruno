import fs from "node:fs/promises"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { createHash } from "node:crypto"
import { createRequire } from "node:module"

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..")
const output=path.join(root,"site/public")
const require=createRequire(path.join(root,"site/package.json"))
const YAML=require("yaml")
const config=YAML.parse(await fs.readFile(path.join(root,"site/quartz.config.yaml"),"utf8"))
const basePath=new URL(`https://${config.configuration.baseUrl || "localhost"}`).pathname.replace(/\/$/,"")
async function* walk(dir) { for(const e of await fs.readdir(dir,{withFileTypes:true})) {const p=path.join(dir,e.name);if(e.isDirectory())yield* walk(p);else yield p} }
const all=[];for await(const p of walk(output))all.push(p)
const names=new Set(all.map(p=>path.relative(output,p).split(path.sep).join("/")))
const broken=[];let localLinks=0,htmlCount=0
for(const full of all.filter(p=>p.endsWith(".html"))) {
  htmlCount++
  const rel=path.relative(output,full).split(path.sep).join("/")
  const html=await fs.readFile(full,"utf8")
  for(const m of html.matchAll(/(?:href|src)="([^"]*)"/g)) {
    let href=m[1].replaceAll("&amp;","&")
    if(!href||/^(?:[a-z]+:|#|\/\/)/i.test(href))continue
    href=href.split(/[?#]/)[0]
    try {href=decodeURIComponent(href)}catch{continue}
    // The Pages 404 page uses site-absolute assets, including the repository prefix.
    if(basePath && (href===basePath || href.startsWith(basePath+"/")))href=href.slice(basePath.length) || "/"
    const target=path.posix.normalize(href.startsWith("/")?href.slice(1):path.posix.join(path.posix.dirname(rel),href)).replace(/\/$/,"")
    localLinks++
    if(![target,target+".html",target+"/index.html"].some(t=>names.has(t)) && !(target==="."&&names.has("index.html"))) broken.push({from:rel,href:m[1],target})
  }
}
const manifest=JSON.parse(await fs.readFile(path.join(root,"docs/site/conteudo-manifesto.json"),"utf8"))
const changed=[]
for(const n of manifest.notes) {
  const bytes=await fs.readFile(path.join(root,"conteudo",n.path))
  if(createHash("sha256").update(bytes).digest("hex")!==n.sha256)changed.push(n.path)
}
const atlas=JSON.parse(await fs.readFile(path.join(output,"static/atlas.json"),"utf8"))
const data=JSON.parse(await fs.readFile(path.join(output,"static/contentIndex.json"),"utf8"))
const noteCount=Object.keys(data).length
const failures=[]
if(noteCount<manifest.notes.length)failures.push("Notas ausentes no índice de busca")
if(!atlas.nodes.some(n=>n.title==="Glim Sombrasselva"))failures.push("Glim ausente do atlas")
if(changed.length)failures.push("Notas originais alteradas")
if(broken.length)failures.push("Links locais sem destino")
const report={ok:!failures.length,notes:manifest.notes.length,searchEntries:noteCount,atlasNodes:atlas.nodes.length,htmlPages:htmlCount,localLinksChecked:localLinks,sourceChanges:changed,brokenLinks:broken,failures}
await fs.writeFile(path.join(root,"docs/site/verificacao.json"),JSON.stringify(report,null,2)+"\n")
console.log(JSON.stringify({...report,brokenLinks:broken.slice(0,12)}))
if(failures.length)process.exitCode=1
