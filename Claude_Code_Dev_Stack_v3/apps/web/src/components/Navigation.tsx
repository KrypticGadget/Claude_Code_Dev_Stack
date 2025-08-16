import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, CheckSquare, Volume2, Server, Monitor, Code } from 'lucide-react'

export const Navigation: React.FC = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/tasks', label: 'Tasks', icon: CheckSquare },
    { path: '/audio', label: 'Audio', icon: Volume2 },
    { path: '/mcp', label: 'MCP', icon: Server },
    { path: '/browser', label: 'Browser', icon: Monitor },
    { path: '/api-generator', label: 'API Gen', icon: Code }
  ]

  return (
    <nav className="navigation">
      <div className="nav-container">
        {navItems.map(({ path, label, icon: Icon }) => (
          <Link
            key={path}
            to={path}
            className={`nav-item ${location.pathname === path ? 'active' : ''}`}
          >
            <Icon size={16} />
            <span>{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}