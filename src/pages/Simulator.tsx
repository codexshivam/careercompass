import { useEffect, useState } from 'react'
import { fetchCompetencies, predictPromotion } from '../api'
import type { CompetencyField } from '../types'

interface PredictionResult {
  percentage: number
  verdict: string
  roiSkill: string | null
  roiDelta: number
}

export function Simulator() {
  const [competencies, setCompetencies] = useState<CompetencyField[]>([])
  const [scores, setScores] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [fetchingMeta, setFetchingMeta] = useState(true)
  const [result, setResult] = useState<PredictionResult>({
    percentage: 0,
    verdict: 'Calculating...',
    roiSkill: null,
    roiDelta: 0,
  })

  // 1. Load competencies dynamically from Backend API
  useEffect(() => {
    let isMounted = true
    fetchCompetencies()
      .then((data) => {
        if (!isMounted) return
        setCompetencies(data)
        setScores(data.map((c) => c.default))
        setFetchingMeta(false)
      })
      .catch((err) => {
        console.error('Failed to load competencies from backend:', err)
        setFetchingMeta(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // 2. Debounced Prediction API call to Backend
  useEffect(() => {
    if (scores.length < 5) return

    const controller = new AbortController()
    const fetchPrediction = async () => {
      setLoading(true)
      try {
        const [dash, math, aiml, big, code] = scores
        const data = await predictPromotion(
          {
            dashboard: dash,
            maths: math,
            ai_ml: aiml,
            big_data: big,
            coding: code,
          },
          controller.signal
        )

        setResult({
          percentage: data.percentage,
          verdict: data.verdict,
          roiSkill: data.roi_skill,
          roiDelta: data.roi_delta,
        })
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('API Error:', error)
          setResult((prev) => ({
            ...prev,
            verdict: 'Server Offline - Start FastAPI Backend',
          }))
        }
      } finally {
        setLoading(false)
      }
    }

    const debounceTimer = setTimeout(() => {
      fetchPrediction()
    }, 200)

    return () => {
      clearTimeout(debounceTimer)
      controller.abort()
    }
  }, [scores])

  if (fetchingMeta) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
        Loading competencies from server...
      </div>
    )
  }

  return (
    <section className="layout-grid simulator-layout">
      <div className="card competency-card">
        <div className="section-heading">Competency Ratings</div>
        {competencies.map((field, index) => (
          <div className="slider-block" key={field.id}>
            <div className="slider-label">
              <span>{field.name}</span>
              <strong>{scores[index]?.toFixed(1) ?? '0.0'}</strong>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="0.1"
              value={scores[index] ?? field.default}
              onChange={(event) =>
                setScores(
                  scores.map((score, i) =>
                    i === index ? Number(event.target.value) : score
                  )
                )
              }
              aria-label={field.name}
            />
            <div className="scale">
              <span>1.0 {field.low}</span>
              <span>3.0 {field.mid}</span>
              <span>5.0 {field.high}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="stack">
        <div className="card metric-card">
          <div className="eyebrow">Probability</div>
          <div className="metric-value">{result.percentage}%</div>
          <div className="meter">
            <span
              style={{
                width: `${result.percentage}%`,
                opacity: loading ? 0.5 : 1,
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <span className="badge">
            {result.percentage >= 40 ? '✓ ' : '⚠ '}
            {result.verdict}
          </span>
        </div>
        {result.roiSkill && result.roiDelta > 0 && (
          <div
            className="card insight-card"
            style={{ opacity: loading ? 0.5 : 1, transition: 'opacity 0.3s ease' }}
          >
            <div className="eyebrow">Skill ROI Recommendation</div>
            <p>
              Improving your <strong>{result.roiSkill}</strong> by 0.5 points
              could increase your high-hike probability by{' '}
              <strong>+{result.roiDelta}%</strong>.
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
