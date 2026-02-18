import { FaLock, FaUser, FaUserShield } from 'react-icons/fa';

import LoadingSpinner from './LoadingSpinner';

const iconMap = {
  login: <FaUser className="text-fuchsia-300" />,
  register: <FaUserShield className="text-fuchsia-300" />,
  recruiter: <FaLock className="text-fuchsia-300" />,
};

export default function AuthFormCard({
  mode,
  title,
  submitLabel,
  fields,
  values,
  onChange,
  onSubmit,
  loading,
  footer,
}) {
  return (
    <form className="relative space-y-4" onSubmit={onSubmit}>
      <div className="mb-6 flex items-center gap-3">
        <span className="rounded-full border border-fuchsia-400/60 bg-fuchsia-500/20 p-2">
          {iconMap[mode]}
        </span>
        <h2 className="text-2xl font-bold text-white">{title}</h2>
      </div>

      {fields.map((field) => (
        <label key={field.name} className="block">
          <span className="mb-1 block text-sm text-slate-300">{field.label}</span>
          <input
            required
            name={field.name}
            type={field.type}
            value={values[field.name] || ''}
            onChange={onChange}
            className="w-full rounded-xl border border-fuchsia-500/30 bg-slate-900/80 px-4 py-3 text-white outline-none transition-all focus:border-fuchsia-300 focus:ring-2 focus:ring-fuchsia-500/30"
            placeholder={field.placeholder}
          />
        </label>
      ))}

      <button
        type="submit"
        disabled={loading}
        className="flex h-11 w-full items-center justify-center rounded-full bg-gradient-to-r from-fuchsia-600 to-violet-500 font-semibold text-white transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? <LoadingSpinner label="Please wait" /> : submitLabel}
      </button>

      {footer ? <p className="text-center text-sm text-slate-300">{footer}</p> : null}
    </form>
  );
}
