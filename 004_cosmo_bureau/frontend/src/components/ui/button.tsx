import type { ButtonHTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

const variants = {
  default:
    'bg-amber text-void hover:bg-amber/85 shadow-[0_0_16px_#ffb54533] font-semibold',
  outline:
    'border border-line-2 bg-transparent text-ink hover:border-amber hover:text-amber',
  ghost: 'bg-transparent text-ink-dim hover:text-ink hover:bg-panel-2',
  danger: 'border border-signal/40 bg-signal/10 text-signal hover:bg-signal/20',
} as const

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants
  size?: 'sm' | 'md'
}

export function Button({ className, variant = 'default', size = 'md', ...props }: Props) {
  return (
    <button
      className={cn(
        'inline-flex cursor-pointer items-center justify-center gap-2 rounded-md font-mono uppercase tracking-wider transition-all duration-150 disabled:pointer-events-none disabled:opacity-40',
        size === 'sm' ? 'h-7 px-2.5 text-[11px]' : 'h-9 px-4 text-xs',
        variants[variant],
        className,
      )}
      {...props}
    />
  )
}
