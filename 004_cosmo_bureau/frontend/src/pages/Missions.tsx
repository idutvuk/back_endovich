// Канбан миссий: колонки по статусам, перетаскивание карточек (HTML5 DnD).
// Взятие миссии требует ракету+экипаж — отдельная форма в карточке.

import { useCallback, useEffect, useState } from 'react'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Select } from '../components/ui/input'
import { api, ApiError, type Cosmonaut, type Mission, type MissionStatus, type Rocket } from '../lib/api'
import { MISSION_STATUS_RU } from '../lib/labels'
import { cn } from '../lib/utils'

const COLUMNS: { status: MissionStatus; accent: string }[] = [
  { status: 'open', accent: 'border-t-amber' },
  { status: 'taken', accent: 'border-t-sky' },
  { status: 'done', accent: 'border-t-phosphor' },
  { status: 'cancelled', accent: 'border-t-signal' },
]

export function Missions() {
  const [missions, setMissions] = useState<Mission[]>([])
  const [rockets, setRockets] = useState<Rocket[]>([])
  const [cosmonauts, setCosmonauts] = useState<Cosmonaut[]>([])
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState<MissionStatus | null>(null)
  const [taking, setTaking] = useState<number | null>(null)

  const reload = useCallback(() => {
    api.missions().then(setMissions)
    api.rockets().then(setRockets)
    api.cosmonauts().then(setCosmonauts)
  }, [])

  useEffect(reload, [reload])

  const flash = (message: string) => {
    setError(message)
    setTimeout(() => setError(''), 4000)
  }

  const onDrop = async (missionId: number, target: MissionStatus) => {
    setDragOver(null)
    const mission = missions.find((m) => m.id === missionId)
    if (!mission || mission.status === target) return
    if (target === 'taken') {
      setTaking(missionId)
      return
    }
    try {
      await api.moveMission(missionId, target)
      reload()
    } catch (e) {
      flash(e instanceof ApiError ? e.message : 'Ошибка связи с ЦУП')
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="rise mb-6 flex items-baseline justify-between">
        <h1 className="font-display text-xl font-bold uppercase tracking-widest text-ink">
          Доска миссий
        </h1>
        {error && (
          <span className="font-mono text-xs text-signal">⚠ {error}</span>
        )}
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {COLUMNS.map((column, columnIndex) => {
          const cards = missions.filter((m) => m.status === column.status)
          return (
            <div
              key={column.status}
              className={cn(
                'rise rounded-lg border border-line border-t-2 bg-panel/40 p-3 transition-colors',
                column.accent,
                dragOver === column.status && 'bg-panel-2/70 border-line-2',
              )}
              style={{ animationDelay: `${columnIndex * 0.06}s` }}
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(column.status)
              }}
              onDragLeave={() => setDragOver(null)}
              onDrop={(e) => {
                const id = Number(e.dataTransfer.getData('mission'))
                if (id) onDrop(id, column.status)
              }}
            >
              <div className="mb-3 flex items-center justify-between px-1">
                <span className="font-mono text-[11px] uppercase tracking-[0.25em] text-ink-dim">
                  {MISSION_STATUS_RU[column.status]}
                </span>
                <span className="font-mono text-[11px] text-ink-dim">{cards.length}</span>
              </div>
              <div className="grid min-h-24 content-start gap-2">
                {cards.map((mission) => (
                  <MissionCard
                    key={mission.id}
                    mission={mission}
                    rockets={rockets}
                    cosmonauts={cosmonauts}
                    taking={taking === mission.id}
                    onTakeStart={() => setTaking(mission.id)}
                    onTakeEnd={() => setTaking(null)}
                    onChanged={reload}
                    onError={flash}
                  />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MissionCard({
  mission, rockets, cosmonauts, taking, onTakeStart, onTakeEnd, onChanged, onError,
}: {
  mission: Mission
  rockets: Rocket[]
  cosmonauts: Cosmonaut[]
  taking: boolean
  onTakeStart: () => void
  onTakeEnd: () => void
  onChanged: () => void
  onError: (message: string) => void
}) {
  const [rocketId, setRocketId] = useState('')
  const [crewIds, setCrewIds] = useState<number[]>([])

  const availableRockets = rockets.filter((r) => r.status === 'created' && r.mission_id === null)
  const availableCrew = cosmonauts.filter((c) => !c.in_space && c.rocket_id === null)
  const needsCrew = mission.cargo_tons === 0

  const take = async () => {
    try {
      await api.takeMission(mission.id, Number(rocketId), crewIds)
      onTakeEnd()
      onChanged()
    } catch (e) {
      onError(e instanceof ApiError ? e.message : 'Ошибка связи с ЦУП')
    }
  }

  return (
    <Card
      draggable
      onDragStart={(e) => e.dataTransfer.setData('mission', String(mission.id))}
      className="cursor-grab active:cursor-grabbing"
    >
      <CardHeader>
        <CardTitle className="text-[13px]">{mission.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex flex-wrap gap-1.5">
          {mission.cargo_tons > 0 && <Badge tone="blue">{mission.cargo_tons} т груза</Badge>}
          {mission.crew.length > 0 && <Badge tone="green">экипаж {mission.crew.length}</Badge>}
          <Badge tone="amber">{mission.reward} кр.</Badge>
        </div>
        {mission.deadline && (
          <div className="font-mono text-[10px] uppercase tracking-widest text-ink-dim">
            дедлайн {new Date(mission.deadline).toLocaleDateString('ru-RU')}
          </div>
        )}
        {mission.rocket_id && (
          <div className="font-mono text-[10px] uppercase tracking-widest text-ink-dim">
            ракета #{mission.rocket_id}
          </div>
        )}

        {mission.status === 'open' && !taking && (
          <Button size="sm" variant="outline" className="w-full" onClick={onTakeStart}>
            Взять миссию
          </Button>
        )}

        {taking && (
          <div className="space-y-2 rounded-md border border-line bg-panel-2 p-2">
            <Select className="w-full" value={rocketId} onChange={(e) => setRocketId(e.target.value)}>
              <option value="">Выбрать ракету…</option>
              {availableRockets.map((rocket) => (
                <option key={rocket.id} value={rocket.id}>
                  {rocket.name} ({rocket.type.kind === 'cargo' ? 'груз' : 'пассажир'})
                </option>
              ))}
            </Select>
            {needsCrew && (
              <div className="grid max-h-32 gap-1 overflow-y-auto">
                {availableCrew.map((cosmonaut) => (
                  <label key={cosmonaut.id} className="flex items-center gap-2 font-mono text-[11px] text-ink">
                    <input
                      type="checkbox"
                      checked={crewIds.includes(cosmonaut.id)}
                      onChange={(e) =>
                        setCrewIds((prev) =>
                          e.target.checked
                            ? [...prev, cosmonaut.id]
                            : prev.filter((id) => id !== cosmonaut.id),
                        )
                      }
                    />
                    {cosmonaut.name}
                  </label>
                ))}
              </div>
            )}
            <div className="flex gap-2">
              <Button size="sm" className="flex-1" disabled={!rocketId} onClick={take}>
                Подтвердить
              </Button>
              <Button size="sm" variant="ghost" onClick={onTakeEnd}>
                Отмена
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
