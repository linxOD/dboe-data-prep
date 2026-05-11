import { encode } from "@toon-format/toon"
import { readdir, readFile, writeFile } from "node:fs/promises"
import { join } from "node:path"


const corpusDir = join("output", "llm_corpus")
const files = await readdir(corpusDir, { withFileTypes: true })

for (const file of files) {
  if (file.isFile() && file.name.endsWith(".json")) {
    const input = join(corpusDir, file.name)
    const output = join(corpusDir, file.name.replace(/\.json$/i, ".toon"))

    const data = JSON.parse(await readFile(input, "utf-8"))
    const encoded = encode(data).replace("null", "")
    await writeFile(output, encoded)
  }
}
