export async function apiJson(url, options = {}) {
  const headers = {
    ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {})
  }
  const res = await fetch(url, {
    credentials: 'include',
    ...options,
    headers
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.success === false) {
    const err = new Error(data.message || `请求失败：${res.status}`)
    err.status = res.status
    err.payload = data
    throw err
  }
  return data.data ?? data
}

export async function apiPostJson(url, payload = {}) {
  return apiJson(url, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}
