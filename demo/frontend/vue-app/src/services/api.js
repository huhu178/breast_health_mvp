const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value);
    }
  });
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

async function request(path, { method = 'GET', params, body, withCredentials = false } = {}) {
  const url = `${API_BASE_URL}${path}${buildQuery(params)}`;

  const response = await fetch(url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    credentials: withCredentials ? 'include' : 'same-origin'
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

export async function getPatients(params) {
  return request('/api/b/patients', { params, withCredentials: true });
}

export default {
  getPatients
};


