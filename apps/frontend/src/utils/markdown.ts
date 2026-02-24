import { marked } from 'marked'

export function renderMarkdown(content: string): string {
  return marked.parse(content, {
    breaks: true,
    gfm: true,
  }) as string
}
