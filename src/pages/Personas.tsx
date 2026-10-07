import { personas } from '../data/constants'

export function Personas() {
  return (
    <section className="persona-grid">
      {personas.map((persona) => (
        <article className="card persona-card" key={persona[0]}>
          <div className="card-meta"><span className="number">{persona[0]}</span><span className="badge">{persona[1]}</span></div>
          <h2>{persona[2]}</h2>
          <p>{persona[3]}</p>
        </article>
      ))}
    </section>
  )
}
