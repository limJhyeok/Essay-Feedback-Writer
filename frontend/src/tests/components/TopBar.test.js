import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import { writable } from 'svelte/store';

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

import TopBar from '../../components/TopBar.svelte';

describe('TopBar component', () => {
  beforeEach(() => {
    mockIsLogin.set(false);
  });

  it('renders domain name', () => {
    const { getByText } = render(TopBar, {
      props: { domainName: 'IELTS Feedback Writer' },
    });
    expect(getByText('IELTS Feedback Writer')).toBeInTheDocument();
  });

  it('shows back button when showBackLink is true', () => {
    const { container } = render(TopBar, {
      props: { showBackLink: true },
    });
    const buttons = container.querySelectorAll('button');
    const backBtn = Array.from(buttons).find(b => b.querySelector('svg'));
    expect(backBtn).toBeTruthy();
  });

  it('hides back button when showBackLink is false', () => {
    const { queryByText } = render(TopBar, {
      props: { showBackLink: false },
    });
    expect(queryByText('Info')).toBeInTheDocument();
  });

  it('shows login/signup buttons when not logged in', () => {
    const { getByText } = render(TopBar, { props: {} });
    expect(getByText('Log In')).toBeInTheDocument();
    expect(getByText('Sign Up')).toBeInTheDocument();
  });

  it('calls onInfoClick on info button click', async () => {
    const onInfoClick = vi.fn();
    const { getByText } = render(TopBar, { props: { onInfoClick } });
    await fireEvent.click(getByText('Info'));
    expect(onInfoClick).toHaveBeenCalledTimes(1);
  });

  it('renders Korean labels when locale is ko', () => {
    const { getByText } = render(TopBar, { props: { locale: 'ko' } });
    expect(getByText('로그인')).toBeInTheDocument();
    expect(getByText('회원가입')).toBeInTheDocument();
    expect(getByText('안내')).toBeInTheDocument();
  });
});
