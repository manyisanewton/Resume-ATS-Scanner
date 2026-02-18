import { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState({
    token: null,
    user: null,
  });

  const value = useMemo(
    () => ({
      token: authState.token,
      user: authState.user,
      setSession: (token, user) => setAuthState({ token, user }),
      clearAuth: () => setAuthState({ token: null, user: null }),
    }),
    [authState.token, authState.user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
