import type { InputHTMLAttributes, SelectHTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        'h-9 w-full rounded-md border border-line bg-panel-2 px-3 font-mono text-xs text-ink placeholder:text-ink-dim/60 outline-none transition-colors focus:border-amber/60 focus:shadow-[0_0_0_3px_#ffb54518]',
        className,
      )}
      {...props}
    />
  )
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        'h-9 rounded-md border border-line bg-panel-2 px-2 font-mono text-xs text-ink outline-none transition-colors focus:border-amber/60',
        className,
      )}
      {...props}
    />
  )
}
