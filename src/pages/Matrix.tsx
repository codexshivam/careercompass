import { matrixItems } from '../data/constants'

export function Matrix() {
  return (
    <section className="matrix-grid">
      {matrixItems.map((item) => (
        <article className="card matrix-card" key={item[2]}>
          <div className="card-meta"><span className="badge">{item[0]}</span><strong>{item[1]}</strong></div>
          <h2>{item[2]}</h2>
          <div className="data-pair">
            <div><span>Market Demand:</span><b>{item[3]}</b></div>
            <div><span>Promotion Impact:</span><b>{item[4]}</b></div>
          </div>
          <p>{item[5]}</p>
        </article>
      ))}
    </section>
  )
}
