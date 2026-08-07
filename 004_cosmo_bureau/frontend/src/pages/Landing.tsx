import { Link } from 'react-router-dom'
import { OrbitMap } from '../components/OrbitMap'
import { Button } from '../components/ui/button'

export function Landing() {
  return (
    <div className="relative mx-auto grid max-w-6xl gap-8 px-4 py-10 lg:grid-cols-[1fr_1.1fr] lg:items-center">
      <div className="rise space-y-6">
        <div className="font-mono text-[11px] uppercase tracking-[0.35em] text-phosphor">
          <span className="blink">●</span> связь со станциями установлена
        </div>
        <h1 className="font-display text-3xl font-extrabold uppercase leading-tight tracking-wide text-ink md:text-5xl">
          Бюро
          <br />
          космонавтики
          <span className="mt-2 block text-sm font-semibold tracking-[0.25em] text-amber md:text-lg">
            им. Героя России Синса
          </span>
        </h1>
        <p className="max-w-md text-sm leading-relaxed text-ink-dim">
          Модули обеспечения полётов и нахождения космонавтов. Строим ракеты из
          говна и палок — доставляем людей и грузы на орбитальные станции.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/missions">
            <Button>Доска миссий</Button>
          </Link>
          <Link to="/hangar">
            <Button variant="outline">В ангар</Button>
          </Link>
        </div>
      </div>
      <div className="rise" style={{ animationDelay: '0.15s' }}>
        <OrbitMap className="mx-auto aspect-square w-full max-w-135" timeScale={120} />
      </div>
    </div>
  )
}
