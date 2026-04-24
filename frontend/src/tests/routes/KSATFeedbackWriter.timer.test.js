import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';

const { mockIsLogin, mockIsSignUpPage, mockAccessToken, mockUserEmail } = vi.hoisted(() => {
  const { writable } = require('svelte/store');
  return {
    mockIsLogin: writable(true),
    mockIsSignUpPage: writable(false),
    mockAccessToken: writable('test-token'),
    mockUserEmail: writable('test@test.com'),
  };
});

vi.mock('../../lib/store.js', () => ({
  isLogin: mockIsLogin,
  isSignUpPage: mockIsSignUpPage,
  accessToken: mockAccessToken,
  userEmail: mockUserEmail,
}));

vi.mock('svelte-spa-router', () => ({
  push: vi.fn(),
  link: vi.fn(() => () => {}),
}));

const { fastapiMock, apiCallMock } = vi.hoisted(() => ({
  fastapiMock: vi.fn(),
  apiCallMock: vi.fn(),
}));

vi.mock('../../lib/api.js', () => ({
  default: fastapiMock,
  apiCall: apiCallMock,
  fastapiUpload: vi.fn(),
}));

import KSATFeedbackWriter from '../../routes/KSATFeedbackWriter.svelte';

const EXAM_A = {
  id: 1,
  university: '중앙대학교',
  year: 2025,
  track: 'humanities',
  exam_type: 'mock',
  duration_minutes: 120,
};
const EXAM_B = {
  id: 2,
  university: '중앙대학교',
  year: 2024,
  track: 'humanities',
  exam_type: 'official',
  duration_minutes: 120,
};
const EXAM_NO_TIMER = {
  id: 3,
  university: '중앙대학교',
  year: 2026,
  track: 'humanities',
  exam_type: 'mock',
  duration_minutes: null,
};
const EXAM_ZERO = {
  id: 4,
  university: '중앙대학교',
  year: 2027,
  track: 'humanities',
  exam_type: 'mock',
  duration_minutes: 0,
};

const QUESTIONS = [
  { question_number: 1, prompt_id: 101, prompt_content: '문제1', max_points: 40, rubric_name: 'r1', content: '<p>p1</p>', char_min: 0, char_max: 0 },
];

function installFastapiMock(examList) {
  fastapiMock.mockImplementation((op, url, params, onSuccess) => {
    if (url === '/api/v1/user/auth') return onSuccess && onSuccess();
    if (url === '/api/v1/shared/api_keys') return onSuccess && onSuccess([{ id: 1 }]);
    if (url === '/api/v1/shared/providers')
      return onSuccess && onSuccess([{ id: 1, name: 'OpenAI' }]);
    if (url.startsWith('/api/v1/shared/api_models/'))
      return onSuccess && onSuccess([{ id: 1, api_model_name: 'gpt-4', alias: 'GPT-4', bot: { id: 1 } }]);
    if (url === '/api/v1/ksat/exams') return onSuccess && onSuccess(examList);
    const examDetailMatch = url.match(/^\/api\/v1\/ksat\/exams\/(\d+)$/);
    if (examDetailMatch) {
      const id = Number(examDetailMatch[1]);
      const exam = examList.find((e) => e.id === id) || examList[0];
      return onSuccess && onSuccess({ ...exam, questions: QUESTIONS });
    }
    if (url === '/api/v1/ksat/essays') return onSuccess && onSuccess([]);
    if (url === '/api/v1/ksat/feedbacks') return onSuccess && onSuccess([]);
    if (url === '/api/v1/ksat/criteria') return onSuccess && onSuccess([]);
    if (url === '/api/v1/ksat/example') return onSuccess && onSuccess({ content: '' });
  });
}

async function selectExamByTitle(result, titleFragment) {
  await waitFor(() => {
    expect(result.getByText('중앙대학교')).toBeInTheDocument();
  });
  await fireEvent.click(result.getByText('중앙대학교'));

  await waitFor(() => {
    expect(result.container.querySelector('.exam-list-item')).not.toBeNull();
  });
  const items = Array.from(result.container.querySelectorAll('.exam-list-item'));
  const target = items.find((el) => el.textContent.includes(titleFragment));
  if (!target) throw new Error(`No exam card matching "${titleFragment}"`);
  await fireEvent.click(target);

  await waitFor(() => {
    expect(result.container.querySelector('.essay-textarea')).not.toBeNull();
  });
}

const BASE_TIME = new Date('2026-04-25T09:00:00Z');

beforeEach(() => {
  vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval', 'Date'] });
  vi.setSystemTime(BASE_TIME);
  localStorage.clear();
  mockUserEmail.set('test@test.com');
  fastapiMock.mockReset();
  apiCallMock.mockReset();
  installFastapiMock([EXAM_A, EXAM_B, EXAM_NO_TIMER, EXAM_ZERO]);
});

afterEach(() => {
  vi.useRealTimers();
});

