import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import DeleteConfirmModal from '../../components/DeleteConfirmModal.svelte';

describe('DeleteConfirmModal component', () => {
  it('renders item name in confirmation message', () => {
    const { getByText } = render(DeleteConfirmModal, {
      props: { open: true, itemName: 'My API Key' },
    });
    expect(getByText('My API Key')).toBeInTheDocument();
    expect(getByText(/Are you sure you want to delete/)).toBeInTheDocument();
  });

  it('calls onConfirm when Yes Delete clicked', async () => {
    const onConfirm = vi.fn();
    const { getByText } = render(DeleteConfirmModal, {
      props: { open: true, itemName: 'Key', onConfirm },
    });
    await fireEvent.click(getByText('Yes, Delete'));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when Cancel clicked', async () => {
    const onCancel = vi.fn();
    const { getByText } = render(DeleteConfirmModal, {
      props: { open: true, itemName: 'Key', onCancel },
    });
    await fireEvent.click(getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
