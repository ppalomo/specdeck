import { Link, Outlet } from '@tanstack/react-router'
import { Moon, Sun } from 'lucide-react'

import { Button } from '../ui/Button'
import { useTheme } from '../theme/useTheme'

/** The frame every screen sits in: where you are, and how to get back. */
export function Shell() {
  const { theme, toggle } = useTheme()

  return (
    <div className="min-h-screen bg-base">
      <header className="flex items-center justify-between gap-16 px-32 py-16">
        <nav className="flex items-center gap-16">
          <Link to="/" className="text-base font-semibold text-text">
            Specdeck
          </Link>
          <Link
            to="/system"
            className="text-sm text-muted transition-colors duration-150 hover:text-text"
          >
            Design system
          </Link>
        </nav>
        <Button tone="plain" size="small" onClick={toggle} aria-label="Switch theme">
          {theme === 'dark' ? (
            <Moon size={16} strokeWidth={1.75} />
          ) : (
            <Sun size={16} strokeWidth={1.75} />
          )}
        </Button>
      </header>
      <main className="px-32 pb-64">
        <Outlet />
      </main>
    </div>
  )
}
