import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CosmonautCard } from '../components/CosmonautCard'
import { OrbitMap } from '../components/OrbitMap'
import { Badge } from '../components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { api, type Cosmonaut, type Mission, type Rocket } from '../lib/api'
import {
  MISSION_STATUS_RU,
  MISSION_STATUS_TONE,
  ROCKET_STATUS_RU,
  ROCKET_STATUS_TONE,
} from '../lib/labels'

export function RocketDetail() {
  const { id } = useParams()
  const rocketId = Number(id)
  const [rocket, setRocket] = useState<Rocket | null>(null)
  const [crew, setCrew] = useState<Cosmonaut[]>([])
  const [mission, setMission] = useState<Mission | null>(null)

  useEffect(() => {
    api.rocket(rocketId).then((data) => {
      setRocket(data)
      if (data.mission_id) api.mission(data.mission_id).then(setMission)
    })
    api.cosmonauts().then((all) => setCrew(all.filter((c) => c.rocket_id === rocketId)))
  }, [rocketId])

  if (!rocket) {
    return <div className="p-12 text-center font-mono text-xs text-ink-dim blink">ЗАПРОС ТЕЛЕМЕТРИИ…</div>
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-[1.1fr_1fr]">
      <div className="space-y-4">
        <div className="rise">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-display text-2xl font-bold uppercase tracking-widest text-ink">
              {rocket.name}
            </h1>
            <Badge tone={ROCKET_STATUS_TONE[rocket.status]}>{ROCKET_STATUS_RU[rocket.status]}</Badge>
          </div>
          <div className="mt-1 font-mono text-[11px] uppercase tracking-widest text-ink-dim">
            {rocket.type.kind === 'cargo' ? 'грузовая' : 'пассажирская'} · {rocket.type.name} ·
            вместимость {rocket.type.capacity} {rocket.type.kind === 'cargo' ? 'т' : 'чел.'}
          </div>
        </div>

        {rocket.station_id && (
          <Card className="rise" style={{ animationDelay: '0.05s' }}>
            <CardContent className="p-4">
              <Link
                to={`/stations/${rocket.station_id}`}
                className="font-mono text-xs uppercase tracking-widest text-sky hover:text-amber"
              >
                → приписана к станции #{rocket.station_id}
              </Link>
            </CardContent>
          </Card>
        )}

        <Card className="rise" style={{ animationDelay: '0.1s' }}>
          <CardHeader>
            <CardTitle>Люди на борту · {crew.length}</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {crew.map((cosmonaut) => (
              <CosmonautCard key={cosmonaut.id} cosmonaut={cosmonaut} />
            ))}
            {crew.length === 0 && (
              <div className="font-mono text-xs text-ink-dim">Борт пуст.</div>
            )}
          </CardContent>
        </Card>

        {mission && (
          <Card className="rise" style={{ animationDelay: '0.15s' }}>
            <CardHeader>
              <CardTitle>Миссия</CardTitle>
              <CardDescription>{mission.name}</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
              <span className="font-mono text-xs text-ink-dim">
                {mission.cargo_tons > 0 ? `${mission.cargo_tons} т груза · ` : ''}
                награда {mission.reward} кр.
              </span>
              <Badge tone={MISSION_STATUS_TONE[mission.status]}>
                {MISSION_STATUS_RU[mission.status]}
              </Badge>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="rise lg:sticky lg:top-20 lg:self-start" style={{ animationDelay: '0.1s' }}>
        <Card className="p-2">
          {rocket.orbit ? (
            <OrbitMap
              focus={{ kind: 'rocket', id: rocketId }}
              className="aspect-square w-full"
              timeScale={120}
            />
          ) : (
            <div className="grid aspect-square place-items-center font-mono text-xs text-ink-dim">
              {rocket.status === 'landed' ? 'Ракета на Земле. Полёт окончен.' : 'Ракета в ангаре.'}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
