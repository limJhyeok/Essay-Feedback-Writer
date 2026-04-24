import { describe, it, expect, vi, beforeEach } from 'vitest';
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

const EXAM ={
  id: 1,
  university: '중앙대학교',
  year: 2025,
  track: 'humanities',
  exam_type: 'mock',
};

const QUESTIONS = [
  { question_number: 1, prompt_id: 101, prompt_content: '문제1 본문', max_points: 40, rubric_name: 'r1', content: '<p>제시문1</p>', char_min: 0, char_max: 0 },
  { question_number: 2, prompt_id: 102, prompt_content: '문제2 본문', max_points: 30, rubric_name: 'r1', content: '<p>제시문2</p>', char_min: 0, char_max: 0 },
  { question_number: 3, prompt_id: 103, prompt_content: '문제3 본문', max_points: 30, rubric_name: 'r1', content: '<p>제시문3</p>', char_min: 0, char_max: 0 },
];

function installFastapiMock() {
  fastapiMock.mockImplementation((op, url, params, onSuccess, onFailure) => {
    if (url === '/api/v1/user/auth') {
      onSuccess && onSuccess();
    } else if (url === '/api/v1/shared/api_keys') {
      onSuccess && onSuccess([{ id: 1 }]);
    } else if (url === '/api/v1/shared/providers') {
      onSuccess && onSuccess([{ id: 1, name: 'OpenAI' }]);
    } else if (url.startsWith('/api/v1/shared/api_models/')) {
      onSuccess && onSuccess([{ id: 1, api_model_name: 'gpt-4', alias: 'GPT-4', bot: { id: 1 } }]);
    } else if (url === '/api/v1/ksat/exams') {
      onSuccess && onSuccess([EXAM]);
    } else if (/^\/api\/v1\/ksat\/exams\/\d+$/.test(url)) {
      onSuccess && onSuccess({ questions: QUESTIONS });
    } else if (url === '/api/v1/ksat/essays') {
      onSuccess && onSuccess([]);
    } else if (url === '/api/v1/ksat/feedbacks') {
      onSuccess && onSuccess([]);
    } else if (url === '/api/v1/ksat/criteria') {
      onSuccess && onSuccess([]);
    } else if (url === '/api/v1/ksat/example') {
      onSuccess && onSuccess({ content: '' });
    }
  });
}

async function navigateToWriteTab(result) {
  // Select university
  await waitFor(() => {
    expect(result.getByText('중앙대학교')).toBeInTheDocument();
  });
  await fireEvent.click(result.getByText('중앙대학교'));

  // Select exam
  await waitFor(() => {
    expect(result.container.querySelector('.exam-list-item')).not.toBeNull();
  });
  await fireEvent.click(result.container.querySelector('.exam-list-item'));

  // Wait for write tab to render with 3 question tabs
  await waitFor(() => {
    const tabs = result.container.querySelectorAll('.passage-question-tab');
    expect(tabs.length).toBe(3);
  });
}

describe('KSATFeedbackWriter - 문제 tab 활성화', () => {
  beforeEach(() => {
    fastapiMock.mockReset();
    apiCallMock.mockReset();
    installFastapiMock();
  });

  it('fills tab 1 with Check icon, leaves tabs 2/3 with Circle icon and shows "작성 완료 1/3"', async () => {
    const result = render(KSATFeedbackWriter);
    await navigateToWriteTab(result);

    // 문제 1 text area에 "test" 작성 (active tab defaults to question 1)
    const textarea = result.container.querySelector('.essay-textarea');
    expect(textarea).not.toBeNull();
    await fireEvent.input(textarea, { target: { value: 'test' } });

    // Wait for reactivity to flush
    await waitFor(() => {
      const progressEl = result.container.querySelector('.progress-text');
      expect(progressEl.textContent).toMatch(/작성 완료 1\s*\/\s*3/);
    });

    const tabs = result.container.querySelectorAll('.passage-question-tab');

    // 문제 1 tab: filled class + Check icon (no <circle> element inside svg)
    expect(tabs[0].classList.contains('filled')).toBe(true);
    const icon1 = tabs[0].querySelector('.tab-status-icon svg');
    expect(icon1).not.toBeNull();
    expect(icon1.querySelector('circle')).toBeNull();

    // 문제 2, 3 tab: no filled class + Circle icon (contains <circle> element)
    expect(tabs[1].classList.contains('filled')).toBe(false);
    expect(tabs[2].classList.contains('filled')).toBe(false);
    const icon2 = tabs[1].querySelector('.tab-status-icon svg');
    const icon3 = tabs[2].querySelector('.tab-status-icon svg');
    expect(icon2.querySelector('circle')).not.toBeNull();
    expect(icon3.querySelector('circle')).not.toBeNull();
  });
});