// ───────────────────────────────────────────────────────────
// A. Storage key
// ───────────────────────────────────────────────────────────
describe('Timer — storage key', () => {
  it('A1: uses ksat_timer_{email}_{examId} when userEmail is populated', async () => {
    mockUserEmail.set('alice@example.com');
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    expect(localStorage.getItem('ksat_timer_alice@example.com_1')).not.toBeNull();
  });

  it('A2: falls back to ksat_timer_anon_{examId} when userEmail is empty', async () => {
    mockUserEmail.set('');
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    expect(localStorage.getItem('ksat_timer_anon_1')).not.toBeNull();
  });
});

// ───────────────────────────────────────────────────────────
// B. Persistence
// ───────────────────────────────────────────────────────────
describe('Timer — persistence', () => {
  it('B1: writes BASE_TIME ms to localStorage on first selectExam', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    const stored = localStorage.getItem('ksat_timer_test@test.com_1');
    expect(Number(stored)).toBe(BASE_TIME.getTime());
  });

  it('B2: resumes from existing localStorage value without overwriting', async () => {
    const pastStart = BASE_TIME.getTime() - 60 * 60 * 1000; // 1h ago
    localStorage.setItem('ksat_timer_test@test.com_1', String(pastStart));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    expect(Number(localStorage.getItem('ksat_timer_test@test.com_1'))).toBe(pastStart);

    // 120 - 60 = 60 min remaining → MM:SS format not used, HH:MM:SS with 01:00:00
    await waitFor(() => {
      const timer = result.container.querySelector('.timer');
      expect(timer.textContent).toContain('01:00:00');
    });
  });

  it('B3: tab switching keeps localStorage value and interval count stable', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');
    const storedInitial = localStorage.getItem('ksat_timer_test@test.com_1');
    expect(vi.getTimerCount()).toBe(1);

    await fireEvent.click(result.getByRole('button', { name: /기출문제/ }));
    await fireEvent.click(result.getByRole('button', { name: /답안 작성/ }));

    expect(localStorage.getItem('ksat_timer_test@test.com_1')).toBe(storedInitial);
    expect(vi.getTimerCount()).toBe(1);
  });
});

// ───────────────────────────────────────────────────────────
// C. Display formatting
// ───────────────────────────────────────────────────────────
describe('Timer — display formatting', () => {
  it('C1: renders HH:MM:SS when more than 1 hour remaining', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    await waitFor(() => {
      const value = result.container.querySelector('.timer-value');
      // 120 min = 02:00:00 at start
      expect(value.textContent.trim()).toBe('02:00:00');
    });
  });

  it('C2: renders MM:SS when less than 1 hour remaining', async () => {
    // 70 min already elapsed → 50 min left
    const past = BASE_TIME.getTime() - 70 * 60 * 1000;
    localStorage.setItem('ksat_timer_test@test.com_1', String(past));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    await waitFor(() => {
      const value = result.container.querySelector('.timer-value');
      expect(value.textContent.trim()).toBe('50:00');
    });
  });

  it('C3: shows "시간 초과" and hides numeric value when overtime', async () => {
    const past = BASE_TIME.getTime() - 125 * 60 * 1000; // 5 min overtime
    localStorage.setItem('ksat_timer_test@test.com_1', String(past));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    await waitFor(() => {
      const timer = result.container.querySelector('.timer');
      expect(timer.textContent).toContain('시간 초과');
      expect(timer.querySelector('.timer-value')).toBeNull();
    });
  });
});

// ───────────────────────────────────────────────────────────
// D. Reactive warning / over states
// ───────────────────────────────────────────────────────────
describe('Timer — reactive states', () => {
  it('D1: no warning/over class when plenty of time remains', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    const timer = result.container.querySelector('.timer');
    expect(timer.classList.contains('warning')).toBe(false);
    expect(timer.classList.contains('over')).toBe(false);
  });

  it('D2: applies warning class when crossing the 30-min threshold', async () => {
    // Start with 31 min remaining → not warning yet
    const past = BASE_TIME.getTime() - (120 - 31) * 60 * 1000;
    localStorage.setItem('ksat_timer_test@test.com_1', String(past));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    let timer = result.container.querySelector('.timer');
    expect(timer.classList.contains('warning')).toBe(false);

    // Advance 90s → now ~29:30 left → warning
    vi.advanceTimersByTime(90 * 1000);

    await waitFor(() => {
      timer = result.container.querySelector('.timer');
      expect(timer.classList.contains('warning')).toBe(true);
      expect(timer.classList.contains('over')).toBe(false);
    });
  });

  it('D3: applies over class and drops warning when crossing zero', async () => {
    // 29 min remaining → warning already active
    const past = BASE_TIME.getTime() - (120 - 29) * 60 * 1000;
    localStorage.setItem('ksat_timer_test@test.com_1', String(past));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    await waitFor(() => {
      const timer = result.container.querySelector('.timer');
      expect(timer.classList.contains('warning')).toBe(true);
    });

    vi.advanceTimersByTime(30 * 60 * 1000); // push past zero

    await waitFor(() => {
      const timer = result.container.querySelector('.timer');
      expect(timer.classList.contains('over')).toBe(true);
      expect(timer.classList.contains('warning')).toBe(false);
    });
  });
});

