// Единый элемент списка космонавта: используется и в общем списке,
// и на страницах станции/ракеты.

import type { CSSProperties } from 'react'
import type { Cosmonaut } from '../lib/api'
import { avatarHue, initials } from '../lib/labels'
import { Badge } from './ui/badge'
import { Card } from './ui/card'

export function CosmonautCard({ cosmonaut, style }: { cosmonaut: Cosmonaut; style?: CSSProperties }) {
  const hue = avatarHue(cosmonaut.name)
  return (
    <Card className="rise flex items-center gap-3 p-3 transition-colors hover:border-line-2" style={style}>
      <div
        className="grid size-11 shrink-0 place-items-center rounded-full font-display text-sm font-semibold"
        style={{
          background: `linear-gradient(135deg, hsl(${hue} 60% 22%), hsl(${hue} 70% 38%))`,
          color: `hsl(${hue} 90% 85%)`,
          border: `1px solid hsl(${hue} 60% 45% / 0.5)`,
        }}
      >
        {initials(cosmonaut.name)}
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-medium text-ink">{cosmonaut.name}</div>
        <div className="font-mono text-[11px] text-ink-dim">
          {cosmonaut.country} · {cosmonaut.zodiac} ·{' '}
          {new Date(cosmonaut.birth_date).toLocaleDateString('ru-RU')}
        </div>
      </div>
      {cosmonaut.in_space ? (
        <Badge tone="green">в космосе</Badge>
      ) : (
        <Badge tone="dim">на Земле</Badge>
      )}
    </Card>
  )
}
