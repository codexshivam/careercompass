import { useMemo, useState } from 'react'
import { competencyFields } from '../data/constants'

export function Simulator() {
  const [scores, setScores] = useState<number[]>(competencyFields.map((field) => field[4]))

  const probability = useMemo(() => {
    const [dash, math, aiml, big, code] = scores
    const z = -26.2236 + 1.821 * math + 1.3547 * dash + 1.2639 * aiml + 0.9961 * big + 0.609 * code
    return Math.round((1 / (1 + Math.exp(-z))) * 100)
  }, [scores])

  return (
    <section className="layout-grid simulator-layout">
      <div className="card competency-card">
        <div className="section-heading">Competency Ratings</div>
        {competencyFields.map((field, index) => (
          <div className="slider-block" key={field[0]}>
            <div className="slider-label"><span>{field[0]}</span><strong>{scores[index].toFixed(1)}</strong></div>
            <input 
              type="range" 
              min="1" 
              max="5" 
              step="0.1" 
              value={scores[index]} 
              onChange={(event) => setScores(scores.map((score, i) => i === index ? Number(event.target.value) : score))} 
              aria-label={field[0]} 
            />
            <div className="scale"><span>1.0 {field[1]}</span><span>3.0 {field[2]}</span><span>5.0 {field[3]}</span></div>
          </div>
        ))}
      </div>
      <div className="stack">
        <div className="card metric-card">
          <div className="eyebrow">Probability</div>
          <div className="metric-value">{probability}%</div>
          <div className="meter"><span style={{ width: `${probability}%` }} /></div>
          <span className="badge">✓ {probability >= 70 ? 'High Likelihood Zone' : probability >= 40 ? 'Moderate Competitive Zone' : 'Low Probability Zone'}</span>
        </div>
      </div>
    </section>
  )
}
