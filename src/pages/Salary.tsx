import { useMemo, useState } from 'react'
import { roles } from '../data/constants'

export function Salary() {
  const [experience, setExperience] = useState(3)
  const [role, setRole] = useState('DS')
  const [senior, setSenior] = useState(false)
  const [location, setLocation] = useState('metro')

  const salary = useMemo(() => {
    const premiums: Record<string, number> = { DA: -3.21, BA: -1.3, DE: 1.85, DS: 3.53, MLE: 0, ARCH: 10.95 }
    const seniorBumps: Record<string, number> = { DA: 0.79, BA: 0.72, DE: 2.57, DS: 5.1, MLE: 2.5, ARCH: 0 }
    const expAdd = 1.5115 * experience
    const bump = senior ? seniorBumps[role] : 0
    let total = 11.2 + expAdd + premiums[role] + bump
    if (location === 'regional' && experience < 5) total *= 0.78
    return { total: Math.max(3.5, total), expAdd, premium: premiums[role], bump }
  }, [experience, location, role, senior])

  return (
    <section className="layout-grid salary-layout">
      <div className="card controls">
        <div className="section-heading">Parameters</div>
        <label className="field-label" htmlFor="role">Target Role</label>
        <select id="role" value={role} onChange={(event) => setRole(event.target.value)}>
          {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
        
        <div className="slider-block">
          <div className="slider-label"><span>Years of Experience</span><strong>{experience.toFixed(1)} yrs</strong></div>
          <input type="range" min="0" max="15" step="0.5" value={experience} onChange={(event) => setExperience(Number(event.target.value))} aria-label="Years of Experience" />
          <div className="scale"><span>0 (Entry)</span><span>5 (Mid)</span><span>15 (Executive)</span></div>
        </div>
        
        <span className="field-label">Seniority</span>
        <div className="segmented">
          <button type="button" className={!senior ? 'selected' : ''} onClick={() => setSenior(false)}>Associate / Jr</button>
          <button type="button" className={senior ? 'selected' : ''} onClick={() => setSenior(true)}>Senior / Lead</button>
        </div>
        
        <label className="field-label" htmlFor="location">Location</label>
        <select id="location" value={location} onChange={(event) => setLocation(event.target.value)}>
          <option value="metro">Top 7 Metro Hubs (Bengaluru, NCR, Mumbai, Hyderabad)</option>
          <option value="regional">Tier-2 / Regional Tech Hubs</option>
        </select>
      </div>
      
      <div className="stack">
        <div className="card salary-card">
          <div>
            <div className="eyebrow">Estimated Annual Compensation</div>
            <div className="salary-value">₹{salary.total.toFixed(1)}L <small>/ annum</small></div>
            <div className="breakdown">Base: ₹11.2L + Exp: ₹{salary.expAdd.toFixed(1)}L + Track: ₹{salary.premium.toFixed(1)}L + Seniority: ₹{salary.bump.toFixed(1)}L</div>
          </div>
        </div>
        <div className="card chart-card">
          <div className="section-heading">Seniority Premium by Role<span>Title increment over junior baseline (₹ Lakhs)</span></div>
          <div className="chart">
            {[
              ['Data Science', 5.1], 
              ['Data Engineering', 2.57], 
              ['Data Analyst', .79], 
              ['Business Analyst', .72]
            ].map(([label, value]) => (
              <div className="bar-wrap" key={label as string}>
                <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', width: '100%' }}>
                  <div className="bar" style={{ height: `${Number(value) / 5.1 * 100}%` }}>
                    <span>+₹{Number(value).toFixed(2)}L</span>
                  </div>
                </div>
                <label>{label as string}</label>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
