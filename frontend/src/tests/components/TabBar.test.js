import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TabBar from '../../components/TabBar.svelte';

const tabs = [
  { id: 'tab1', label: 'First' },
  { id: 'tab2', label: 'Second' },
  { id: 'tab3', label: 'Third', disabled: true },
];

describe('TabBar component', () => {
  it('renders all tab labels', () => {
    const { getByText } = render(TabBar, { props: { tabs, activeTab: 'tab1' } });
    expect(getByText('First')).toBeInTheDocument();
    expect(getByText('Second')).toBeInTheDocument();
    expect(getByText('Third')).toBeInTheDocument();
  });

  it('marks the active tab with active class', () => {
    const { getByText } = render(TabBar, { props: { tabs, activeTab: 'tab2' } });
    expect(getByText('Second').classList.contains('active')).toBe(true);
    expect(getByText('First').classList.contains('active')).toBe(false);
  });

  it('calls onTabChange with tab id on click', async () => {
    const onTabChange = vi.fn();
    const { getByText } = render(TabBar, {
      props: { tabs, activeTab: 'tab1', onTabChange },
    });
    await fireEvent.click(getByText('First'));
    expect(onTabChange).toHaveBeenCalledWith('tab1');
  });

  it('does not call onTabChange on disabled tab click', async () => {
    const onTabChange = vi.fn();
    const { getByText } = render(TabBar, {
      props: { tabs, activeTab: 'tab1', onTabChange },
    });
    await fireEvent.click(getByText('Third'));
    expect(onTabChange).not.toHaveBeenCalled();
  });
});
