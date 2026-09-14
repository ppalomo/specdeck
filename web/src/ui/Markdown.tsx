import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * An artifact, read as the document it is.
 *
 * The column is capped at a reading width whatever the window does: a line that crosses a
 * 27-inch screen is not read, it is scanned. Tables and code blocks are the only things that
 * can be wider than that, and each gets its own scrolling box — the page itself never moves
 * sideways, which is the rule, but a wide table stays readable.
 */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="flex flex-col gap-16 text-sm text-muted">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children: content }) => (
            <h1 className="max-w-[72ch] text-lg font-semibold text-text">{content}</h1>
          ),
          h2: ({ children: content }) => (
            <h2 className="max-w-[72ch] pt-8 text-base font-medium text-text">{content}</h2>
          ),
          h3: ({ children: content }) => (
            <h3 className="max-w-[72ch] text-sm font-medium text-text">{content}</h3>
          ),
          p: ({ children: content }) => <p className="max-w-[72ch]">{content}</p>,
          ul: ({ children: content }) => (
            <ul className="flex max-w-[72ch] list-disc flex-col gap-4 pl-16">{content}</ul>
          ),
          ol: ({ children: content }) => (
            <ol className="flex max-w-[72ch] list-decimal flex-col gap-4 pl-16">{content}</ol>
          ),
          strong: ({ children: content }) => (
            <strong className="font-medium text-text">{content}</strong>
          ),
          code: ({ children: content }) => (
            <code className="rounded-[8px] bg-raised px-4 font-mono text-xs">{content}</code>
          ),
          pre: ({ children: content }) => (
            <pre className="max-w-[72ch] overflow-x-auto rounded-[8px] bg-raised p-12 font-mono text-xs">
              {content}
            </pre>
          ),
          table: ({ children: content }) => (
            <div className="max-w-full overflow-x-auto">
              <table className="text-xs">{content}</table>
            </div>
          ),
          th: ({ children: content }) => (
            <th className="px-8 py-4 text-left font-medium text-text">{content}</th>
          ),
          td: ({ children: content }) => <td className="px-8 py-4 align-top">{content}</td>,
          a: ({ children: content, href }) => (
            <a href={href} className="text-accent underline underline-offset-4">
              {content}
            </a>
          ),
          blockquote: ({ children: content }) => (
            <blockquote className="max-w-[72ch] rounded-[8px] bg-surface px-12 py-8">
              {content}
            </blockquote>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
