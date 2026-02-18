import { useEffect, useMemo, useState } from 'react';
import Swal from 'sweetalert2';

import AuthFormCard from '../components/AuthFormCard';

const modeConfig = {
  login: {
    title: 'Sign In',
    submitLabel: 'Login',
    headline: 'Welcome Back',
    copy: 'Secure login for admin and recruiters. Built for company-only access with role-based controls.',
    fields: [
      { name: 'username', label: 'Username', type: 'text', placeholder: 'Enter username' },
      { name: 'password', label: 'Password', type: 'password', placeholder: 'Enter password' },
    ],
  },
  register: {
    title: 'Register',
    submitLabel: 'Register',
    headline: 'Create Admin Account',
    copy: 'Register the first admin account. After this setup, use Login for daily authentication.',
    fields: [
      { name: 'username', label: 'Admin Username', type: 'text', placeholder: 'first admin user' },
      { name: 'password', label: 'Admin Password', type: 'password', placeholder: 'strong password' },
    ],
  },
};

export default function AuthPage({ onLogin, onBootstrap, loading }) {
  const [mode, setMode] = useState('login');
  const [values, setValues] = useState({ username: '', password: '' });
  const [isMobile, setIsMobile] = useState(
    typeof window !== 'undefined' ? window.innerWidth < 768 : false
  );
  const [mobileView, setMobileView] = useState('form');

  const activeConfig = useMemo(() => modeConfig[mode], [mode]);

  useEffect(() => {
    function handleResize() {
      setIsMobile(window.innerWidth < 768);
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    setMobileView('form');
  }, [mode]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!values.username.trim() || !values.password.trim()) {
      await Swal.fire({
        icon: 'warning',
        title: 'Missing fields',
        text: 'Please fill username and password.',
        confirmButtonColor: '#a855f7',
      });
      return;
    }

    if (mode === 'login') {
      await onLogin(values);
      return;
    }

    await onBootstrap(values);
    setMode('login');
  }

  const isLogin = mode === 'login';
  const infoPanel = (
    <section
      className={`relative overflow-hidden p-6 md:p-10 lg:p-12 ${
        isLogin ? 'md:order-2 animate-slide-in-right' : 'md:order-1 animate-slide-in-left'
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-violet-800/70 via-fuchsia-700/30 to-transparent" />
      <div className="absolute -right-32 top-0 h-full w-64 rotate-12 bg-gradient-to-r from-transparent to-fuchsia-400/20" />
      <div className="relative z-10">
        <p className="mb-3 inline-block rounded-full border border-fuchsia-300/40 bg-fuchsia-500/20 px-3 py-1 text-xs tracking-[0.2em] text-fuchsia-100">
          ATS AUTH MODULE
        </p>
        <h1 className="text-3xl font-bold leading-tight text-white md:text-4xl">
          {activeConfig.headline}
        </h1>
        <p className="mt-3 max-w-sm text-sm text-slate-200 md:text-base">{activeConfig.copy}</p>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={() => setMode('login')}
            className={`rounded-full px-4 py-2 text-sm transition ${
              isLogin
                ? 'bg-fuchsia-500 text-white'
                : 'border border-fuchsia-300/30 text-fuchsia-100'
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => setMode('register')}
            className={`rounded-full px-4 py-2 text-sm transition ${
              !isLogin
                ? 'bg-fuchsia-500 text-white'
                : 'border border-fuchsia-300/30 text-fuchsia-100'
            }`}
          >
            Register
          </button>
        </div>

        {isMobile ? (
          <button
            type="button"
            onClick={() => setMobileView('form')}
            className="mt-5 w-full rounded-full border border-fuchsia-300/40 px-4 py-2 text-sm text-fuchsia-100 transition hover:bg-fuchsia-600/20"
          >
            Open {activeConfig.title} Form
          </button>
        ) : null}
      </div>
    </section>
  );

  const formPanel = (
    <section
      className={`flex items-center p-6 md:p-10 lg:p-12 ${
        isLogin ? 'md:order-1 animate-slide-in-left' : 'md:order-2 animate-slide-in-right'
      }`}
    >
      <div className="w-full animate-fade-in-up">
        <AuthFormCard
          mode={mode}
          title={activeConfig.title}
          submitLabel={activeConfig.submitLabel}
          fields={activeConfig.fields}
          values={values}
          onChange={handleChange}
          onSubmit={handleSubmit}
          loading={loading}
          footer={
            isLogin
              ? 'Use your assigned company username and password.'
              : 'Register once, then return to Login.'
          }
        />
        {isMobile ? (
          <button
            type="button"
            onClick={() => setMobileView('info')}
            className="mt-4 w-full rounded-full border border-fuchsia-300/40 px-4 py-2 text-sm text-fuchsia-100 transition hover:bg-fuchsia-600/20"
          >
            Show Overview
          </button>
        ) : null}
      </div>
    </section>
  );

  if (isMobile) {
    return (
      <div className="relative mx-auto h-full w-full max-w-6xl overflow-hidden rounded-3xl border border-fuchsia-500/60 bg-slate-950/70 shadow-[0_0_35px_rgba(168,85,247,0.4)] backdrop-blur-md">
        <div className="absolute -left-12 top-8 h-32 w-32 animate-float rounded-full bg-fuchsia-500/20 blur-3xl" />
        <div className="h-full">
          {mobileView === 'info' ? (
            <div className="h-full overflow-y-auto">{infoPanel}</div>
          ) : (
            <div className="h-full overflow-y-auto">{formPanel}</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="relative mx-auto h-full w-full max-w-6xl overflow-hidden rounded-3xl border border-fuchsia-500/60 bg-slate-950/70 shadow-[0_0_35px_rgba(168,85,247,0.4)] backdrop-blur-md">
      <div className="absolute -left-12 top-8 h-32 w-32 animate-float rounded-full bg-fuchsia-500/20 blur-3xl" />
      <div className="absolute right-0 top-0 h-full w-[1px] bg-gradient-to-b from-transparent via-fuchsia-500/60 to-transparent md:right-[56%]" />

      <div className="grid h-full min-h-[520px] grid-cols-1 md:grid-cols-2">
        {infoPanel}
        {formPanel}
      </div>
    </div>
  );
}
