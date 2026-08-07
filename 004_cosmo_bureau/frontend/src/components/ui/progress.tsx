import { cn } from '../../lib/utils'

export function Progress({
  value,
  className,
  tone = 'green',
}: {
  value: number // 0..1
  className?: string
  tone?: 'green' | 'amber' | 'red'
}) {
  const color =
    tone === 'red' ? 'bg-signal' : tone === 'amber' ? 'bg-amber' : 'bg-phosphor'
  return (
    <div className={cn('h-1.5 w-full overflow-hidden rounded-full bg-line', className)}>
      <div
        className={cn('h-full rounded-full transition-all duration-700', color)}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  )
}
