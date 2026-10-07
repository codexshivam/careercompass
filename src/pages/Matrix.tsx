import { useEffect, useState } from 'react'
import { fetchMatrix } from '../api'
import type { MatrixItem } from '../types'

export function Matrix() {
  const [items, setItems] = useState<MatrixItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    fetchMatrix()
      .then((data) => {
        if (!isMounted) return
        setItems(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load matrix items from backend:', err)
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
        Loading skill matrix from server...
      </div>
    )
  }

  return (
    <section className="matrix-grid">
      {items.map((item) => (
        <article className="card matrix-card" key={item.title}>
          <div className="card-meta">
            <span className="badge">{item.tag}</span>
            <strong>{item.impact}</strong>
          </div>
          <h2>{item.title}</h2>
          <div className="data-pair">
            <div>
              <span>Market Demand:</span>
              <b>{item.demand}</b>
            </div>
            <div>
              <span>Promotion Impact:</span>
              <b>{item.impactRating}</b>
            </div>
          </div>
          <p>{item.description}</p>
        </article>
      ))}
    </section>
  )
}
