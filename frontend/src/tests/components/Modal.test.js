import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import Modal from '../../components/Modal.svelte';

describe('Modal component', () => {
  it('renders nothing when open is false', () => {
    const { container } = render(Modal, { props: { open: false, title: 'Test' } });
    expect(container.querySelector('.modal')).toBeNull();
  });

  it('renders modal with title when open is true', () => {
    const { getByText, container } = render(Modal, {
      props: { open: true, title: 'My Title' },
    });
    expect(container.querySelector('.modal')).not.toBeNull();
    expect(getByText('My Title')).toBeInTheDocument();
  });

  it('applies size class based on size prop', () => {
    const { container: smContainer } = render(Modal, {
      props: { open: true, title: 'Small', size: 'sm' },
    });
    expect(smContainer.querySelector('.modal-sm')).not.toBeNull();

    const { container: lgContainer } = render(Modal, {
      props: { open: true, title: 'Large', size: 'lg' },
    });
    expect(lgContainer.querySelector('.modal-lg')).not.toBeNull();

    // md size should not add modal-sm or modal-lg
    const { container: mdContainer } = render(Modal, {
      props: { open: true, title: 'Medium', size: 'md' },
    });
    expect(mdContainer.querySelector('.modal-sm')).toBeNull();
    expect(mdContainer.querySelector('.modal-lg')).toBeNull();
  });

  it('calls onClose when close button clicked', async () => {
    const onClose = vi.fn();
    const { container } = render(Modal, {
      props: { open: true, title: 'Close Test', onClose },
    });
    await fireEvent.click(container.querySelector('.btn-close'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
