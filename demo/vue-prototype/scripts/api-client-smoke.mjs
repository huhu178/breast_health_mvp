import assert from 'node:assert/strict'
import { apiJson, apiPostJson } from '../src/utils/apiClient.js'

function jsonResponse(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: { 'Content-Type': 'application/json' },
  })
}

const calls = []
globalThis.fetch = async (url, options = {}) => {
  calls.push({ url, options })
  if (url === '/ok') return jsonResponse({ success: true, data: { id: 1 } })
  if (url === '/plain') return jsonResponse({ name: 'plain' })
  if (url === '/business-error') return jsonResponse({ success: false, message: '业务失败', data: { code: 'E_BIZ' } })
  if (url === '/http-error') return jsonResponse({ message: '服务失败' }, { status: 500 })
  if (url === '/post') return jsonResponse({ success: true, data: { saved: true } })
  if (url === '/form') return jsonResponse({ success: true, data: { uploaded: true } })
  throw new Error(`unexpected fetch: ${url}`)
}

assert.deepEqual(await apiJson('/ok'), { id: 1 })
assert.deepEqual(await apiJson('/plain'), { name: 'plain' })

await assert.rejects(
  () => apiJson('/business-error'),
  (err) => err.message === '业务失败' && err.payload?.data?.code === 'E_BIZ'
)

await assert.rejects(
  () => apiJson('/http-error'),
  (err) => err.message === '服务失败' && err.status === 500
)

assert.deepEqual(await apiPostJson('/post', { name: '张三' }), { saved: true })
const postCall = calls.find((call) => call.url === '/post')
assert.equal(postCall.options.method, 'POST')
assert.equal(postCall.options.headers['Content-Type'], 'application/json')
assert.equal(postCall.options.body, JSON.stringify({ name: '张三' }))

const form = new FormData()
form.append('file', new Blob(['x']), 'x.txt')
assert.deepEqual(await apiJson('/form', { method: 'POST', body: form }), { uploaded: true })
const formCall = calls.find((call) => call.url === '/form')
assert.equal(formCall.options.headers['Content-Type'], undefined)
assert.equal(formCall.options.credentials, 'include')

console.log('[OK] API client smoke checks passed')
