import type { Tab } from '../types'

interface TopbarProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

export function Topbar({ activeTab, onTabChange }: TopbarProps) {
  const tabs: Tab[] = ['simulator', 'salary', 'matrix', 'personas']

  const getTabLabel = (item: Tab) => {
    switch (item) {
      case 'simulator': return 'Promotion Simulator'
      case 'salary': return 'Salary Estimator'
      case 'matrix': return 'Skill Matrix'
      case 'personas': return 'Leadership Personas'
    }
  }

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <svg className="brand-icon" viewBox="0 0 32 32" fill="none" width="20" height="20" aria-hidden="true">
            <circle cx="16" cy="16" r="13" stroke="currentColor" strokeWidth="2" />
            <circle cx="16" cy="16" r="2.2" fill="currentColor" />
            <polygon points="16,5 18.8,14 13.2,14" fill="currentColor" />
            <polygon points="16,27 18.8,18 13.2,18" fill="var(--muted)" />
          </svg>
          <span>Career Compass</span>
        </div>
        <nav className="desktop-tabs" aria-label="Career modules">
          {tabs.map((item) => (
            <button
              type="button"
              className={activeTab === item ? 'tab-btn active' : 'tab-btn'}
              key={item}
              onClick={() => onTabChange(item)}
              aria-selected={activeTab === item}
              role="tab"
            >
              {getTabLabel(item)}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}
