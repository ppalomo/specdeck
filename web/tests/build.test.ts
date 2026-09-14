import { readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

/**
 * What the page is allowed to depend on before it has painted anything.
 *
 * Two promises are easy to break by accident and impossible to notice on the machine that
 * broke them: that the theme is decided before the first paint, and that Specdeck asks the
 * network for nothing. Both fail only for somebody else — on a slow connection, or on a
 * train — which is exactly why they are asserted here.
 */
const web = resolve(import.meta.dirname, '..')
const html = readFileSync(resolve(web, 'index.html'), 'utf8')
const css = readFileSync(resolve(web, 'src/index.css'), 'utf8')

describe('the theme, in the document itself', () => {
  it('is already dark on the element, so nothing paints white first', () => {
    expect(html).toMatch(/<html[^>]*data-theme="dark"/)
  })

  it('reads the stored choice in the head, before the application is asked for', () => {
    const head = html.slice(0, html.indexOf('</head>'))

    expect(head).toContain('specdeck.theme')
    expect(head).toContain('data-theme')
    expect(html.indexOf('specdeck.theme')).toBeLessThan(html.indexOf('src/main.tsx'))
  })
})

describe('the fonts', () => {
  it('are in the repository, both of them, with the licence that has to travel with them', () => {
    const files = readdirSync(resolve(web, 'src/fonts'))

    expect(files).toContain('Geist-Variable.woff2')
    expect(files).toContain('GeistMono-Variable.woff2')
    expect(files).toContain('LICENSE.txt')
  })

  it('are declared against those files', () => {
    expect(css).toContain("src: url('./fonts/Geist-Variable.woff2')")
    expect(css).toContain("src: url('./fonts/GeistMono-Variable.woff2')")
  })
})

describe('what the page fetches', () => {
  it('is nothing from anywhere else', () => {
    for (const source of [html, css]) {
      // A stylesheet, a font or a script pulled from a host. Prose and comments that merely
      // mention a URL are not requests, so only the forms that load something are looked for.
      expect(source).not.toMatch(/url\(\s*['"]?https?:/)
      expect(source).not.toMatch(/@import\s+url\(/)
      expect(source).not.toMatch(/<(link|script)[^>]+(href|src)=["']https?:/)
    }
  })
})