// ───────────────────────────────────────────────────────────
// E. Edge cases
// ───────────────────────────────────────────────────────────
describe('Timer — edge cases', () => {
  it('E1: no timer UI when exam has null duration_minutes', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2026학년도');

    expect(result.container.querySelector('.timer')).toBeNull();
    expect(localStorage.getItem('ksat_timer_test@test.com_3')).toBeNull();
  });

  it('E2: no timer started when duration_minutes is 0', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2027학년도');

    expect(result.container.querySelector('.timer')).toBeNull();
    expect(localStorage.getItem('ksat_timer_test@test.com_4')).toBeNull();
    expect(vi.getTimerCount()).toBe(0);
  });

  it('E3: ignores corrupted non-numeric localStorage and starts fresh', async () => {
    localStorage.setItem('ksat_timer_test@test.com_1', 'notanumber');
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    expect(Number(localStorage.getItem('ksat_timer_test@test.com_1'))).toBe(BASE_TIME.getTime());
  });
});

// ───────────────────────────────────────────────────────────
// F. Lifecycle / leak prevention
// ───────────────────────────────────────────────────────────
describe('Timer — lifecycle', () => {
  it('F1: onDestroy clears the interval on unmount', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');
    expect(vi.getTimerCount()).toBe(1);

    result.unmount();

    expect(vi.getTimerCount()).toBe(0);
  });

  it('F2: switching exams does not accumulate intervals', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');
    expect(vi.getTimerCount()).toBe(1);

    await fireEvent.click(result.getByRole('button', { name: /기출문제/ }));

    await waitFor(() => {
      expect(result.container.querySelector('.exam-list-item')).not.toBeNull();
    });
    const items = Array.from(result.container.querySelectorAll('.exam-list-item'));
    const target = items.find((el) => el.textContent.includes('2024학년도'));
    await fireEvent.click(target);

    await waitFor(() => {
      expect(result.container.querySelector('.essay-textarea')).not.toBeNull();
    });

    expect(vi.getTimerCount()).toBe(1);
    // Separate localStorage namespaces
    expect(localStorage.getItem('ksat_timer_test@test.com_1')).not.toBeNull();
    expect(localStorage.getItem('ksat_timer_test@test.com_2')).not.toBeNull();
  });

  it('F3: repeated reset does not accumulate intervals', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    const resetBtn = result.container.querySelector('.timer-reset');
    await fireEvent.click(resetBtn);
    await fireEvent.click(resetBtn);
    await fireEvent.click(resetBtn);

    expect(vi.getTimerCount()).toBe(1);
  });

  it('F4: advancing time after unmount does not mutate localStorage', async () => {
    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');
    const before = localStorage.getItem('ksat_timer_test@test.com_1');

    result.unmount();
    vi.advanceTimersByTime(60 * 1000);

    expect(localStorage.getItem('ksat_timer_test@test.com_1')).toBe(before);
    expect(vi.getTimerCount()).toBe(0);
  });
});

// ───────────────────────────────────────────────────────────
// G. Reset behaviour
// ───────────────────────────────────────────────────────────
describe('Timer — reset', () => {
  it('G1: reset rewrites localStorage with current time', async () => {
    const pastStart = BASE_TIME.getTime() - 30 * 60 * 1000;
    localStorage.setItem('ksat_timer_test@test.com_1', String(pastStart));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');
    expect(Number(localStorage.getItem('ksat_timer_test@test.com_1'))).toBe(pastStart);

    const resetBtn = result.container.querySelector('.timer-reset');
    await fireEvent.click(resetBtn);

    expect(Number(localStorage.getItem('ksat_timer_test@test.com_1'))).toBe(BASE_TIME.getTime());
  });

  it('G2: reset resets displayed time to the full duration', async () => {
    const pastStart = BASE_TIME.getTime() - 100 * 60 * 1000; // 20 min left
    localStorage.setItem('ksat_timer_test@test.com_1', String(pastStart));

    const result = render(KSATFeedbackWriter);
    await selectExamByTitle(result, '2025학년도');

    await waitFor(() => {
      expect(result.container.querySelector('.timer').classList.contains('warning')).toBe(true);
    });

    const resetBtn = result.container.querySelector('.timer-reset');
    await fireEvent.click(resetBtn);

    await waitFor(() => {
      const timer = result.container.querySelector('.timer');
      expect(timer.classList.contains('warning')).toBe(false);
      expect(timer.querySelector('.timer-value').textContent.trim()).toBe('02:00:00');
    });
  });
});
