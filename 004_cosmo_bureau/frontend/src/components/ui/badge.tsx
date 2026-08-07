import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

const tones = {
  amber: 'border-amber/40 bg-amber/10 text-amber',
  green: 'border-phosphor/40 bg-phosphor/10 text-phosphor',
  red: 'border-signal/40 bg-signal/10 text-signal',
  blue: 'border-sky/40 bg-sky/10 text-sky',
  dim: 'border-line-2 bg-panel-2 text-ink-dim',
} as const

interface Props extends HTMLAttributes<HTMLSpanElement> {
  tone?: keyof typeof tones
}

export function Badge({ className, tone = 'dim', ...props }: Props) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-widest',
        tones[tone],
        className,
      )}
      {...props}
    />
  )
}
