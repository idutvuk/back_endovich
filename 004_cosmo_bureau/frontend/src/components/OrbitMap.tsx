// Живая карта орбит: Земля в центре, тонкие линии орбит, станции и ракеты
// движутся по данным /map (клиентская пропагация, без повторных запросов).

import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type WorldMap } from '../lib/api'
import { toXY } from '../lib/orbits'

const VIEW = 1000
const CENTER = VIEW / 2

interface Props {
  interactive?: boolean
  /** Подсветить конкретный объект (страница деталей) */
  focus?: { kind: 'station' | 'rocket'; id: number }
  className?: string
  /** Ускорение времени, чтобы движение было заметно глазу */
  timeScale?: number
}

export function OrbitMap({ interactive = false, focus, className, timeScale = 60 }: Props) {
  const [world, setWorld] = useState<WorldMap | null>(null)
  const fetchedAt = useRef(0)
  const [, forceTick] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    api.worldMap().then((data) => {
      fetchedAt.current = Date.now()
      setWorld(data)
    })
  }, [])

  useEffect(() => {
    let raf = 0
    const tick = () => {
      forceTick((n) => n + 1)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  if (!world) {
    return (
      <div className={className}>
        <div className="grid h-full min-h-40 place-items-center font-mono text-xs text-ink-dim">
          <span className="blink">УСТАНОВКА СВЯЗИ…</span>
        </div>
      </div>
    )
  }

  const maxRadius = Math.max(
    ...world.stations.map((s) => s.position.radius_km),
    ...world.rockets.map((r) => r.position.radius_km),
    world.earth_radius_km * 1.4,
  )
  const scale = (CENTER - 60) / maxRadius
  const earthR = world.earth_radius_km * scale

  // Виртуальное «ускоренное» время: elapsed * timeScale
  const virtualNow = fetchedAt.current + (Date.now() - fetchedAt.current) * timeScale

  const project = (angleDeg: number, radiusKm: number) => {
    const { x, y } = toXY(angleDeg, radiusKm * scale)
    return { x: CENTER + x, y: CENTER + y }
  }

  const liveAngle = (pos: WorldMap['stations'][0]['position']) => {
    const elapsedMin = (virtualNow - fetchedAt.current) / 60_000
    return (pos.angle_deg + (360 * elapsedMin) / pos.period_min) % 360
  }

  return (
    <svg
      viewBox={`0 0 ${VIEW} ${VIEW}`}
      className={className}
      role={interactive ? 'application' : 'img'}
      aria-label="Карта орбит"
    >
      <defs>
        <radialGradient id="earth-glow" cx="35%" cy="35%">
          <stop offset="0%" stopColor="#3f7fd4" />
          <stop offset="55%" stopColor="#1d4a8f" />
          <stop offset="100%" stopColor="#0a1e42" />
        </radialGradient>
        <radialGradient id="atmo" cx="50%" cy="50%">
          <stop offset="78%" stopColor="transparent" />
          <stop offset="92%" stopColor="#6fb7ff33" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>

      {/* атмосфера + Земля */}
      <circle cx={CENTER} cy={CENTER} r={earthR * 1.35} fill="url(#atmo)" />
      <circle cx={CENTER} cy={CENTER} r={earthR} fill="url(#earth-glow)" />
      <ellipse cx={CENTER - earthR * 0.25} cy={CENTER - earthR * 0.2} rx={earthR * 0.45} ry={earthR * 0.28} fill="#4f9e6a55" />
      <ellipse cx={CENTER + earthR * 0.3} cy={CENTER + earthR * 0.25} rx={earthR * 0.35} ry={earthR * 0.2} fill="#4f9e6a44" />

      {/* орбиты станций */}
      {world.stations.map((station) => (
        <circle
          key={`orbit-${station.id}`}
          cx={CENTER}
          cy={CENTER}
          r={station.position.radius_km * scale}
          fill="none"
          stroke="#2a3b60"
          strokeWidth="1"
          strokeDasharray="3 5"
        />
      ))}

      {/* станции */}
      {world.stations.map((station) => {
        const point = project(liveAngle(station.position), station.position.radius_km)
        const focused = focus?.kind === 'station' && focus.id === station.id
        return (
          <g
            key={`station-${station.id}`}
            transform={`translate(${point.x}, ${point.y})`}
            className={interactive ? 'cursor-pointer' : undefined}
            onClick={interactive ? () => navigate(`/stations/${station.id}`) : undefined}
          >
            {focused && <circle r="22" fill="none" stroke="#ffb545" strokeWidth="1.5" className="blink" />}
            <rect x="-9" y="-4" width="18" height="8" rx="1.5" fill="#dbe4f5" />
            <rect x="-16" y="-2.5" width="6" height="5" rx="1" fill="#6fb7ff" />
            <rect x="10" y="-2.5" width="6" height="5" rx="1" fill="#6fb7ff" />
            <text y="-12" textAnchor="middle" fill="#7f8fb0" fontSize="13" fontFamily="JetBrains Mono, monospace">
              {station.name}
            </text>
          </g>
        )
      })}

      {/* ракеты на орбитах */}
      {world.rockets.map((rocket) => {
        const point = project(liveAngle(rocket.position), rocket.position.radius_km)
        const focused = focus?.kind === 'rocket' && focus.id === rocket.id
        return (
          <g
            key={`rocket-${rocket.id}`}
            transform={`translate(${point.x}, ${point.y})`}
            className={interactive ? 'cursor-pointer' : undefined}
            onClick={interactive ? () => navigate(`/rockets/${rocket.id}`) : undefined}
          >
            {focused && <circle r="18" fill="none" stroke="#ffb545" strokeWidth="1.5" className="blink" />}
            <polygon points="0,-8 5,6 0,3 -5,6" fill={rocket.status === 'docked' ? '#5df0a2' : '#ffb545'} />
            {interactive && (
              <text y="18" textAnchor="middle" fill="#7f8fb0" fontSize="11" fontFamily="JetBrains Mono, monospace">
                {rocket.name}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}