describe('KSATFeedbackWriter - 채점 받기 button', () => {
  beforeEach(() => {
    fastapiMock.mockReset();
    apiCallMock.mockReset();
    installFastapiMock();
    apiCallMock.mockResolvedValue({ id: 999, submitted_at: '2025-01-01', prompt_id: 101 });
  });

  async function fillQuestion(result, tabIndex, text) {
    const tabs = result.container.querySelectorAll('.passage-question-tab');
    await fireEvent.click(tabs[tabIndex]);
    await waitFor(() => {
      const textarea = result.container.querySelector('.essay-textarea');
      const header = result.container.querySelector('.question-write-label');
      expect(header.textContent).toContain(`문제 ${tabIndex + 1}`);
      expect(textarea).not.toBeNull();
    });
    const textarea = result.container.querySelector('.essay-textarea');
    await fireEvent.input(textarea, { target: { value: text } });
  }

  it('shows warning modal when only some questions are filled', async () => {
    const result = render(KSATFeedbackWriter);
    await navigateToWriteTab(result);

    await fillQuestion(result, 0, 'test');

    await fireEvent.click(result.getByText('채점 받기'));

    await waitFor(() => {
      expect(result.getByText('미작성 답안이 있습니다')).toBeInTheDocument();
    });
    // Unfilled labels should include 문제 2, 문제 3
    const unfilledBox = result.container.querySelector('.submit-confirm-unfilled');
    expect(unfilledBox.textContent).toContain('문제 2');
    expect(unfilledBox.textContent).toContain('문제 3');
  });

  it('does NOT show the modal when all questions are filled', async () => {
    const result = render(KSATFeedbackWriter);
    await navigateToWriteTab(result);

    await fillQuestion(result, 0, 'answer-1');
    await fillQuestion(result, 1, 'answer-2');
    await fillQuestion(result, 2, 'answer-3');

    await fireEvent.click(result.getByText('채점 받기'));

    // Modal should not appear
    expect(result.queryByText('미작성 답안이 있습니다')).toBeNull();

    // apiCall should be invoked for essay submission
    await waitFor(() => {
      expect(apiCallMock).toHaveBeenCalled();
    });
  });

  it('does NOT call apiCall when 취소 is clicked on the modal', async () => {
    const result = render(KSATFeedbackWriter);
    await navigateToWriteTab(result);

    await fillQuestion(result, 0, 'test');

    await fireEvent.click(result.getByText('채점 받기'));

    await waitFor(() => {
      expect(result.getByText('미작성 답안이 있습니다')).toBeInTheDocument();
    });

    await fireEvent.click(result.getByText('취소'));

    await waitFor(() => {
      expect(result.queryByText('미작성 답안이 있습니다')).toBeNull();
    });
    expect(apiCallMock).not.toHaveBeenCalled();
  });

  it('calls apiCall when 그래도 제출 is clicked on the modal', async () => {
    const result = render(KSATFeedbackWriter);
    await navigateToWriteTab(result);

    await fillQuestion(result, 0, 'test');

    await fireEvent.click(result.getByText('채점 받기'));

    await waitFor(() => {
      expect(result.getByText('미작성 답안이 있습니다')).toBeInTheDocument();
    });

    await fireEvent.click(result.getByText('그래도 제출'));

    await waitFor(() => {
      expect(apiCallMock).toHaveBeenCalled();
    });
    // Only filled question (문제 1) should be submitted as an essay
    expect(apiCallMock).toHaveBeenCalledWith(
      'post',
      '/api/v1/ksat/essays',
      expect.objectContaining({ prompt_id: 101, content: 'test' }),
    );
    // Unfilled questions (prompt_id 102, 103) should NOT be submitted
    const submittedPromptIds = apiCallMock.mock.calls
      .filter(([op, url]) => url === '/api/v1/ksat/essays')
      .map(([, , params]) => params.prompt_id);
    expect(submittedPromptIds).not.toContain(102);
    expect(submittedPromptIds).not.toContain(103);
  });
});
