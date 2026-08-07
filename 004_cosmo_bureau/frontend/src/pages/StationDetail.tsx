import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CosmonautCard } from '../components/CosmonautCard'
import { OrbitMap } from '../components/OrbitMap'
import { Badge } from '../components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Progress } from '../components/ui/progress'
import { api, type Cosmonaut, type Mission, type Station } from '../lib/api'
import { MISSION_STATUS_RU, MISSION_STATUS_TONE } from '../lib/labels'

export function StationDetail() {
  const { id } = useParams()
  const stationId = Number(id)
  const [station, setStation] = useState<Station | null>(null)
  const [crew, setCrew] = useState<Cosmonaut[]>([])
  const [missions, setMissions] = useState<Mission[]>([])

  useEffect(() => {
    api.station(stationId).then(setStation)
    api.cosmonauts({ station_id: String(stationId) }).then(setCrew)
    api.missions().then((all) => setMissions(all.filter((m) => m.station_id === stationId)))
  }, [stationId])

  if (!station) {
    return <div className="p-12 text-center font-mono text-xs text-ink-dim blink">ЗАПРОС ТЕЛЕМЕТРИИ…</div>
  }

  const oxygenTone = station.oxygen > 0.7 ? 'green' : station.oxygen > 0.4 ? 'amber' : 'red'

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-[1.1fr_1fr]">
      <div className="space-y-4">
        <div className="rise">
          <h1 className="font-display text-2xl font-bold uppercase tracking-widest text-ink">
            {station.name}
          </h1>
          <div className="mt-1 font-mono text-[11px] uppercase tracking-widest text-ink-dim">
            станция · орбита {Math.round(station.orbit.radius_km - 6371)} км
          </div>
        </div>

        <Card className="rise" style={{ animationDelay: '0.05s' }}>
          <CardHeader>
            <CardTitle>Кислород</CardTitle>
            <CardDescription>{Math.round(station.oxygen * 100)}% номинала</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={station.oxygen} tone={oxygenTone} />
          </CardContent>
        </Card>

        <Card className="rise" style={{ animationDelay: '0.1s' }}>
          <CardHeader>
            <CardTitle>Экипаж на борту · {crew.length}</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {crew.map((cosmonaut) => (
              <CosmonautCard key={cosmonaut.id} cosmonaut={cosmonaut} />
            ))}
            {crew.length === 0 && (
              <div className="font-mono text-xs text-ink-dim">Станция необитаема.</div>
            )}
          </CardContent>
        </Card>

        <Card className="rise" style={{ animationDelay: '0.15s' }}>
          <CardHeader>
            <CardTitle>Связанные миссии</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {missions.map((mission) => (
              <Link
                key={mission.id}
                to="/missions"
                className="flex items-center justify-between rounded-md border border-line bg-panel-2 p-3 transition-colors hover:border-line-2"
              >
                <span className="text-sm text-ink">{mission.name}</span>
                <Badge tone={MISSION_STATUS_TONE[mission.status]}>
                  {MISSION_STATUS_RU[mission.status]}
                </Badge>
              </Link>
            ))}
            {missions.length === 0 && (
              <div className="font-mono text-xs text-ink-dim">Миссий для станции нет.</div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="rise lg:sticky lg:top-20 lg:self-start" style={{ animationDelay: '0.1s' }}>
        <Card className="p-2">
          <OrbitMap
            focus={{ kind: 'station', id: stationId }}
            className="aspect-square w-full"
            timeScale={120}
          />
        </Card>
      </div>
    </div>
  )
}
