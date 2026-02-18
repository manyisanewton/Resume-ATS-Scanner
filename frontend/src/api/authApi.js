const API_BASE_URL =
  (typeof window !== 'undefined' && window.__APP_API_BASE_URL__) || '';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const body = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = body?.error || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return body;
}

export function login(payload) {
  return request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function bootstrapAdmin(payload) {
  return request('/api/auth/bootstrap-admin', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser(token) {
  return request('/api/users/me', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function createRecruiter(payload, token) {
  return request('/api/users/recruiters', {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}
