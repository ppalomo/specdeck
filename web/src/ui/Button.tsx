import { cva, type VariantProps } from 'class-variance-authority'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

import { classes } from './classes'

const button = cva(
  // The parts every button shares: the grid, a radius from the three, and motion inside the
  // system's range. Focus is visible because a panel is a thing people drive from a keyboard.
  'inline-flex items-center justify-center gap-8 rounded-[8px] font-medium ' +
    'transition-colors duration-150 ease-[cubic-bezier(0.22,0.61,0.36,1)] ' +
    'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ' +
    'disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      tone: {
        accent: 'bg-accent text-base hover:opacity-90',
        quiet: 'bg-raised text-text hover:bg-line',
        plain: 'text-muted hover:bg-surface hover:text-text',
      },
      size: {
        small: 'h-32 px-12 text-xs',
        medium: 'h-40 px-16 text-sm',
      },
    },
    defaultVariants: { tone: 'quiet', size: 'medium' },
  },
)

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof button> & { children: ReactNode }

export function Button({ tone, size, className, children, ...rest }: ButtonProps) {
  return (
    <button type="button" className={classes(button({ tone, size }), className)} {...rest}>
      {children}
    </button>
  )
}
