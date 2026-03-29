import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import PromptList from '../../components/PromptList.svelte';

const prompts = [
  { content: 'Discuss the impact of technology on education.' },
  { content: 'Some people believe that universities should focus on skills.' },
];

describe('PromptList component', () => {
  it('renders all prompt items', () => {
    const { getByText } = render(PromptList, {
      props: { prompts, activePromptContent: '' },
    });
    expect(getByText('Discuss the impact of technology on education.')).toBeInTheDocument();
    expect(getByText('Some people believe that universities should focus on skills.')).toBeInTheDocument();
  });

  it('applies active class to matching prompt', () => {
    const { container } = render(PromptList, {
      props: { prompts, activePromptContent: prompts[0].content },
    });
    const activeItems = container.querySelectorAll('.prompt-item.active');
    expect(activeItems.length).toBe(1);
    expect(activeItems[0].textContent).toContain('Discuss the impact');
  });

  it('calls onSelectPrompt with prompt object on click', async () => {
    const onSelectPrompt = vi.fn();
    const { getByText } = render(PromptList, {
      props: { prompts, activePromptContent: '', onSelectPrompt },
    });
    await fireEvent.click(getByText('Discuss the impact of technology on education.'));
    expect(onSelectPrompt).toHaveBeenCalledWith(prompts[0]);
  });

  it('keyboard Enter triggers onSelectPrompt', async () => {
    const onSelectPrompt = vi.fn();
    const { getByText } = render(PromptList, {
      props: { prompts, activePromptContent: '', onSelectPrompt },
    });
    await fireEvent.keyDown(getByText('Discuss the impact of technology on education.'), { key: 'Enter' });
    expect(onSelectPrompt).toHaveBeenCalledWith(prompts[0]);
  });
});
