import { NavLink, Link } from 'react-router-dom'
import { cn } from '../lib/utils'

const links = [
  { to: '/missions', label: 'Миссии' },
  { to: '/earth', label: 'Земля' },
  { to: '/cosmonauts', label: 'Космонавты' },
  { to: '/hangar', label: 'Ангар' },
]

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-void/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link to="/" className="group flex items-center gap-3">
          <span className="grid size-8 place-items-center rounded-full border border-amber/50 font-display text-sm font-extrabold text-amber shadow-[0_0_14px_#ffb54540] transition-shadow group-hover:shadow-[0_0_22px_#ffb54570]">
            С
          </span>
          <span className="hidden font-display text-[11px] font-semibold uppercase leading-tight tracking-[0.2em] text-ink sm:block">
            Бюро космонавтики
            <span className="block text-[9px] font-normal tracking-[0.3em] text-ink-dim">
              им. Героя России Синса
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  'rounded-md px-3 py-1.5 font-mono text-xs uppercase tracking-widest transition-colors',
                  isActive
                    ? 'bg-amber/10 text-amber shadow-[inset_0_-2px_0_#ffb545]'
                    : 'text-ink-dim hover:text-ink',
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
