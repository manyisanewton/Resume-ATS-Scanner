import { useEffect, useState } from 'react';
import Swal from 'sweetalert2';

import { bootstrapAdmin, createRecruiter, getCurrentUser, login } from './api/authApi';
import AuthSkeleton from './components/AuthSkeleton';
import { useAuth } from './context/AuthContext';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import { clearSession, loadSession, saveSession } from './utils/storage';

function App() {
  const { token, user, setSession, clearAuth } = useAuth();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function hydrateSession() {
      const existing = loadSession();
      if (!existing.token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser(existing.token);
        setSession(existing.token, currentUser);
      } catch {
        clearSession();
      } finally {
        setLoading(false);
      }
    }

    hydrateSession();
  }, [setSession]);

  async function handleLogin(payload) {
    setSubmitting(true);
    try {
      const data = await login(payload);
      saveSession(data.access_token, data.user);
      setSession(data.access_token, data.user);
      await Swal.fire({
        icon: 'success',
        title: 'Welcome',
        text: `Logged in as ${data.user.username}`,
        confirmButtonColor: '#a855f7',
      });
    } catch (error) {
      await Swal.fire({
        icon: 'error',
        title: 'Login failed',
        text: error.message,
        confirmButtonColor: '#a855f7',
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleBootstrap(payload) {
    setSubmitting(true);
    try {
      await bootstrapAdmin(payload);
      await Swal.fire({
        icon: 'success',
        title: 'Admin created',
        text: 'You can now login with the admin credentials.',
        confirmButtonColor: '#a855f7',
      });
    } catch (error) {
      await Swal.fire({
        icon: 'error',
        title: 'Setup failed',
        text: error.message,
        confirmButtonColor: '#a855f7',
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateRecruiter(payload) {
    if (!token) {
      throw new Error('Session expired. Please login again.');
    }

    return createRecruiter(payload, token);
  }

  function handleLogout() {
    clearSession();
    clearAuth();
    Swal.fire({
      icon: 'info',
      title: 'Logged out',
      text: 'Session ended successfully.',
      confirmButtonColor: '#a855f7',
    });
  }

  const mainClassName = user
    ? 'auth-app-shell h-screen w-full overflow-y-auto px-4 py-6 md:px-8 md:py-10'
    : 'auth-app-shell h-screen w-full overflow-hidden p-3 md:p-6';

  return (
    <main className={mainClassName}>
      {loading ? (
        <AuthSkeleton />
      ) : user ? (
        <DashboardPage user={user} onLogout={handleLogout} onCreateRecruiter={handleCreateRecruiter} />
      ) : (
        <AuthPage onLogin={handleLogin} onBootstrap={handleBootstrap} loading={submitting} />
      )}
    </main>
  );
}

export default App;
