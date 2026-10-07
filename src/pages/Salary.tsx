import { useEffect, useState } from 'react'
import { fetchSalaryConfig, calculateSalary } from '../api'
import type { RoleConfig, PremiumChartItem, SalaryEstimate } from '../types'

export function Salary() {
  const [roles, setRoles] = useState<RoleConfig[]>([])
  const [premiumsChart, setPremiumsChart] = useState<PremiumChartItem[]>([])
  const [experience, setExperience] = useState(3)
  const [role, setRole] = useState('DS')
  const [senior, setSenior] = useState(false)
  const [location, setLocation] = useState('metro')
  const [salary, setSalary] = useState<SalaryEstimate>({
    total: 0,
    expAdd: 0,
    premium: 0,
    bump: 0,
  })
  const [loadingConfig, setLoadingConfig] = useState(true)

  // 1. Fetch roles & chart config from Backend
  useEffect(() => {
    let isMounted = true
    fetchSalaryConfig()
      .then((data) => {
        if (!isMounted) return
        setRoles(data.roles)
        setPremiumsChart(data.premiumsChart)
        if (data.roles.length > 0 && !data.roles.some((r) => r.code === role)) {
          setRole(data.roles[0].code)
        }
        setLoadingConfig(false)
      })
      .catch((err) => {
        console.error('Failed to load salary config from backend:', err)
        setLoadingConfig(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // 2. Fetch estimated salary calculation from Backend
  useEffect(() => {
    let isMounted = true
    calculateSalary({ role, experience, senior, location })
      .then((data) => {
        if (isMounted) setSalary(data)
      })
      .catch((err) => console.error('Error calculating salary on backend:', err))

    return () => {
      isMounted = false
    }
  }, [role, experience, senior, location])

  if (loadingConfig) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
        Loading salary parameters from server...
      </div>
    )
  }

  return (
    <section className="layout-grid salary-layout">
      <div className="card controls">
        <div className="section-heading">Parameters</div>
        <label className="field-label" htmlFor="role">Target Role</label>
        <select id="role" value={role} onChange={(event) => setRole(event.target.value)}>
          {roles.map((r) => (
            <option key={r.code} value={r.code}>
              {r.label}
            </option>
          ))}
        </select>

        <div className="slider-block">
          <div className="slider-label">
            <span>Years of Experience</span>
            <strong>{experience.toFixed(1)} yrs</strong>
          </div>
          <input
            type="range"
            min="0"
            max="15"
            step="0.5"
            value={experience}
            onChange={(event) => setExperience(Number(event.target.value))}
            aria-label="Years of Experience"
          />
          <div className="scale">
            <span>0 (Entry)</span>
            <span>5 (Mid)</span>
            <span>15 (Executive)</span>
          </div>
        </div>

        <span className="field-label">Seniority</span>
        <div className="segmented">
          <button
            type="button"
            className={!senior ? 'selected' : ''}
            onClick={() => setSenior(false)}
          >
            Associate / Jr
          </button>
          <button
            type="button"
            className={senior ? 'selected' : ''}
            onClick={() => setSenior(true)}
          >
            Senior / Lead
          </button>
        </div>

        <label className="field-label" htmlFor="location">Location</label>
        <select
          id="location"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
        >
          <option value="metro">Top 7 Metro Hubs (Bengaluru, NCR, Mumbai, Hyderabad)</option>
          <option value="regional">Tier-2 / Regional Tech Hubs</option>
        </select>
      </div>

      <div className="stack">
        <div className="card salary-card">
          <div>
            <div className="eyebrow">Estimated Annual Compensation</div>
            <div className="salary-value">
              ₹{salary.total.toFixed(1)}L <small>/ annum</small>
            </div>
            <div className="breakdown">
              Base: ₹11.2L + Exp: ₹{salary.expAdd.toFixed(1)}L + Track: ₹{salary.premium.toFixed(1)}L + Seniority: ₹{salary.bump.toFixed(1)}L
            </div>
          </div>
        </div>
        <div className="card chart-card">
          <div className="section-heading">
            Seniority Premium by Role
            <span>Title increment over junior baseline (₹ Lakhs)</span>
          </div>
          <div className="chart">
            {premiumsChart.map((item) => (
              <div className="bar-wrap" key={item.role}>
                <div
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'flex-end',
                    justifyContent: 'center',
                    width: '100%',
                  }}
                >
                  <div
                    className="bar"
                    style={{
                      height: `${(Number(item.premium) / 5.1) * 100}%`,
                    }}
                  >
                    <span>+₹{Number(item.premium).toFixed(2)}L</span>
                  </div>
                </div>
                <label>{item.role}</label>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
