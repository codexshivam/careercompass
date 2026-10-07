import { useEffect, useState } from 'react'
import { fetchPersonas } from '../api'
import type { PersonaItem } from '../types'

export function Personas() {
  const [personas, setPersonas] = useState<PersonaItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    fetchPersonas()
      .then((data) => {
        if (!isMounted) return
        setPersonas(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load personas from backend:', err)
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
        Loading leadership personas from server...
      </div>
    )
  }

  return (
    <section className="persona-grid">
      {personas.map((persona) => (
        <article className="card persona-card" key={persona.id}>
          <div className="card-meta">
            <span className="number">{persona.id}</span>
            <span className="badge">{persona.badge}</span>
          </div>
          <h2>{persona.title}</h2>
          <p>{persona.description}</p>
        </article>
      ))}
    </section>
  )
}
