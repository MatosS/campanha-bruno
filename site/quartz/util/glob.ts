import path from "path"
import { FilePath } from "./path"
import { globby } from "globby"

export function toPosixPath(fp: string): string {
  return fp.split(path.sep).join("/")
}

export async function glob(
  pattern: string,
  cwd: string,
  ignorePatterns: string[],
): Promise<FilePath[]> {
  const fps = (
    await globby(pattern, {
      cwd,
      ignore: ignorePatterns,
      // Campaign content is generated and deliberately excluded from version control.
      // Quartz's explicit ignorePatterns still apply to the staged public content.
      gitignore: false,
    })
  ).map(toPosixPath)
  return fps as FilePath[]
}
