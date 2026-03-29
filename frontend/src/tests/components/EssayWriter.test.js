import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';

vi.mock('../../components/HandwritingCanvas.svelte', () => ({
  default: {},
}));

import EssayWriter from '../../components/EssayWriter.svelte';

describe('EssayWriter component', () => {
  it('shows placeholder when no promptContent', () => {
    const { getByText, container } = render(EssayWriter, {
      props: { promptContent: '' },
    });
    expect(getByText('Please select a prompt from the Prompts tab')).toBeInTheDocument();
    expect(container.querySelector('textarea')).toBeNull();
  });

  it('renders textarea when promptContent is set', () => {
    const { getByText, container } = render(EssayWriter, {
      props: { promptContent: 'Write about climate change.' },
    });
    expect(getByText('Write about climate change.')).toBeInTheDocument();
    expect(container.querySelector('textarea')).not.toBeNull();
  });

  it('disables submit button when essayContent is empty', () => {
    const { getByText } = render(EssayWriter, {
      props: { promptContent: 'Prompt', essayContent: '' },
    });
    expect(getByText('Submit for Feedback').disabled).toBe(true);
  });

  it('enables submit button when essayContent has text', () => {
    const { getByText } = render(EssayWriter, {
      props: { promptContent: 'Prompt', essayContent: 'My essay text' },
    });
    expect(getByText('Submit for Feedback').disabled).toBe(false);
  });

  it('calls onSubmitEssay on submit click', async () => {
    const onSubmitEssay = vi.fn();
    const { getByText } = render(EssayWriter, {
      props: { promptContent: 'Prompt', essayContent: 'My essay', onSubmitEssay },
    });
    await fireEvent.click(getByText('Submit for Feedback'));
    expect(onSubmitEssay).toHaveBeenCalledTimes(1);
  });

  it('displays word count in text mode', () => {
    const { getByText } = render(EssayWriter, {
      props: { promptContent: 'Prompt', wordCount: 42 },
    });
    expect(getByText('Word count: 42')).toBeInTheDocument();
  });
});
