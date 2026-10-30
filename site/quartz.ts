import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import { PageTypeDispatcher } from "./quartz/plugins/pageTypes"
import { Atlas, CampaignNav } from "./campanha/Atlas"
import { AtlasData } from "./campanha/atlas-data"

const config = await loadQuartzConfig()
export const layout = await loadQuartzLayout()
for (const pageLayout of [layout.defaults, ...Object.values(layout.byPageType)]) {
  pageLayout.left = [...(pageLayout.left ?? []).slice(0, 2), CampaignNav, ...(pageLayout.left ?? []).slice(2)]
  pageLayout.beforeBody = [...(pageLayout.beforeBody ?? []), Atlas]
}
config.plugins.emitters = config.plugins.emitters.filter((p) => p.name !== "PageTypeDispatcher")
config.plugins.emitters.push(AtlasData(), PageTypeDispatcher(layout))
export default config
