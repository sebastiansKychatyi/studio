// Quick input parser for the backend assistant: JSON {text, ctx} on stdin → QuickResult JSON on stdout.
// Run: node --experimental-strip-types --no-warnings scripts/quick-parse-cli.mjs  (Node 22+)
import { parseQuick } from '../app/utils/quickParse.ts'

let raw = ''
process.stdin.setEncoding('utf8')
process.stdin.on('data', (chunk) => (raw += chunk))
process.stdin.on('end', () => {
  const { text, ctx } = JSON.parse(raw)
  process.stdout.write(JSON.stringify(parseQuick(String(text ?? ''), ctx)))
})
