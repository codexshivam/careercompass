import { useMemo, useState } from 'react'
import { competencyFields } from '../data/constants'

const calculateProbability = (s: number[]) => {
  const [dash, math, aiml, big, code] = s
  const z = -26.2236 + 1.821 * math + 1.3547 * dash + 1.2639 * aiml + 0.9961 * big + 0.609 * code
  return Math.round((1 / (1 + Math.exp(-z))) * 100)
}

export function Simulator() {
  const [scores, setScores] = useState<number[]>(competencyFields.map((field) => field[4] as number))

  const probability = useMemo(() => calculateProbability(scores), [scores])

  const bestROI = useMemo(() => {
    const baseProb = calculateProbability(scores)
    let bestDelta = 0
    let bestSkill = -1

    scores.forEach((score, index) => {
      if (score < 5) {
        const newScores = [...scores]
        newScores[index] = Math.min(5, score + 0.5)
        const newProb = calculateProbability(newScores)
        const delta = newProb - baseProb
        if (delta > bestDelta) {
          bestDelta = delta
          bestSkill = index
        }
      }
    })

    if (bestSkill !== -1 && bestDelta > 0) {
      return {
        skillName: competencyFields[bestSkill][0],
        delta: bestDelta
      }
    }
    return null
  }, [scores])

  return (
    <section className="layout-grid simulator-layout">
      <div className="card competency-card">
        <div className="section-heading">Competency Ratings</div>
        {competencyFields.map((field, index) => (
          <div className="slider-block" key={field[0] as string}>
            <div className="slider-label"><span>{field[0] as string}</span><strong>{scores[index].toFixed(1)}</strong></div>
            <input 
              type="range" 
              min="1" 
              max="5" 
              step="0.1" 
              value={scores[index]} 
              onChange={(event) => setScores(scores.map((score, i) => i === index ? Number(event.target.value) : score))} 
              aria-label={field[0] as string} 
            />
            <div className="scale"><span>1.0 {field[1] as string}</span><span>3.0 {field[2] as string}</span><span>5.0 {field[3] as string}</span></div>
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
        {bestROI && (
          <div className="card insight-card">
            <div className="eyebrow">Skill ROI Recommendation</div>
            <p>
              Improving your <strong>{bestROI.skillName}</strong> by 0.5 points could increase your high-hike probability by <strong>+{bestROI.delta}%</strong>.
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
