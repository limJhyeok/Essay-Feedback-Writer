import { describe, it, expect } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import DropdownWrapper from './_DropdownWrapper.svelte';

describe('Dropdown component', () => {
  it('menu hidden initially', () => {
    const { queryByTestId } = render(DropdownWrapper);
    expect(queryByTestId('menu-item')).toBeNull();
  });

  it('menu visible after trigger click', async () => {
    const { getByTestId, queryByTestId } = render(DropdownWrapper);
    await fireEvent.click(getByTestId('trigger'));
    expect(queryByTestId('menu-item')).not.toBeNull();
  });

  it('menu closes after close function called', async () => {
    const { getByTestId, queryByTestId } = render(DropdownWrapper);
    await fireEvent.click(getByTestId('trigger'));
    expect(queryByTestId('menu-item')).not.toBeNull();
    await fireEvent.click(getByTestId('menu-item'));
    expect(queryByTestId('menu-item')).toBeNull();
  });
});
