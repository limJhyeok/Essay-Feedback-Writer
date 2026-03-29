import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import ExampleAnswer from '../../components/ExampleAnswer.svelte';

describe('ExampleAnswer component', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn(() => Promise.resolve()) },
    });
  });

  it('renders Example Answer heading', () => {
    const { getByText } = render(ExampleAnswer, {
      props: { exampleAnswer: 'Sample text' },
    });
    expect(getByText('Example Answer')).toBeInTheDocument();
  });

  it('renders example answer content', () => {
    const { container } = render(ExampleAnswer, {
      props: { exampleAnswer: 'This is a sample essay.' },
    });
    expect(container.textContent).toContain('This is a sample essay.');
  });

  it('has a copy button with correct aria-label', () => {
    const { container } = render(ExampleAnswer, {
      props: { exampleAnswer: 'Text' },
    });
    expect(container.querySelector('[aria-label="Copy to clipboard"]')).not.toBeNull();
  });

  it('copy button calls clipboard API', async () => {
    const { container } = render(ExampleAnswer, {
      props: { exampleAnswer: 'Copy me' },
    });
    const btn = container.querySelector('[aria-label="Copy to clipboard"]');
    await fireEvent.click(btn);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Copy me');
  });
});
