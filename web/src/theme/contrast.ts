/**
 * Contrast, computed rather than eyeballed.
 *
 * A palette is always claimed to be legible and sometimes is not, and the pair that fails is
 * never the one anybody thought to check. So the arithmetic is here: OKLCH to linear sRGB,
 * and the WCAG 2 ratio between two of them.
 *
 * Done in numbers rather than through a browser on purpose. jsdom resolves neither `var()`
 * nor `oklch()`, and a test that needs a real browser to say whether the palette is readable
 * is a test that will be skipped the first time it is inconvenient.
 */

const OKLCH = /^oklch\(\s*([\d.]+)%?\s+([\d.]+)\s+([\d.]+)/

/** OKLCH as written in the stylesheet, to linear sRGB channels. */
export function linearRgb(colour: string): [number, number, number] {
  const parsed = OKLCH.exec(colour.trim())
  if (parsed === null) throw new Error(`not an oklch colour: ${colour}`)

  const lightness = Number(parsed[1]) / (colour.includes('%') ? 100 : 1)
  const chroma = Number(parsed[2])
  const hue = (Number(parsed[3]) * Math.PI) / 180

  const a = chroma * Math.cos(hue)
  const b = chroma * Math.sin(hue)

  // OKLab to cone responses, then cubed: the one step that is not a matrix.
  const long = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
  const medium = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
  const short = (lightness - 0.0894841775 * a - 1.291485548 * b) ** 3

  return [
    4.0767416621 * long - 3.3077115913 * medium + 0.2309699292 * short,
    -1.2684380046 * long + 2.6097574011 * medium - 0.3413193965 * short,
    -0.0041960863 * long - 0.7034186147 * medium + 1.707614701 * short,
  ]
}

/** Relative luminance, which is the linear channels weighted as an eye weights them. */
export function luminance(colour: string): number {
  const [red, green, blue] = linearRgb(colour)
  const clamp = (channel: number): number => Math.min(1, Math.max(0, channel))

  return 0.2126 * clamp(red) + 0.7152 * clamp(green) + 0.0722 * clamp(blue)
}

export function contrast(foreground: string, background: string): number {
  const one = luminance(foreground)
  const other = luminance(background)
  const [lighter, darker] = one > other ? [one, other] : [other, one]

  return (lighter + 0.05) / (darker + 0.05)
}
