import { OrbitMap } from '../components/OrbitMap'

export function EarthMap() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="rise mb-4 flex items-baseline justify-between">
        <h1 className="font-display text-xl font-bold uppercase tracking-widest text-ink">
          Земля · оперативная обстановка
        </h1>
        <span className="font-mono text-[11px] uppercase tracking-widest text-ink-dim">
          клик по объекту — подробности
        </span>
      </div>
      <div className="rise rounded-xl border border-line bg-panel/60 p-2" style={{ animationDelay: '0.1s' }}>
        <OrbitMap interactive className="aspect-square w-full" timeScale={120} />
      </div>
    </div>
  )
}
