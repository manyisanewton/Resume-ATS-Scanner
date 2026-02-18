import { useState } from 'react';
import Swal from 'sweetalert2';
import { FaSignOutAlt, FaUserPlus } from 'react-icons/fa';

import LoadingSpinner from '../components/LoadingSpinner';

export default function DashboardPage({ user, onLogout, onCreateRecruiter }) {
  const [formValues, setFormValues] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  }

  async function handleRecruiterSubmit(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await onCreateRecruiter(formValues);
      await Swal.fire({
        icon: 'success',
        title: 'Recruiter Created',
        text: `${formValues.username} is ready to login.`,
        confirmButtonColor: '#a855f7',
      });
      setFormValues({ username: '', password: '' });
    } catch (error) {
      await Swal.fire({
        icon: 'error',
        title: 'Failed',
        text: error.message,
        confirmButtonColor: '#a855f7',
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-5xl space-y-8">
      <header className="flex flex-col gap-4 rounded-2xl border border-fuchsia-500/40 bg-slate-950/70 p-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Authentication Control Panel</h1>
          <p className="text-sm text-slate-300">
            Logged in as <span className="font-semibold text-fuchsia-300">{user.username}</span> ({user.role})
          </p>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-fuchsia-500/40 bg-slate-900 px-4 py-2 text-sm text-white transition hover:bg-fuchsia-600/20"
        >
          <FaSignOutAlt />
          Logout
        </button>
      </header>

      {user.role === 'admin' ? (
        <section className="rounded-2xl border border-fuchsia-500/40 bg-slate-950/70 p-6">
          <div className="mb-4 flex items-center gap-2 text-white">
            <FaUserPlus className="text-fuchsia-300" />
            <h2 className="text-xl font-semibold">Create Recruiter Account</h2>
          </div>
          <form className="grid gap-4 md:grid-cols-2" onSubmit={handleRecruiterSubmit}>
            <input
              required
              name="username"
              value={formValues.username}
              onChange={handleChange}
              placeholder="recruiter username"
              className="rounded-xl border border-fuchsia-500/30 bg-slate-900/80 px-4 py-3 text-white outline-none focus:border-fuchsia-300"
            />
            <input
              required
              name="password"
              type="password"
              value={formValues.password}
              onChange={handleChange}
              placeholder="temporary password"
              className="rounded-xl border border-fuchsia-500/30 bg-slate-900/80 px-4 py-3 text-white outline-none focus:border-fuchsia-300"
            />
            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="flex h-11 w-full items-center justify-center rounded-full bg-gradient-to-r from-fuchsia-600 to-violet-500 font-semibold text-white transition-all hover:brightness-110 disabled:opacity-70"
              >
                {loading ? <LoadingSpinner label="Creating recruiter" /> : 'Create Recruiter'}
              </button>
            </div>
          </form>
        </section>
      ) : (
        <section className="rounded-2xl border border-fuchsia-500/40 bg-slate-950/70 p-6 text-slate-300">
          Recruiter access is active. Admin-only user creation is disabled for your role.
        </section>
      )}
    </div>
  );
}
