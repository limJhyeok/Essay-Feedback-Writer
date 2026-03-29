import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';

const { mockPush } = vi.hoisted(() => ({
  mockPush: vi.fn(),
}));

vi.mock('svelte-spa-router', () => ({
  push: mockPush,
  link: vi.fn(),
}));

import DomainSelector from '../../routes/DomainSelector.svelte';

describe('DomainSelector route', () => {
  it('renders all four domain cards', () => {
    const { getByText } = render(DomainSelector);
    expect(getByText('IELTS Writing')).toBeInTheDocument();
    expect(getByText('대학별 논술')).toBeInTheDocument();
    expect(getByText('Math Problem Solving')).toBeInTheDocument();
    expect(getByText('Science Essays')).toBeInTheDocument();
  });

  it('shows COMING SOON badge on disabled domains', () => {
    const { getAllByText } = render(DomainSelector);
    const badges = getAllByText('COMING SOON');
    expect(badges.length).toBe(2);
  });

  it('enabled domains have clickable class', () => {
    const { container } = render(DomainSelector);
    const clickableCards = container.querySelectorAll('.domain-card.clickable');
    const disabledCards = container.querySelectorAll('.domain-card.disabled');
    expect(clickableCards.length).toBe(2);
    expect(disabledCards.length).toBe(2);
  });

  it('clicking enabled domain navigates to route', async () => {
    mockPush.mockClear();
    const { getByText } = render(DomainSelector);
    await fireEvent.click(getByText('IELTS Writing'));
    expect(mockPush).toHaveBeenCalledWith('/ielts');
  });

  it('clicking disabled domain does not navigate', async () => {
    mockPush.mockClear();
    const { getByText } = render(DomainSelector);
    await fireEvent.click(getByText('Math Problem Solving'));
    expect(mockPush).not.toHaveBeenCalled();
  });
});
