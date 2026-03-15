import DOMPurify from 'dompurify';
import { marked } from 'marked';

export function safeHtml(markdown) {
  if (!markdown) return '';
  return DOMPurify.sanitize(marked.parse(markdown));
}
