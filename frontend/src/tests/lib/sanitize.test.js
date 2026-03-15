import { describe, it, expect } from 'vitest';
import { safeHtml } from '../../lib/sanitize';

describe('safeHtml', () => {
  it('renders normal markdown heading', () => {
    const result = safeHtml('## Heading');
    expect(result).toContain('<h2');
    expect(result).toContain('Heading');
  });

  it('renders bold and italic markdown', () => {
    const result = safeHtml('**bold** *italic*');
    expect(result).toContain('<strong>bold</strong>');
    expect(result).toContain('<em>italic</em>');
  });

  it('strips <script> tags', () => {
    const result = safeHtml('<script>alert(1)</script>');
    expect(result).not.toContain('<script>');
    expect(result).not.toContain('alert(1)');
  });

  it('strips onerror event attributes', () => {
    const result = safeHtml('<img src=x onerror=alert(1)>');
    expect(result).not.toContain('onerror');
  });

  it('strips javascript: URLs from anchor tags', () => {
    const result = safeHtml('<a href="javascript:alert(1)">click</a>');
    expect(result).not.toContain('javascript:');
  });

  it('returns empty string for empty input', () => {
    expect(safeHtml('')).toBe('');
  });

  it('returns empty string for null input', () => {
    expect(safeHtml(null)).toBe('');
  });

  it('returns empty string for undefined input', () => {
    expect(safeHtml(undefined)).toBe('');
  });

  it('preserves safe links in markdown', () => {
    const result = safeHtml('[link](https://example.com)');
    expect(result).toContain('<a');
    expect(result).toContain('href="https://example.com"');
  });

  it('renders unordered lists', () => {
    const result = safeHtml('- item one\n- item two');
    expect(result).toContain('<ul>');
    expect(result).toContain('<li>item one</li>');
  });

  it('renders inline code', () => {
    const result = safeHtml('use `console.log()`');
    expect(result).toContain('<code>');
  });
});
