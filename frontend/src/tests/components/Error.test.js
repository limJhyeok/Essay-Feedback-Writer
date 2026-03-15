import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import Error from '../../components/Error.svelte';

describe('Error component', () => {
  it('renders nothing when error.detail is an empty array', () => {
    const { container } = render(Error, { props: { error: { detail: [] } } });
    expect(container.querySelector('.alert')).toBeNull();
  });

  it('renders a string error message', () => {
    const { getByText, container } = render(Error, {
      props: { error: { detail: 'Something went wrong' } },
    });
    expect(getByText('Something went wrong')).toBeInTheDocument();
    expect(container.querySelector('.alert-danger')).toBeInTheDocument();
  });

  it('renders validation error objects with loc and msg', () => {
    const errors = [
      { loc: ['body', 'email'], msg: 'field required', type: 'missing' },
      { loc: ['body', 'password'], msg: 'ensure this value has at least 8 characters', type: 'value_error' },
    ];
    const { getByText, container } = render(Error, {
      props: { error: { detail: errors } },
    });
    expect(container.querySelector('.alert-danger')).toBeInTheDocument();
    expect(getByText(/email/)).toBeInTheDocument();
    expect(getByText(/field required/)).toBeInTheDocument();
    expect(getByText(/password/)).toBeInTheDocument();
  });

  it('uses Bootstrap alert-danger styling', () => {
    const { container } = render(Error, {
      props: { error: { detail: 'Error' } },
    });
    const alertEl = container.querySelector('.alert');
    expect(alertEl).toHaveClass('alert-danger');
  });
});
