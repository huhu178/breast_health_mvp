import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const root = new URL('..', import.meta.url).pathname

function read(relativePath) {
  return readFileSync(join(root, relativePath), 'utf8')
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

function assertIncludes(file, fragments) {
  const content = read(file)
  for (const fragment of fragments) {
    assert(content.includes(fragment), `${file} missing "${fragment}"`)
  }
}

assertIncludes('src/router/index.js', [
  "path: '/login'",
  "path: '/workbench'",
  "path: '/analytics'",
  "path: '/patient'"
])

assertIncludes('src/views/LoginView.vue', [
  '机构工作台登录',
  '填入演示账号',
  "fetch('/api/auth/login'"
])

assertIncludes('src/views/WorkbenchView.vue', [
  '医生工作台',
  'loadWorkbenchData',
  '/api/b/reports?page=1&per_page=50&include_unreported=1'
])

const distDir = join(root, 'dist')
const distHtml = join(distDir, 'index.html')
assert(existsSync(distHtml), 'dist/index.html does not exist; run npm run build first')

const html = readFileSync(distHtml, 'utf8')
const assetRefs = Array.from(html.matchAll(/(?:src|href)="([^"]+)"/g)).map((match) => match[1])
assert(assetRefs.length > 0, 'dist/index.html has no asset references')

for (const ref of assetRefs) {
  if (!ref.startsWith('/')) continue
  const assetPath = join(distDir, ref.replace(/^\//, ''))
  assert(existsSync(assetPath), `dist asset missing: ${ref}`)
}

const jsAssets = readdirSync(join(distDir, 'assets')).filter((name) => name.endsWith('.js'))
const cssAssets = readdirSync(join(distDir, 'assets')).filter((name) => name.endsWith('.css'))
assert(jsAssets.length > 0, 'dist/assets has no JavaScript bundle')
assert(cssAssets.length > 0, 'dist/assets has no CSS bundle')

console.log('[OK] prototype smoke checks passed')
