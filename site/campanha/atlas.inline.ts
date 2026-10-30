type AtlasNode = { id: string; title: string; kind: string; eras: string[]; links: string[] }
type Point = AtlasNode & { x: number; y: number; vx: number; vy: number; degree: number }

async function startCampaignAtlas() {
  const root = document.querySelector<HTMLElement>("[data-atlas-root]")
  if (!root || root.dataset.ready) return
  root.dataset.ready = "true"
  const controller = new AbortController()
  const { signal } = controller
  window.addCleanup(() => controller.abort())
  const svg = root.querySelector<SVGSVGElement>(".atlas-svg")!
  const world = root.querySelector<SVGGElement>(".atlas-world")!
  const results = root.querySelector<HTMLElement>(".atlas-results")!
  const count = root.querySelector<HTMLElement>(".atlas-count")!
  const search = root.querySelector<HTMLInputElement>(".atlas-find")!
  const archive = root.querySelector<HTMLInputElement>(".atlas-archive input")!
  const base = new URL(document.body.dataset.slug === "index" ? "./" : "../", location.href)
  const ns = "http://www.w3.org/2000/svg"
  const defaults = ["personagem", "lugar", "faccao", "evento", "item", "criatura"]
  const kinds = new Set(defaults)
  let era = "all", points: Point[] = [], pan = { x: 0, y: 0 }, zoom = 1
  let edges: [Point, Point][] = []
  let frame = 0, hovered = "", selected: Point | null = null
  let width = 900, height = 520
  const fold = (s: string) => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase()
  const route = (id: string) => new URL(id.split("/").map(encodeURIComponent).join("/"), base).href
  function element(name: string, attrs: Record<string, string> = {}) {
    const el = document.createElementNS(ns, name)
    for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value)
    return el
  }
  function transform() { world.setAttribute("transform", `translate(${pan.x},${pan.y}) scale(${zoom})`) }
  function local(event: PointerEvent | WheelEvent) {
    const p = new DOMPoint(event.clientX, event.clientY)
    return p.matrixTransform(svg.getScreenCTM()!.inverse())
  }
  try {
    const response = await fetch(new URL("static/atlas.json", base), { signal })
    if (!response.ok) throw new Error("Atlas indisponível")
    const { nodes }: { nodes: AtlasNode[] } = await response.json()
    if (!root.isConnected) return
    const all = nodes.filter(n => n.id && n.title)
    function draw() {
      world.replaceChildren()
      const lines = element("g", { class: "atlas-edges" })
      const nodeLayer = element("g", { class: "atlas-nodes" })
      const adjacent = new Set<string>()
      if (hovered) for (const [a, b] of edges) {
        if (a.id === hovered) adjacent.add(b.id)
        if (b.id === hovered) adjacent.add(a.id)
      }
      for (const [a, b] of edges) {
        const active = a.id === hovered || b.id === hovered
        lines.append(element("line", { x1: String(a.x), y1: String(a.y), x2: String(b.x), y2: String(b.y), class: active ? "active" : hovered ? "muted" : "" }))
      }
      const leaders = new Set([...points].sort((a,b) => b.degree - a.degree).slice(0, 13).map(n => n.id))
      for (const n of points) {
        const active = hovered === n.id, related = active || adjacent.has(n.id)
        const link = element("a", { href: route(n.id), class: `atlas-node internal${active ? " active" : ""}${hovered && !related ? " muted" : ""}`, "aria-label": `${n.title} — abrir nota`, "data-id": n.id, "data-kind": n.kind })
        const title = element("title"); title.textContent = `${n.title} · ${n.degree} conexões`
        const circle = element("circle", { cx: String(n.x), cy: String(n.y), r: String(3.5 + Math.min(8, Math.sqrt(n.degree) * 1.25)) })
        link.append(title, circle)
        if (active || leaders.has(n.id) || points.length < 35) {
          const label = element("text", { x: String(n.x + 12), y: String(n.y + 4), class: active ? "active" : "" })
          label.textContent = n.title.length > 30 && !active ? n.title.slice(0, 28) + "…" : n.title
          link.append(label)
        }
        nodeLayer.append(link)
      }
      world.append(lines, nodeLayer)
      transform()
    }
    function settle() {
      // Deterministic, bounded layout; respects reduced motion and stops after settling.
      forceSimulation(points)
        .force("link", forceLink<Point, {source:Point;target:Point}>(edges.map(([source,target])=>({source,target}))).id(n=>n.id).distance(70).strength(.12))
        .force("charge", forceManyBody().strength(-65))
        .force("center", forceCenter(width/2,height/2))
        .force("collision", forceCollide<Point>().radius(n=>9+Math.min(7,Math.sqrt(n.degree))))
        .stop().tick(180)
      // Fit the geometry itself so labels and hit areas stay readable at the initial zoom.
      if (points.length) {
        const minX=Math.min(...points.map(n=>n.x)),maxX=Math.max(...points.map(n=>n.x))
        const minY=Math.min(...points.map(n=>n.y)),maxY=Math.max(...points.map(n=>n.y))
        const scale=Math.min((width-150)/Math.max(1,maxX-minX),(height-140)/Math.max(1,maxY-minY))
        for(const n of points) { n.x=(n.x-(minX+maxX)/2)*scale+width/2; n.y=(n.y-(minY+maxY)/2)*scale+height/2 }
      }
      fit()
    }
    function fit() {
      if (!points.length) return
      const minX=Math.min(...points.map(n=>n.x)), maxX=Math.max(...points.map(n=>n.x))
      const minY=Math.min(...points.map(n=>n.y)), maxY=Math.max(...points.map(n=>n.y))
      zoom=Math.min(1.8, (width-100)/Math.max(80,maxX-minX), (height-100)/Math.max(80,maxY-minY))
      pan={x:width/2-(minX+maxX)/2*zoom,y:height/2-(minY+maxY)/2*zoom}
      draw()
    }
    function update() {
      width=Math.max(340,svg.clientWidth); height=svg.clientHeight || 520
      svg.setAttribute("viewBox",`0 0 ${width} ${height}`)
      const term=fold(search.value)
      const filtered=all.filter(n => (archive.checked ? !defaults.includes(n.kind) || kinds.has(n.kind) : kinds.has(n.kind)) && (era==="all" || n.eras.includes(era)) && (!term || fold(n.title).includes(term)))
      points=filtered.map((n,i) => ({...n,x:width/2+Math.cos(i*2.399)*Math.sqrt(i+1)*12,y:height/2+Math.sin(i*2.399)*Math.sqrt(i+1)*12,vx:0,vy:0,degree:0}))
      const lookup=new Map(points.map(n=>[n.id,n])), seen=new Set<string>()
      edges=[]
      for (const n of points) for (const id of n.links) {
        const other=lookup.get(id.split("#")[0])
        if (!other || other===n) continue
        const key=[n.id,other.id].sort().join("\0")
        if (seen.has(key)) continue
        seen.add(key); edges.push([n,other]); n.degree++; other.degree++
      }
      count.textContent=points.length ? `${points.length} notas · ${edges.length} conexões` : "Nenhuma nota com estes filtros"
      results.replaceChildren()
      for (const n of [...points].sort((a,b)=>a.title.localeCompare(b.title,"pt-BR")).slice(0,80)) {
        const a=document.createElement("a"); a.href=route(n.id); a.className="internal"; a.textContent=n.title; results.append(a)
      }
      if (points.length>80) { const p=document.createElement("p");p.textContent="Mostrando 80 notas. Digite um nome para refinar a lista.";results.append(p) }
      hovered=""; settle(); if (!points.length) world.replaceChildren()
    }
    root.querySelectorAll<HTMLButtonElement>("[data-era]").forEach(button => button.addEventListener("click",()=>{
      era=button.dataset.era!
      root.querySelectorAll<HTMLButtonElement>("[data-era]").forEach(b=>b.setAttribute("aria-pressed",String(b===button)))
      update()
    },{signal}))
    root.querySelectorAll<HTMLButtonElement>("[data-kind]").forEach(button=>button.addEventListener("click",()=>{
      const kind=button.dataset.kind!
      if (kinds.has(kind)) kinds.delete(kind); else kinds.add(kind)
      button.setAttribute("aria-pressed",String(kinds.has(kind)));update()
    },{signal}))
    search.addEventListener("input",update,{signal}); archive.addEventListener("change",update,{signal})
    root.querySelector(".atlas-fit")!.addEventListener("click",fit,{signal})
    svg.addEventListener("wheel",event=>{
      event.preventDefault(); const p=local(event), next=Math.max(0.15,Math.min(5,zoom*Math.exp(-event.deltaY*0.001)))
      pan={x:p.x-(p.x-pan.x)*next/zoom,y:p.y-(p.y-pan.y)*next/zoom};zoom=next;transform()
    },{signal,passive:false})
    let dragging=false,moved=false,last={x:0,y:0}
    svg.addEventListener("pointerdown",event=>{
      if (event.button!==0) return
      last=local(event); dragging=true;moved=false
      const anchor=(event.target as Element).closest("[data-id]")
      selected=points.find(n=>n.id===anchor?.getAttribute("data-id")) || null
      svg.setPointerCapture(event.pointerId)
    },{signal})
    svg.addEventListener("pointermove",event=>{
      const p=local(event)
      if (dragging) {
        const dx=p.x-last.x,dy=p.y-last.y
        if (Math.abs(dx)+Math.abs(dy)>2) moved=true
        if (selected) {selected.x+=dx/zoom;selected.y+=dy/zoom;draw()}
        else {pan.x+=dx;pan.y+=dy;transform()}
        last=p
      } else {
        const id=(event.target as Element).closest("[data-id]")?.getAttribute("data-id") || ""
        if (id!==hovered) { hovered=id;cancelAnimationFrame(frame);frame=requestAnimationFrame(draw) }
      }
    },{signal})
    svg.addEventListener("pointerup",event=>{
      if (selected && !moved) location.href=route(selected.id)
      dragging=false;selected=null;svg.releasePointerCapture(event.pointerId)
    },{signal})
    svg.addEventListener("pointercancel",()=>{dragging=false;selected=null},{signal})
    svg.addEventListener("click",event=>{if(moved)event.preventDefault()},{signal})
    svg.addEventListener("pointerleave",()=>{if(!dragging){hovered="";draw()}},{signal})
    const observer=new ResizeObserver(()=>{if(Math.abs(svg.clientWidth-width)>10)update()})
    observer.observe(svg);window.addCleanup(()=>{observer.disconnect();cancelAnimationFrame(frame)})
    update()
  } catch (err) {
    if (signal.aborted) return
    count.textContent="Grafo indisponível"
    root.querySelector<HTMLElement>(".atlas-error")!.hidden=false
    console.error(err)
  }
}
document.addEventListener("nav",startCampaignAtlas)
export default ""
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from "d3-force"

