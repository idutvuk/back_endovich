// Ангар: сверху — все ракеты, сгруппированные по статусам; внизу — склад
// с N типами ракет и кнопками постройки (с эффектом сборки).

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import {
  api, ApiError,
  type Resource, type Rocket, type RocketStatus, type RocketType,
} from '../lib/api'
import { ROCKET_STATUS_RU, ROCKET_STATUS_TONE } from '../lib/labels'

const STATUS_ORDER: RocketStatus[] = ['created', 'flying', 'docked', 'descending', 'landed']

export function Hangar() {
  const [rockets, setRockets] = useState<Rocket[]>([])
  const [types, setTypes] = useState<RocketType[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [error, setError] = useState('')
  const [justBuilt, setJustBuilt] = useState<number | null>(null)
  const [buildingCode, setBuildingCode] = useState<string | null>(null)

  const reload = useCallback(() => {
    api.rockets().then(setRockets)
    api.rocketTypes().then(setTypes)
    api.resources().then(setResources)
  }, [])

  useEffect(reload, [reload])

  const build = async (type: RocketType) => {
    setError('')
    setBuildingCode(type.code)
    try {
      const rocket = await api.buildRocket(type.code)
      setJustBuilt(rocket.id)
      reload()
      setTimeout(() => setJustBuilt(null), 1200)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Ошибка связи с ЦУП')
    } finally {
      setTimeout(() => setBuildingCode(null), 400)
    }
  }

  const stock = (name: string) => resources.find((r) => r.name === name)?.amount ?? 0

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8">
      <div className="rise flex items-baseline justify-between">
        <h1 className="font-display text-xl font-bold uppercase tracking-widest text-ink">Ангар</h1>
        <div className="flex gap-3 font-mono text-[11px] uppercase tracking-widest text-ink-dim">
          {resources.map((resource) => (
            <span key={resource.name}>
              {resource.name}: <span className="text-amber">{resource.amount}</span>
            </span>
          ))}
        </div>
      </div>

      {error && (
        <div className="rise rounded-md border border-signal/40 bg-signal/10 p-3 font-mono text-xs text-signal">
          ⚠ {error}
        </div>
      )}

      {/* Флот по статусам */}
      <div className="space-y-4">
        {STATUS_ORDER.map((status) => {
          const group = rockets.filter((rocket) => rocket.status === status)
          if (group.length === 0) return null
          return (
            <div key={status} className="rise">
              <div className="mb-2 flex items-center gap-2">
                <Badge tone={ROCKET_STATUS_TONE[status]}>{ROCKET_STATUS_RU[status]}</Badge>
                <span className="font-mono text-[11px] text-ink-dim">{group.length}</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {group.map((rocket) => (
                  <Link key={rocket.id} to={`/rockets/${rocket.id}`}>
                    <Card
                      className={
                        'p-3 transition-colors hover:border-amber/50 ' +
                        (justBuilt === rocket.id ? 'assemble border-amber/60' : '')
                      }
                    >
                      <div className="flex items-center gap-3">
                        <RocketGlyph kind={rocket.type.kind} />
                        <div className="min-w-0">
                          <div className="truncate text-sm font-medium text-ink">{rocket.name}</div>
                          <div className="font-mono text-[10px] uppercase tracking-widest text-ink-dim">
                            {rocket.type.kind === 'cargo' ? 'грузовая' : 'пассажирская'} · #{rocket.id}
                            {rocket.station_id ? ` · станция #${rocket.station_id}` : ''}
                          </div>
                        </div>
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>
          )
        })}
        {rockets.length === 0 && (
          <div className="py-8 text-center font-mono text-xs text-ink-dim">Флот пуст. Постройте первую ракету.</div>
        )}
      </div>

      {/* Склад: N типов ракет */}
      <div className="rise border-t border-line pt-6" style={{ animationDelay: '0.1s' }}>
        <h2 className="mb-4 font-mono text-[11px] uppercase tracking-[0.3em] text-ink-dim">
          Склад · сборочные линии
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {types.map((type) => {
            const affordable = Object.entries(type.cost).every(
              ([resource, need]) => stock(resource) >= need,
            )
            return (
              <Card
                key={type.code}
                className={buildingCode === type.code ? 'launch-shake' : ''}
              >
                <CardHeader className="flex-row items-center gap-3">
                  <RocketGlyph kind={type.kind} large />
                  <div>
                    <CardTitle>{type.name}</CardTitle>
                    <CardDescription>
                      {type.kind === 'cargo' ? 'грузовая' : 'пассажирская'} · вместимость{' '}
                      {type.capacity} {type.kind === 'cargo' ? 'т' : 'чел.'}
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent className="flex items-center justify-between gap-3">
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(type.cost).map(([resource, need]) => (
                      <Badge key={resource} tone={stock(resource) >= need ? 'dim' : 'red'}>
                        {need} т {resource}
                      </Badge>
                    ))}
                  </div>
                  <Button size="sm" disabled={!affordable} onClick={() => build(type)}>
                    Построить
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function RocketGlyph({ kind, large }: { kind: string; large?: boolean }) {
  const size = large ? 'size-10' : 'size-8'
  const color = kind === 'cargo' ? 'text-sky' : 'text-phosphor'
  return (
    <svg viewBox="0 0 24 40" className={`${size} shrink-0 ${color}`} fill="currentColor">
      <path d="M12 0 C16 6 18 12 18 20 L18 30 L14 27 L10 27 L6 30 L6 20 C6 12 8 6 12 0 Z" opacity="0.9" />
      <circle cx="12" cy="14" r="2.5" fill="#060a13" />
      <path d="M6 28 L2 36 L6 34 Z M18 28 L22 36 L18 34 Z" opacity="0.7" />
      <path d="M10 31 L12 40 L14 31 Z" fill="#ffb545" opacity="0.85" />
    </svg>
  )
}
