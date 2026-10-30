import { spawnSync } from "node:child_process"
import path from "node:path"
import { fileURLToPath } from "node:url"

export const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
export function build() {
  const prepare = spawnSync(process.execPath, [path.resolve(site, "../tools/preparar-site.mjs")], { cwd: path.dirname(site), stdio: "inherit", windowsHide: true })
  if (prepare.status !== 0) return false
  const quartz = spawnSync(process.execPath, ["quartz/bootstrap-cli.mjs", "build", "--directory", "content", "--concurrency", "2"], { cwd: site, stdio: "inherit", windowsHide: true })
  return quartz.status === 0
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) process.exitCode = build() ? 0 : 1
