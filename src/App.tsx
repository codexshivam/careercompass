import { useState } from 'react'
import './App.css'
import type { Tab } from './types'
import { Topbar } from './components/Topbar'
import { MobileNav } from './components/MobileNav'
import { Simulator } from './pages/Simulator'
import { Salary } from './pages/Salary'
import { Matrix } from './pages/Matrix'
import { Personas } from './pages/Personas'

function App() {
  const [tab, setTab] = useState<Tab>('simulator')

  return (
    <div className="app-shell">
      <Topbar activeTab={tab} onTabChange={setTab} />

      <main className="main">
        <MobileNav activeTab={tab} onTabChange={setTab} />

        {tab === 'simulator' && <Simulator />}
        {tab === 'salary' && <Salary />}
        {tab === 'matrix' && <Matrix />}
        {tab === 'personas' && <Personas />}
      </main>
    </div>
  )
}

export default App
