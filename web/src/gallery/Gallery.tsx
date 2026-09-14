import { Moon, Sun } from 'lucide-react'

import { ServerLine } from './ServerLine'
import { Appear } from '../ui/Appear'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { classes } from '../ui/classes'
import { OperationLabel, StatusLabel } from '../ui/Label'
import { ProgressRing } from '../ui/ProgressRing'
import { Skeleton } from '../ui/Skeleton'
import { EmptyState, ErrorState } from '../ui/States'
import {
  ACCENTS,
  ACCENT_CLASS,
  LAYERS,
  LAYER_CLASS,
  OPERATIONS,
  STATUSES,
  TEXT,
  TEXT_CLASS,
} from '../theme/tokens'
import { useTheme } from '../theme/useTheme'

/**
 * The design system, shown with the same pieces the screens are built from.
 *
 * It is part of the application rather than a document beside it. A styleguide kept
 * separately is out of date the first afternoon somebody is in a hurry; one that is the
 * application cannot be, because when a component changes this changes with it.
 *
 * This is the place to look before writing a new component.
 */
export function Gallery() {
  const { theme, toggle } = useTheme()

  return (
    <div className="min-h-screen bg-base px-32 py-40">
      <div className="mx-auto flex max-w-[960px] flex-col gap-40">
        <header className="flex items-start justify-between gap-16">
          <div className="flex flex-col gap-4">
            <h1 className="text-xl font-semibold text-text">Specdeck design system</h1>
            <p className="text-sm text-muted">
              Every token and every piece, in the state you will use it. Look here before
              writing a new one.
            </p>
          </div>
          <Button tone="quiet" size="small" onClick={toggle} aria-label="Switch theme">
            {theme === 'dark' ? <Moon size={16} strokeWidth={1.75} /> : <Sun size={16} strokeWidth={1.75} />}
            {theme === 'dark' ? 'Dark' : 'Light'}
          </Button>
        </header>

        <Appear className="flex flex-col gap-40">
          <Section title="Layers" note="Told apart by luminosity and a soft shadow, never by a border.">
            <div className="flex flex-wrap gap-16">
              {LAYERS.map((layer) => (
                <div
                  key={layer}
                  className={classes(
                    'flex h-64 w-160 items-center justify-center rounded-[12px]',
                    'shadow-[var(--shadow-surface)]',
                    LAYER_CLASS[layer],
                  )}
                >
                  <code className="font-mono text-xs text-muted">{layer}</code>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Text" note="Three weights of attention, all of them legible on all three layers.">
            <div className="flex flex-col gap-8">
              {TEXT.map((name) => (
                <p key={name} className={classes('text-sm', TEXT_CLASS[name])}>
                  <code className="font-mono text-xs">--colour-{name}</code> — the quick brown
                  fox jumps over the lazy dog
                </p>
              ))}
            </div>
          </Section>

          <Section title="Type" note="Geist for the interface, Geist Mono for paths and code. Five sizes, three weights.">
            <div className="flex flex-col gap-8">
              <p className="text-xl font-semibold text-text">Extra large, semibold</p>
              <p className="text-lg font-medium text-text">Large, medium</p>
              <p className="text-base text-text">Base, regular</p>
              <p className="text-sm text-muted">Small, regular</p>
              <p className="font-mono text-xs text-faint">openspec/changes/add-reminders/tasks.md</p>
            </div>
          </Section>

          <Section title="Accents" note="Eight, harmonised. One per registered repository.">
            <div className="flex flex-wrap gap-8">
              {ACCENTS.map((number) => (
                <div
                  key={number}
                  className={classes(
                    'flex size-48 items-center justify-center rounded-[8px]',
                    ACCENT_CLASS[number],
                  )}
                >
                  <span className="font-mono text-xs text-base">{number}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Meanings" note="Fixed everywhere. Always written as well as painted.">
            <div className="flex flex-col gap-16">
              <div className="flex flex-wrap gap-8">
                {OPERATIONS.map((operation) => (
                  <OperationLabel key={operation} operation={operation} />
                ))}
              </div>
              <div className="flex flex-wrap gap-8">
                {STATUSES.map((status) => (
                  <StatusLabel key={status} status={status} />
                ))}
              </div>
            </div>
          </Section>

          <Section title="Buttons" note="Three tones, two sizes, and a visible focus ring.">
            <div className="flex flex-wrap items-center gap-8">
              <Button tone="accent">Validate</Button>
              <Button tone="quiet">Open in editor</Button>
              <Button tone="plain">Copy path</Button>
              <Button tone="quiet" size="small">
                Small
              </Button>
              <Button tone="accent" disabled>
                Disabled
              </Button>
            </div>
          </Section>

          <Section title="Progress" note="The numbers as well as the ring. No tasks is not nought per cent.">
            <div className="flex flex-wrap items-center gap-24">
              <ProgressRing done={0} total={8} />
              <ProgressRing done={12} total={25} />
              <ProgressRing done={9} total={9} />
              <ProgressRing done={0} total={0} />
            </div>
          </Section>

          <Section title="Cards" note="On the surface layer, lifted by shadow alone.">
            <div className="grid grid-cols-2 gap-16">
              <Card>
                <div className="flex items-center justify-between gap-16">
                  <div className="flex flex-col gap-4">
                    <p className="text-base font-medium text-text">add-reminders</p>
                    <code className="font-mono text-xs text-faint">spec-driven</code>
                  </div>
                  <ProgressRing done={1} total={4} />
                </div>
              </Card>
              <Card>
                <div className="flex flex-col gap-12">
                  <p className="text-base font-medium text-text">retire-old-reports</p>
                  <div className="flex flex-wrap gap-8">
                    <StatusLabel status="done" />
                    <StatusLabel status="ready" />
                  </div>
                </div>
              </Card>
            </div>
          </Section>

          <Section title="Waiting" note="Only the first time. Refreshing is not loading.">
            <div className="flex flex-col gap-8">
              <Skeleton className="h-40 w-full" />
              <Skeleton className="h-40 w-3/4" />
              <Skeleton className="h-40 w-1/2" />
            </div>
          </Section>

          <Section title="Nothing here, and something wrong" note="Both designed. They must not be mistaken for each other.">
            <div className="grid grid-cols-2 gap-16">
              <EmptyState
                what="No changes in flight"
                why="Nothing is being worked on in this repository right now."
                action={<Button tone="quiet" size="small">Copy the command to propose one</Button>}
              />
              <ErrorState
                what="Could not read this repository"
                reason="the openspec executable is not installed or not on the PATH"
                onRetry={() => undefined}
              />
            </div>
          </Section>
        </Appear>

        <footer className="pt-16 text-xs text-faint">
          <ServerLine />
        </footer>
      </div>
    </div>
  )
}

function Section({ title, note, children }: { title: string; note: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-16">
      <div className="flex flex-col gap-4">
        <h2 className="text-lg font-medium text-text">{title}</h2>
        <p className="text-sm text-muted">{note}</p>
      </div>
      {children}
    </section>
  )
}
