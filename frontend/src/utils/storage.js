const TOKEN_KEY = 'resume_ats_token';
const USER_KEY = 'resume_ats_user';

export function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function loadSession() {
  const token = localStorage.getItem(TOKEN_KEY);
  const rawUser = localStorage.getItem(USER_KEY);

  if (!token || !rawUser) {
    return { token: null, user: null };
  }

  try {
    const user = JSON.parse(rawUser);
    return { token, user };
  } catch {
    clearSession();
    return { token: null, user: null };
  }
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
