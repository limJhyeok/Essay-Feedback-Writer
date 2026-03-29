import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/svelte';

const { mockIsLogin, mockIsSignUpPage, mockAccessToken, mockUserEmail } = vi.hoisted(() => {
  const { writable } = require('svelte/store');
  return {
    mockIsLogin: writable(false),
    mockIsSignUpPage: writable(false),
    mockAccessToken: writable(''),
    mockUserEmail: writable(''),
  };
});

vi.mock('../../lib/store', () => ({
  isLogin: mockIsLogin,
  isSignUpPage: mockIsSignUpPage,
  accessToken: mockAccessToken,
  userEmail: mockUserEmail,
}));

vi.mock('svelte-spa-router', () => ({
  push: vi.fn(),
  link: vi.fn(() => () => {}),
}));

vi.mock('../../lib/api', () => ({
  default: vi.fn(),
}));

import Auth from '../../routes/Auth.svelte';

describe('Auth route', () => {
  it('renders login heading by default', () => {
    const { container } = render(Auth);
    const heading = container.querySelector('h1');
    expect(heading).not.toBeNull();
    expect(heading.textContent).toBe('Log in');
  });

  it('renders email and password input fields', () => {
    const { container } = render(Auth);
    const emailInput = container.querySelector('#email');
    const passwordInput = container.querySelector('#password');
    expect(emailInput).not.toBeNull();
    expect(emailInput.type).toBe('email');
    expect(passwordInput).not.toBeNull();
    expect(passwordInput.type).toBe('password');
  });

  it('renders toggle link to switch to signup', () => {
    const { getByText } = render(Auth);
    expect(getByText("Don't have an account? Sign up")).toBeInTheDocument();
  });

  it('renders forgot password link', () => {
    const { getByText } = render(Auth);
    expect(getByText('Forgot your password?')).toBeInTheDocument();
  });
});
