import type { QuartzComponent } from "../quartz/components/types"
import script from "./atlas.inline"
import { pathToRoot } from "../quartz/util/path"

const links = [
  ["Personagens", "Personagens/Indice"], ["Lugares", "Lugares/Indice"],
  ["Facções", "Faccoes/Indice"], ["Acontecimentos", "Eventos/Indice"],
  ["Diários", "Sessoes/Indice"], ["Fontes", "Fontes/Indice"],
]
export const CampaignNav: QuartzComponent = ({ fileData }) => {
  const base = pathToRoot(fileData.slug!)
  return <nav class="campaign-nav" aria-label="Navegar pela campanha">
    <span class="nav-caption">ARQUIVO DE CAMPANHA</span>
    <a class="atlas-entry internal" href={`${base}/`}>◈ Explorar o atlas</a>
    <div class="campaign-eras"><a class="internal" href={`${base}/campanhas/glim`}>Glim <small>atual</small></a><a class="internal" href={`${base}/campanhas/fash`}>Fash <small>−70 anos</small></a></div>
    {links.map(([label, href]) => <a class="internal" href={`${base}/${href.toLowerCase()}`}>{label}<span aria-hidden="true">›</span></a>)}
  </nav>
}

export const Atlas: QuartzComponent = ({ fileData }) => {
  if (fileData.slug !== "index") return null
  return <section class="campaign-atlas" data-atlas-root aria-label="Grafo interativo da campanha">
    <div class="atlas-intro"><p class="atlas-eyebrow">PESSOAS, LUGARES E HISTÓRIAS CONECTADAS</p><p class="atlas-lead">Toda história deixa um fio.</p><p>Encontre um nome. Siga suas conexões. Explore as duas campanhas.</p></div>
    <div class="atlas-toolbar">
      <div class="atlas-epochs" role="group" aria-label="Filtrar por campanha"><button data-era="all" aria-pressed="true">As duas épocas</button><button data-era="glim" aria-pressed="false">Glim</button><button data-era="fash" aria-pressed="false">Fash</button></div>
      <button class="atlas-fit" type="button" title="Reenquadrar o grafo">Reenquadrar ↗</button>
    </div>
    <div class="atlas-surface">
      <svg class="atlas-svg" role="img" aria-label="Relações entre as notas; use a lista ao lado para navegar pelo teclado" viewBox="0 0 900 540"><g class="atlas-world" /></svg>
      <div class="atlas-count" aria-live="polite">Carregando conexões…</div>
      <div class="atlas-instructions">Arraste para mover · Role para ampliar · Clique para ler</div>
    </div>
    <div class="atlas-legend" role="group" aria-label="Filtrar por tipo de nota">
      {[['personagem','Personagens'],['lugar','Lugares'],['faccao','Facções'],['evento','Acontecimentos'],['item','Itens'],['criatura','Criaturas']].map(([kind,label]) => <button data-kind={kind} aria-pressed="true"><i data-color={kind} />{label}</button>)}
    </div>
    <details class="atlas-directory"><summary>Encontrar uma nota no grafo <span>Lista acessível e filtros</span></summary><label>Nome da nota<input type="search" class="atlas-find" placeholder="Glim, Ébano, Eral…" /></label><label class="atlas-archive"><input type="checkbox" /> Incluir fontes, sessões, índices e revisão no grafo</label><div class="atlas-results" /></details>
    <p class="atlas-error" hidden>Não foi possível carregar o grafo. Recarregue a página ou use a busca e os índices.</p>
  </section>
}
Atlas.afterDOMLoaded = script
