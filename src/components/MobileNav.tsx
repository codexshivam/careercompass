import type { Tab } from '../types'

interface MobileNavProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

export function MobileNav({ activeTab, onTabChange }: MobileNavProps) {
  return (
    <div className="mobile-module">
      <label htmlFor="module-select">Select Module</label>
      <select 
        id="module-select" 
        value={activeTab} 
        onChange={(event) => onTabChange(event.target.value as Tab)}
      >
        <option value="simulator">Promotion Simulator</option>
        <option value="salary">Salary Estimator</option>
        <option value="matrix">Skill Matrix</option>
        <option value="personas">Leadership Personas</option>
      </select>
    </div>
  )
}
