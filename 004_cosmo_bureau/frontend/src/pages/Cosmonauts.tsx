import { useEffect, useState } from 'react'
import { CosmonautCard } from '../components/CosmonautCard'
import { Input, Select } from '../components/ui/input'
import { api, type Cosmonaut } from '../lib/api'

const ZODIACS = [
  'Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
  'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы',
]

export function Cosmonauts() {
  const [roster, setRoster] = useState<Cosmonaut[]>([])
  const [name, setName] = useState('')
  const [country, setCountry] = useState('')
  const [zodiac, setZodiac] = useState('')
  const [inSpace, setInSpace] = useState('')

  useEffect(() => {
    const params: Record<string, string> = {}
    if (name) params.name = name
    if (country) params.country = country
    if (zodiac) params.zodiac = zodiac
    if (inSpace) params.in_space = inSpace
    const timer = setTimeout(() => api.cosmonauts(params).then(setRoster), 200)
    return () => clearTimeout(timer)
  }, [name, country, zodiac, inSpace])

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="rise mb-6 font-display text-xl font-bold uppercase tracking-widest text-ink">
        Отряд космонавтов
      </h1>
      <div className="rise mb-6 grid gap-2 sm:grid-cols-4" style={{ animationDelay: '0.05s' }}>
        <Input placeholder="Поиск по имени…" value={name} onChange={(e) => setName(e.target.value)} />
        <Input placeholder="Страна…" value={country} onChange={(e) => setCountry(e.target.value)} />
        <Select value={zodiac} onChange={(e) => setZodiac(e.target.value)}>
          <option value="">Любой знак</option>
          {ZODIACS.map((sign) => (
            <option key={sign} value={sign}>{sign}</option>
          ))}
        </Select>
        <Select value={inSpace} onChange={(e) => setInSpace(e.target.value)}>
          <option value="">Где угодно</option>
          <option value="true">В космосе</option>
          <option value="false">На Земле</option>
        </Select>
      </div>
      <div className="grid gap-2">
        {roster.map((cosmonaut, index) => (
          <CosmonautCard
            key={cosmonaut.id}
            cosmonaut={cosmonaut}
            style={{ animationDelay: `${index * 0.04}s` }}
          />
        ))}
        {roster.length === 0 && (
          <div className="py-12 text-center font-mono text-xs text-ink-dim">
            Никого не нашли. Отряд пуст или фильтры слишком строгие.
          </div>
        )}
      </div>
    </div>
  )
}
