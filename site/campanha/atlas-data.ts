import fs from "node:fs/promises"
import path from "node:path"
import type { QuartzEmitterPlugin } from "../quartz/plugins/types"
import type { FilePath } from "../quartz/util/path"

export const AtlasData: QuartzEmitterPlugin = () => ({
  name: "CampaignAtlasData",
  async *emit({ argv }, content) {
    const nodes = content.map(([, file]) => {
      const m = (file.data.frontmatter ?? {}) as Record<string, unknown>
      const kinds: Record<string, string> = { grupo: "faccao", dossie_de_itens: "item", poder: "item", conjunto_de_documentos: "item", conjunto_de_itens: "item", mecanismo: "item" }
      const kind = String(m.tipo ?? "indice")
      return { id: file.data.slug, title: m.title, kind: kinds[kind] ?? kind, eras: m.campanhas ?? [], links: file.data.links ?? [] }
    })
    const dest = path.join(argv.output, "static", "atlas.json") as FilePath
    await fs.mkdir(path.dirname(dest), { recursive: true })
    await fs.writeFile(dest, JSON.stringify({ nodes }))
    yield dest
  },
})
