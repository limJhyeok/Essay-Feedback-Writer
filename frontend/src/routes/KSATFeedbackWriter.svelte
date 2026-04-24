<script>
  import { isLogin, accessToken, userEmail } from '../lib/store.js';
  import { get } from 'svelte/store';
  import fastapi, { apiCall } from '../lib/api.js';
  import { onMount, onDestroy, tick } from 'svelte';
  import { push } from 'svelte-spa-router';
  import './home.css';
  import { BookOpen, FileText, BarChart, PenLine, Search, Check, Circle, AlertTriangle, Clock, RotateCcw } from 'lucide-svelte';

  import Error from '../components/Error.svelte';
  import TopBar from '../components/TopBar.svelte';
  import InfoDeskModal from '../components/InfoDeskModal.svelte';
  import ManageKeyModal from '../components/ManageKeyModal.svelte';
  import Modal from '../components/Modal.svelte';
  import ModelSelector from '../components/ModelSelector.svelte';
  import ScoreCard from '../components/ScoreCard.svelte';
  import { safeHtml } from '../lib/sanitize.js';

  // Core state
  let mainActiveTab = 'prompts';
  let selectedUniversity = null;
  let selectedExam = null;

  let showInfoDeskModalOpen = false;
  let showManageKeyModalOpen = false;

  // Per-question state (keyed by question_number)
  let essayContents = {};
  let essaysByQuestion = {};
  let feedbacksByQuestion = {};
  let activeEssayIdxByQ = {};
  let activeFeedbackIdxByQ = {};
  let exampleAnswers = {};

  let exams = [];
  let questions = [];
  let activePassageQNum = null;
  $: activePassageContent =
    questions.find(q => q.question_number === activePassageQNum)?.content || '';

  let AIModelProviders = [];
  let selectedAIModelProvider = null;
  let feedbackModels = [];
  let selectedFeedbackModel = null;

  let error = { detail: [] };
  let universitySearch = '';
  let isGeneratingFeedback = false;
  let criteriaLabelsMap = {};
  let hasApiKeys = null;

  // Submit confirmation modal state
  let showSubmitConfirm = false;
  let unfilledLabels = '';
  let submitConfirmResolver = null;

  // Timer state
  const WARNING_THRESHOLD_SECONDS = 30 * 60;
  let timerStartedAt = null; // ms epoch
  let timerElapsedSeconds = 0;
  let timerIntervalId = null;

  function timerStorageKey(examId) {
    const email = get(userEmail) || 'anon';
    return `ksat_timer_${email}_${examId}`;
  }

  function startTimerForExam(exam) {
    if (!exam || !exam.duration_minutes) return;
    const key = timerStorageKey(exam.id);
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = parseInt(stored, 10);
      if (!Number.isNaN(parsed)) {
        timerStartedAt = parsed;
      }
    }
    if (!timerStartedAt) {
      timerStartedAt = Date.now();
      localStorage.setItem(key, String(timerStartedAt));
    }
    tickTimer();
    if (timerIntervalId) clearInterval(timerIntervalId);
    timerIntervalId = setInterval(tickTimer, 1000);
  }

  function tickTimer() {
    if (!timerStartedAt) return;
    timerElapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  }

  function stopTimer() {
    if (timerIntervalId) {
      clearInterval(timerIntervalId);
      timerIntervalId = null;
    }
  }

  function resetTimer() {
    if (!selectedExam) return;
    const key = timerStorageKey(selectedExam.id);
    timerStartedAt = Date.now();
    localStorage.setItem(key, String(timerStartedAt));
    timerElapsedSeconds = 0;
    if (timerIntervalId) clearInterval(timerIntervalId);
    timerIntervalId = setInterval(tickTimer, 1000);
  }

  function clearTimerState() {
    stopTimer();
    timerStartedAt = null;
    timerElapsedSeconds = 0;
  }

  $: timerDurationSeconds =
    selectedExam && selectedExam.duration_minutes
      ? selectedExam.duration_minutes * 60
      : 0;
  $: timerRemainingSeconds = timerDurationSeconds
    ? timerDurationSeconds - timerElapsedSeconds
    : 0;
  $: timerIsOver = timerDurationSeconds > 0 && timerRemainingSeconds <= 0;
  $: timerIsWarning =
    timerDurationSeconds > 0 &&
    !timerIsOver &&
    timerRemainingSeconds <= WARNING_THRESHOLD_SECONDS;

  function formatTimerDisplay(seconds) {
    if (seconds <= 0) return '00:00';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    const pad = (n) => String(n).padStart(2, '0');
    return h > 0 ? `${pad(h)}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
  }

  onDestroy(() => {
    stopTimer();
  });

  function askSubmitConfirm(label) {
    unfilledLabels = label;
    showSubmitConfirm = true;
    return new Promise((resolve) => {
      submitConfirmResolver = resolve;
    });
  }

  function resolveSubmitConfirm(proceed) {
    showSubmitConfirm = false;
    if (submitConfirmResolver) {
      submitConfirmResolver(proceed);
      submitConfirmResolver = null;
    }
  }

  function checkApiKeys() {
    fastapi('get', '/api/v1/shared/api_keys', {},
      (json) => { hasApiKeys = json.length > 0; },
      () => { hasApiKeys = null; }
    );
  }

  // Auth check
  function checkAuth() {
    fastapi('get', '/api/v1/user/auth', {}, () => {}, (json_error) => { error = json_error; });
  }
  checkAuth();
  checkApiKeys();

  $: if ($isLogin === false) {
    handleUnauthorized();
  }

  async function handleUnauthorized() {
    alert('로그인이 필요합니다.');
    await tick();
    push('/authorize');
  }

  // Providers / models
  function read_bots() {
    if (!selectedAIModelProvider) return;
    fastapi('get', `/api/v1/shared/api_models/${selectedAIModelProvider.name}`, {},
      (json) => {
        feedbackModels = json;
        if (feedbackModels.length > 0) selectedFeedbackModel = feedbackModels[0];
      },
      (json_error) => { error = json_error; }
    );
  }
  $: selectedAIModelProvider && read_bots();

  function read_providers() {
    fastapi('get', '/api/v1/shared/providers', {},
      (json) => {
        AIModelProviders = json;
        if (AIModelProviders.length > 0) selectedAIModelProvider = AIModelProviders[0];
      },
      (json_error) => { error = json_error; }
    );
  }
  read_providers();

  // Load exams
  function loadExams() {
    fastapi('get', '/api/v1/ksat/exams', {},
      (json) => { exams = json; },
      (json_error) => { error = json_error; }
    );
  }
  loadExams();

  // Select an exam and load its details
  function selectExam(exam) {
    clearTimerState();
    selectedExam = exam;
    mainActiveTab = 'write';
    startTimerForExam(exam);
    fastapi('get', `/api/v1/ksat/exams/${exam.id}`, {},
      (json) => {
        questions = json.questions || [];
        activePassageQNum = questions[0]?.question_number ?? null;
        // Initialize per-question state
        essayContents = {};
        essaysByQuestion = {};
        feedbacksByQuestion = {};
        activeEssayIdxByQ = {};
        activeFeedbackIdxByQ = {};
        exampleAnswers = {};
        questions.forEach(q => {
          essayContents[q.question_number] = '';
          essaysByQuestion[q.question_number] = [];
          feedbacksByQuestion[q.question_number] = [];
          activeEssayIdxByQ[q.question_number] = 0;
          activeFeedbackIdxByQ[q.question_number] = 0;
          getEssaysByPromptId(q);
          if (q.rubric_name) loadCriteriaLabels(q.rubric_name);
        });
      },
      (json_error) => { error = json_error; }
    );
  }

  // Per-question data fetching
  function getEssaysByPromptId(q) {
    fastapi('get', '/api/v1/ksat/essays', { prompt_id: q.prompt_id },
      (json) => {
        essaysByQuestion[q.question_number] = json;
        essaysByQuestion = essaysByQuestion; // trigger reactivity
        if (json.length > 0) {
          activeEssayIdxByQ[q.question_number] = 0;
          activeEssayIdxByQ = activeEssayIdxByQ;
          getFeedbacksByEssayId(q, json[0]);
        }
      },
      (json_error) => { error = json_error; }
    );
  }

  function getFeedbacksByEssayId(q, essay) {
    fastapi('get', '/api/v1/ksat/feedbacks',
      { prompt_id: q.prompt_id, essay_id: essay.id },
      (json) => {
        feedbacksByQuestion[q.question_number] = json;
        feedbacksByQuestion = feedbacksByQuestion;
      },
      (json_error) => { error = json_error; }
    );
  }

  function getExampleAnswers() {
    questions.forEach(q => {
      fastapi('get', '/api/v1/ksat/example', { prompt_id: q.prompt_id },
        (json) => {
          exampleAnswers[q.question_number] = json.content || '';
          exampleAnswers = exampleAnswers;
        },
        () => {
          exampleAnswers[q.question_number] = '';
          exampleAnswers = exampleAnswers;
        }
      );
    });
  }

  // Fetch criteria labels for a rubric
  function loadCriteriaLabels(rubricName) {
    if (!rubricName || criteriaLabelsMap[rubricName]) return;
    fastapi('get', '/api/v1/ksat/criteria', { name: rubricName },
      (json) => {
        const labels = {};
        json.forEach(c => {
          // Map snake_case or any key to human-readable name
          const key = c.name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_가-힣]/g, '');
          labels[key] = c.name;
          labels[c.name] = c.name; // also map exact name
        });
        criteriaLabelsMap[rubricName] = labels;
        criteriaLabelsMap = criteriaLabelsMap;
      },
      () => {}
    );
  }

  // At least one question has content
  $: anyEssayFilled = questions.length > 0 &&
    questions.some(q => (essayContents[q.question_number] || '').trim().length > 0);

  // All questions have content
  $: allEssaysFilled = questions.length > 0 &&
    questions.every(q => (essayContents[q.question_number] || '').trim().length > 0);

  // Filled count for progress display
  $: filledCount = questions.filter(
    q => (essayContents[q.question_number] || '').trim().length > 0
  ).length;

  async function submitAndGenerateFeedback() {
    if (!anyEssayFilled || isGeneratingFeedback) return;

    // Only process questions that have content
    const filledQuestions = questions.filter(
      q => (essayContents[q.question_number] || '').trim().length > 0
    );

    if (!allEssaysFilled) {
      const unfilled = questions
        .filter(q => (essayContents[q.question_number] || '').trim().length === 0)
        .map(q => `문제 ${q.question_number}`)
        .join(', ');
      const proceed = await askSubmitConfirm(unfilled);
      if (!proceed) return;
    }

    isGeneratingFeedback = true;
    try {
      // Step 1: save filled essays
      const submitPromises = filledQuestions.map(q =>
        apiCall('post', '/api/v1/ksat/essays', {
          prompt_id: q.prompt_id,
          content: essayContents[q.question_number]
        })
      );
      const savedEssays = await Promise.all(submitPromises);

      // Update local state with saved essays
      savedEssays.forEach((essay, i) => {
        const qNum = filledQuestions[i].question_number;
        essaysByQuestion[qNum] = [essay, ...(essaysByQuestion[qNum] || [])];
        activeEssayIdxByQ[qNum] = 0;
      });
      essaysByQuestion = essaysByQuestion;
      activeEssayIdxByQ = activeEssayIdxByQ;

      // Step 2: generate feedback for filled essays
      const fbPromises = filledQuestions.map((q, i) => {
        const essay = savedEssays[i];
        return apiCall('post', `/api/v1/ksat/essays/${essay.id}/feedback`, {
          prompt: `[문제 ${q.question_number}] ${q.prompt_content || ''}`,
          rubric_name: q.rubric_name,
          model_provider_name: selectedAIModelProvider?.name || '',
          api_model_name: selectedFeedbackModel?.api_model_name || '',
        });
      });
      await Promise.all(fbPromises);

      // Reload feedback for filled questions
      filledQuestions.forEach((q, i) => {
        getFeedbacksByEssayId(q, savedEssays[i]);
      });
      mainActiveTab = 'feedback';
    } catch (err) {
      error = err;
    } finally {
      isGeneratingFeedback = false;
    }
  }

  // Score helpers
  function getQuestionScore(q) {
    const fbList = feedbacksByQuestion[q.question_number] || [];
    if (fbList.length === 0) return null;
    const idx = activeFeedbackIdxByQ[q.question_number] || 0;
    return fbList[idx]?.content?.overall_score ?? null;
  }

  function computeTotalScore() {
    let total = 0;
    for (const q of questions) {
      const score = getQuestionScore(q);
      if (score === null) return null;
      total += Number(score);
    }
    return total;
  }

  function computeMaxScore() {
    return questions.reduce((sum, q) => sum + (q.max_points || 0), 0);
  }

  // Build a display title for an exam (e.g. "2025학년도 중앙대학교 모의논술 인문사회계열")
  function examDisplayTitle(exam) {
    if (!exam) return '';
    const trackLabel = exam.track === 'humanities' ? '인문사회계열' : '자연계열';
    const typeLabel = exam.exam_type === 'mock' ? '모의논술' : '수시논술';
    return `${exam.year}학년도 ${exam.university} ${typeLabel} ${trackLabel}`;
  }

  // University grouping
  $: groupedExams = exams.reduce((acc, exam) => {
    if (!acc[exam.university]) acc[exam.university] = [];
    acc[exam.university].push(exam);
    return acc;
  }, {});

  $: filteredUniversities = Object.keys(groupedExams).filter(
    uni => !universitySearch || uni.includes(universitySearch)
  );

  const tabItems = [
    { id: 'prompts', label: '기출문제', icon: BookOpen },
    { id: 'write', label: '답안 작성', icon: PenLine },
    { id: 'example', label: '예시 답안', icon: FileText },
    { id: 'feedback', label: '피드백', icon: BarChart },
  ];
</script>

<InfoDeskModal
  open={showInfoDeskModalOpen}
  onClose={() => (showInfoDeskModalOpen = false)}
/>
<ManageKeyModal
  open={showManageKeyModalOpen}
  onClose={() => (showManageKeyModalOpen = false)}
  {AIModelProviders}
  locale="ko"
/>

<Modal
  open={showSubmitConfirm}
  title="미작성 답안이 있습니다"
  size="md"
  onClose={() => resolveSubmitConfirm(false)}
>
  <svelte:fragment slot="icon">
    <span class="submit-confirm-icon"><AlertTriangle size={18} /></span>
  </svelte:fragment>

  <div class="submit-confirm-body">
    <p class="submit-confirm-lead">아직 작성하지 않은 답안이 있습니다.</p>
    <div class="submit-confirm-unfilled">{unfilledLabels}</div>
    <p class="submit-confirm-note">
      그대로 제출하면 해당 문제는 <strong>채점 및 첨삭이 진행되지 않습니다.</strong>
      계속 진행하시겠습니까?
    </p>
  </div>

  <svelte:fragment slot="footer">
    <button type="button" class="btn btn-secondary" on:click={() => resolveSubmitConfirm(false)}>취소</button>
    <button type="button" class="btn btn-primary" on:click={() => resolveSubmitConfirm(true)}>그래도 제출</button>
  </svelte:fragment>
</Modal>

<div class="ksat-layout">
  <!-- Left Sidebar -->
  <aside class="ksat-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-dot"></span>
      <h3>대학별 논술</h3>
    </div>

    <div class="sidebar-search">
      <Search size={14} class="search-icon" />
      <input
        type="text"
        placeholder="대학교 검색..."
        bind:value={universitySearch}
      />
    </div>

    <div class="university-list">
      {#each filteredUniversities as university}
        {@const uniExams = groupedExams[university]}
        <button
          class="university-item"
          class:active={selectedUniversity === university}
          on:click={() => {
            clearTimerState();
            selectedUniversity = university;
            selectedExam = null;
            mainActiveTab = 'prompts';
          }}
        >
          <span class="uni-badge">{university.charAt(0)}</span>
          <span class="uni-name">{university}</span>
          <span class="uni-count">{uniExams.length}</span>
        </button>
      {/each}

      {#if filteredUniversities.length === 0}
        <div class="empty-message">등록된 대학이 없습니다.</div>
      {/if}
    </div>
  </aside>

  <!-- Main Content -->
  <main class="ksat-main">
    <TopBar
      domainName="대학별 논술"
      onInfoClick={() => (showInfoDeskModalOpen = true)}
      onManageKeyClick={() => (showManageKeyModalOpen = true)}
      locale="ko"
    />

    <!-- Tab Navigation -->
    <div class="ksat-tabs">
      {#each tabItems as tab}
        <button
          class="ksat-tab"
          class:active={mainActiveTab === tab.id}
          on:click={() => {
            mainActiveTab = tab.id;
            if (tab.id === 'example') getExampleAnswers();
          }}
        >
          <svelte:component this={tab.icon} size={16} />
          {tab.label}
        </button>
      {/each}
    </div>

    {#if hasApiKeys === false}
      <div class="onboarding-banner">
        <strong>시작하기:</strong> 피드백을 받으려면 API 키가 필요합니다.
        <button class="onboarding-link" on:click={() => (showManageKeyModalOpen = true)}>API 키 등록</button>을 먼저 해주세요.
        <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">OpenAI</a> 또는
        <a href="https://console.anthropic.com/" target="_blank" rel="noopener">Anthropic</a>에서 발급받을 수 있습니다.
      </div>
    {/if}

    <div class="ksat-content">
      {#if mainActiveTab === 'prompts'}
        <!-- Exam list for selected university -->
        {#if selectedUniversity}
          {@const uniExams = groupedExams[selectedUniversity] || []}
          <div class="exam-list">
            <h3 class="exam-list-heading">{selectedUniversity} 논술 기출문제</h3>
            {#each uniExams as exam (exam.id)}
              <button
                class="exam-list-item"
                class:active={selectedExam?.id === exam.id}
                on:click={() => selectExam(exam)}
              >
                <span class="year-badge">{exam.year}학년도</span>
                <span class="exam-list-title">{examDisplayTitle(exam)}</span>
              </button>
            {/each}
          </div>
        {:else}
          <div class="empty-message">왼쪽 사이드바에서 대학교를 선택하세요.</div>
        {/if}

      {:else if mainActiveTab === 'write'}
        <!-- Essay writing: all questions -->
        <div class="write-layout">
          <div class="passages-panel">
            <h4 class="panel-title">제시문</h4>
            <div class="exam-text">{@html safeHtml(activePassageContent)}</div>
          </div>

          <div class="essay-panel">
            <div class="essay-panel-header">
              <div class="essay-panel-header-title">
                <h4 class="panel-title">답안 작성</h4>
                {#if selectedExam?.duration_minutes}
                  <div
                    class="timer"
                    class:warning={timerIsWarning}
                    class:over={timerIsOver}
                    role="timer"
                    aria-live="polite"
                    aria-label={timerIsOver
                      ? '제한 시간이 초과되었습니다'
                      : `남은 시간 ${formatTimerDisplay(timerRemainingSeconds)}`}
                  >
                    <Clock size={14} aria-hidden="true" />
                    {#if timerIsOver}
                      <span class="timer-label">시간 초과</span>
                    {:else}
                      <span class="timer-label">남은 시간</span>
                      <span class="timer-value">{formatTimerDisplay(timerRemainingSeconds)}</span>
                    {/if}
                    <button
                      type="button"
                      class="timer-reset"
                      on:click={resetTimer}
                      aria-label="타이머 재설정"
                      title="타이머 재설정"
                    >
                      <RotateCcw size={13} aria-hidden="true" />
                    </button>
                  </div>
                {/if}
              </div>
              {#if questions.length > 1}
                <div class="passage-question-tabs">
                  {#each questions as q (q.question_number)}
                    {@const filled = (essayContents[q.question_number] || '').trim().length > 0}
                    <button
                      class="passage-question-tab"
                      class:active={activePassageQNum === q.question_number}
                      class:filled
                      on:click={() => (activePassageQNum = q.question_number)}
                      aria-label={filled ? `문제 ${q.question_number} (작성 완료)` : `문제 ${q.question_number} (미작성)`}
                    >
                      <span class="tab-status-icon" aria-hidden="true">
                        {#if filled}
                          <Check size={14} strokeWidth={3} />
                        {:else}
                          <Circle size={14} strokeWidth={2} />
                        {/if}
                      </span>
                      문제 {q.question_number}
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
            {#each questions.filter(q => q.question_number === activePassageQNum) as q (q.question_number)}
              <div class="question-write-section">
                <div class="question-write-header">
                  <span class="question-write-label">[문제 {q.question_number}]</span>
                  <span class="question-write-points">{q.max_points}점</span>
                </div>
                <p class="question-prompt-mini">{q.prompt_content || ''}</p>
                <div class="char-counter"
                  class:warning={q.char_min && q.char_max && ((essayContents[q.question_number] || '').length < q.char_min || (essayContents[q.question_number] || '').length > q.char_max)}
                >
                  {(essayContents[q.question_number] || '').length}자
                  {#if q.char_min && q.char_max}
                    / {q.char_min}~{q.char_max}자
                  {/if}
                </div>
                <textarea
                  bind:value={essayContents[q.question_number]}
                  placeholder="문제 {q.question_number} 답안을 작성하세요..."
                  rows="12"
                  class="essay-textarea"
                ></textarea>
              </div>
            {/each}

            {#if questions.length > 0}
              <div class="essay-actions">
                <ModelSelector
                  {AIModelProviders}
                  bind:selectedAIModelProvider
                  {feedbackModels}
                  bind:selectedFeedbackModel
                />
                <div class="submit-group">
                  <span class="progress-text" class:complete={allEssaysFilled}>
                    {#if allEssaysFilled}
                      모든 문제 작성 완료 ({filledCount}/{questions.length})
                    {:else}
                      작성 완료 {filledCount}/{questions.length}
                    {/if}
                  </span>
                  <button
                    class="btn btn-primary"
                    on:click={submitAndGenerateFeedback}
                    disabled={!anyEssayFilled || isGeneratingFeedback}
                  >
                    {isGeneratingFeedback ? '채점 중...' : '채점 받기'}
                  </button>
                </div>
              </div>
            {:else}
              <div class="empty-message">기출문제 탭에서 문제를 확인한 후 답안을 작성하세요.</div>
            {/if}
          </div>
        </div>

      {:else if mainActiveTab === 'example'}
        <!-- Example answers for all questions -->
        <div class="example-panel">
          <h4 class="panel-title">예시 답안</h4>
          {#if questions.length > 0}
            {#each questions as q}
              <div class="example-section">
                <h5 class="example-question-title">[문제 {q.question_number}] ({q.max_points}점)</h5>
                {#if exampleAnswers[q.question_number]}
                  <div class="example-content">{exampleAnswers[q.question_number]}</div>
                {:else}
                  <div class="empty-message-inline">예시 답안이 아직 등록되지 않았습니다.</div>
                {/if}
              </div>
            {/each}
          {:else}
            <div class="empty-message">문제를 선택한 후 예시 답안을 확인하세요.</div>
          {/if}
        </div>

      {:else if mainActiveTab === 'feedback'}
        <!-- Feedback display with total score -->
        <div class="feedback-panel">
          {#if isGeneratingFeedback}
            <div class="loading-indicator">
              <div class="spinner"></div>
              <p>채점 중입니다... 10~30초 정도 소요됩니다.</p>
            </div>
          {/if}
          {#if questions.length > 0}
            <!-- Total score card -->
            <div class="total-score-card">
              <div class="total-score-label">총점</div>
              <div class="total-score-value">
                {#if computeTotalScore() !== null}
                  {computeTotalScore()} / {computeMaxScore()}
                {:else}
                  - / {computeMaxScore()}
                {/if}
              </div>
              <div class="per-question-scores">
                {#each questions as q}
                  <div class="per-q-score">
                    <span class="per-q-label">문제 {q.question_number}</span>
                    <span class="per-q-value">
                      {getQuestionScore(q) !== null ? getQuestionScore(q) : '-'} / {q.max_points}
                    </span>
                  </div>
                {/each}
              </div>
            </div>

            <!-- Per-question feedback -->
            {#each questions as q}
              {@const essays = essaysByQuestion[q.question_number] || []}
              {@const fbList = feedbacksByQuestion[q.question_number] || []}
              <div class="question-feedback-section">
                <h4 class="question-feedback-title">[문제 {q.question_number}] 피드백 ({q.max_points}점 만점)</h4>

                {#if essays.length > 0}
                  <!-- Attempt tabs -->
                  <div class="attempt-tabs">
                    {#each essays as essay, index}
                      <button
                        class="attempt-tab"
                        class:active={activeEssayIdxByQ[q.question_number] === index}
                        on:click={() => {
                          activeEssayIdxByQ[q.question_number] = index;
                          activeEssayIdxByQ = activeEssayIdxByQ;
                          activeFeedbackIdxByQ[q.question_number] = 0;
                          activeFeedbackIdxByQ = activeFeedbackIdxByQ;
                          getFeedbacksByEssayId(q, essay);
                        }}
                      >
                        시도 #{essays.length - index}
                        <span class="attempt-date">{essay.submitted_at}</span>
                      </button>
                    {/each}
                  </div>

                  {#if fbList.length > 0}
                    <div class="feedback-tabs">
                      {#each fbList as feedback, index}
                        <button
                          class="feedback-tab"
                          class:active={activeFeedbackIdxByQ[q.question_number] === index}
                          on:click={() => {
                            activeFeedbackIdxByQ[q.question_number] = index;
                            activeFeedbackIdxByQ = activeFeedbackIdxByQ;
                          }}
                        >
                          {feedback.bot_name} ({feedback.created_at})
                        </button>
                      {/each}
                    </div>

                    {@const activeFb = fbList[activeFeedbackIdxByQ[q.question_number] || 0]}
                    {#if activeFb}
                      <div class="feedback-content">
                        <ScoreCard
                          feedback={activeFb.content}
                          criteriaLabels={criteriaLabelsMap[q.rubric_name] || {}}
                          maxScore={q.max_points || 40}
                        />

                        {#each Object.entries(activeFb.content?.feedback_by_criteria ?? {}) as [key, { score, feedback }]}
                          <div class="feedback-section">
                            <div class="feedback-heading">{key}</div>
                            <div class="feedback-text">{@html safeHtml(feedback ?? '')}</div>
                          </div>
                        {/each}

                        <div class="feedback-section">
                          <div class="feedback-heading">종합 평가</div>
                          <div class="feedback-text">
                            {@html safeHtml(activeFb.content?.overall_feedback ?? '')}
                          </div>
                        </div>
                      </div>
                    {/if}
                  {:else}
                    <div class="empty-message-inline">아직 피드백이 없습니다.</div>
                  {/if}
                {:else}
                  <div class="empty-message-inline">답안을 먼저 제출하세요.</div>
                {/if}
              </div>
            {/each}
          {:else}
            <div class="empty-message">대학교를 선택하고 답안을 제출하세요.</div>
          {/if}
        </div>
      {/if}
    </div>
  </main>
</div>

<style>
  .ksat-layout {
    display: flex;
    height: 100vh;
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  /* Sidebar */
  .ksat-sidebar {
    width: 240px;
    min-width: 240px;
    border-right: 1px solid #e5e7eb;
    padding: 20px 16px;
    background: #fafafa;
    overflow-y: auto;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }

  .sidebar-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #c44536;
  }

  .sidebar-header h3 {
    font-size: 15px;
    font-weight: 700;
    margin: 0;
  }

  .sidebar-search {
    position: relative;
    margin-bottom: 16px;
  }

  .sidebar-search input {
    width: 100%;
    padding: 8px 8px 8px 30px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 13px;
    background: #fff;
  }

  .sidebar-search :global(.search-icon) {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-secondary, #6b7280);
  }

  .university-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .university-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    width: 100%;
    text-align: left;
    font-size: 14px;
    transition: background 0.15s;
  }

  .university-item:hover {
    background: #f0f0f0;
  }

  .university-item.active {
    background: #fdf0ee;
    color: #c44536;
  }

  .uni-badge {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    flex-shrink: 0;
  }

  .university-item.active .uni-badge {
    background: #c44536;
    color: white;
  }

  .uni-name {
    flex: 1;
  }

  .uni-count {
    font-size: 12px;
    color: var(--color-text-secondary, #6b7280);
    background: #f3f4f6;
    padding: 2px 8px;
    border-radius: 10px;
  }

  /* Main */
  .ksat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .ksat-tabs {
    display: flex;
    border-bottom: 2px solid #f3f4f6;
    padding: 0 24px;
    gap: 4px;
  }

  .ksat-tab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 16px;
    border: none;
    background: transparent;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.15s;
  }

  .ksat-tab:hover {
    color: #c44536;
  }

  .ksat-tab.active {
    color: #c44536;
    border-bottom-color: #c44536;
  }

  .ksat-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  /* Exam list */
  .exam-list {
    max-width: 640px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .exam-list-heading {
    font-size: 18px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 12px 0;
  }

  .exam-list-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
  }

  .exam-list-item:hover {
    border-color: #c44536;
    box-shadow: 0 2px 8px rgba(196, 69, 54, 0.08);
  }

  .exam-list-item.active {
    border-color: #c44536;
    background: #fdf0ee;
  }

  .exam-list-title {
    font-size: 15px;
    font-weight: 600;
    color: #1f2937;
  }

  /* Exam paper (passage panel renders markdown via safeHtml) */
  .exam-text {
    line-height: 1.8;
    font-size: 15px;
    color: #1f2937;
    padding: 24px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .exam-text :global(h3) {
    font-size: 15px;
    font-weight: 700;
    margin: 20px 0 10px 0;
    color: #1f2937;
  }

  .exam-text :global(h3:first-child) {
    margin-top: 0;
  }

  .exam-text :global(p) {
    margin: 0 0 12px 0;
  }

  .exam-text :global(hr) {
    border: none;
    border-top: 1px dashed #d1d5db;
    margin: 20px 0;
  }

  .exam-text :global(img) {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 12px auto;
  }

  .exam-text :global(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 13px;
  }

  .exam-text :global(th),
  .exam-text :global(td) {
    border: 1px solid #d1d5db;
    padding: 6px 10px;
    text-align: left;
  }

  .exam-text :global(th) {
    background: #f9fafb;
    font-weight: 600;
  }

  .exam-text :global(ul) {
    padding-left: 20px;
    margin: 8px 0;
  }

  .exam-text :global(li) {
    margin-bottom: 4px;
  }

  .exam-text :global(em) {
    color: #6b7280;
    font-size: 13px;
  }

  .exam-text :global(blockquote) {
    margin: 12px 0;
    padding: 4px 0 4px 2em;
    border-left: 3px solid #e5e7eb;
    color: #374151;
    font-style: normal;
  }

  .exam-text :global(blockquote p) {
    margin: 4px 0;
    text-indent: 0;
  }

  .year-badge {
    font-size: 12px;
    font-weight: 600;
    color: #c44536;
    background: #fdf0ee;
    padding: 3px 10px;
    border-radius: 4px;
  }

  .track-label {
    font-size: 12px;
    color: var(--color-text-secondary, #6b7280);
  }


  .question-meta {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }

  .meta-item {
    font-size: 13px;
    color: #6b7280;
  }

  .btn-write {
    background: #c44536;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
  }

  .btn-write:hover {
    background: #a93828;
  }

  /* Write layout */
  .write-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    height: calc(100vh - 180px);
  }

  .passages-panel, .essay-panel {
    overflow-y: auto;
  }

  .essay-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .essay-panel-header .panel-title {
    margin: 0;
  }

  .essay-panel-header-title {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .timer {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 6px;
    background: #f3f4f6;
    color: #374151;
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    border: 1px solid #e5e7eb;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
  }

  .timer-label {
    font-weight: 500;
    color: #6b7280;
  }

  .timer-value {
    font-weight: 700;
    letter-spacing: 0.02em;
  }

  .timer.warning {
    background: #fdf0ee;
    color: #c44536;
    border-color: #c44536;
  }

  .timer.warning .timer-label {
    color: #c44536;
  }

  .timer.over {
    background: #c44536;
    color: #fff;
    border-color: #c44536;
    animation: timer-blink 1s ease-in-out infinite;
  }

  @keyframes timer-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.55; }
  }

  @media (prefers-reduced-motion: reduce) {
    .timer.over { animation: none; }
  }

  .timer-reset {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 2px;
    margin-left: 2px;
    border: none;
    background: transparent;
    color: inherit;
    cursor: pointer;
    border-radius: 4px;
    opacity: 0.7;
  }

  .timer-reset:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.06);
  }

  .timer.over .timer-reset:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .passage-question-tabs {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .passage-question-tab {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    background: #fff;
    color: #6b7280;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.2;
    cursor: pointer;
    transition: all 0.15s;
  }

  .passage-question-tab:hover {
    border-color: #c44536;
    color: #c44536;
  }

  .passage-question-tab.filled {
    border-color: #16a34a;
    background: #f0fdf4;
    color: #15803d;
  }

  .passage-question-tab.filled:hover {
    border-color: #15803d;
    color: #166534;
  }

  .passage-question-tab.active {
    background: #c44536;
    color: white;
    border-color: #c44536;
  }

  .passage-question-tab.filled.active {
    background: #c44536;
    border-color: #c44536;
    color: white;
  }

  .tab-status-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #d1d5db;
  }

  .passage-question-tab.filled .tab-status-icon {
    color: #16a34a;
  }

  .passage-question-tab.active .tab-status-icon {
    color: rgba(255, 255, 255, 0.95);
  }

  .panel-title {
    font-size: 14px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: #374151;
  }

  /* Question write sections */
  .question-write-section {
    margin-bottom: 24px;
    padding: 20px;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #fff;
  }

  .question-write-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .question-write-label {
    font-size: 15px;
    font-weight: 700;
    color: #1f2937;
  }

  .question-write-points {
    font-size: 13px;
    font-weight: 600;
    color: #c44536;
    background: #fdf0ee;
    padding: 2px 10px;
    border-radius: 4px;
  }

  .question-prompt-mini {
    font-size: 13px;
    line-height: 1.6;
    color: #6b7280;
    margin: 0 0 10px 0;
  }

  .char-counter {
    text-align: right;
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 8px;
  }

  .char-counter.warning {
    color: #dc2626;
    font-weight: 600;
  }

  .essay-textarea {
    width: 100%;
    padding: 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 15px;
    line-height: 1.8;
    resize: none;
    font-family: inherit;
  }

  .essay-textarea:focus {
    outline: none;
    border-color: #c44536;
  }

  .essay-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .submit-group {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .progress-text {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
  }

  .progress-text.complete {
    color: #16a34a;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: default;
  }

  /* Example */
  .example-panel {
    max-width: 800px;
  }

  .example-section {
    margin-bottom: 24px;
  }

  .example-question-title {
    font-size: 15px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 12px 0;
  }

  .example-content {
    white-space: pre-wrap;
    line-height: 1.8;
    font-size: 15px;
    padding: 24px;
    background: #fafafa;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  /* Feedback */
  .feedback-panel {
    max-width: 900px;
  }

  /* Total score card */
  .total-score-card {
    background: linear-gradient(135deg, #1f2937, #374151);
    color: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 28px;
  }

  .total-score-label {
    font-size: 13px;
    font-weight: 500;
    opacity: 0.8;
    margin-bottom: 4px;
  }

  .total-score-value {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 16px;
  }

  .per-question-scores {
    display: flex;
    gap: 16px;
  }

  .per-q-score {
    display: flex;
    flex-direction: column;
    gap: 2px;
    background: rgba(255, 255, 255, 0.1);
    padding: 8px 16px;
    border-radius: 8px;
  }

  .per-q-label {
    font-size: 12px;
    opacity: 0.7;
  }

  .per-q-value {
    font-size: 16px;
    font-weight: 700;
  }

  /* Per-question feedback */
  .question-feedback-section {
    margin-bottom: 28px;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 24px;
    background: #fff;
  }

  .question-feedback-title {
    font-size: 16px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
  }

  .attempt-tabs, .feedback-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    overflow-x: auto;
  }

  .attempt-tab, .feedback-tab {
    padding: 8px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
    font-size: 13px;
    white-space: nowrap;
  }

  .attempt-tab.active, .feedback-tab.active {
    background: #c44536;
    color: white;
    border-color: #c44536;
  }

  .attempt-date {
    display: block;
    font-size: 11px;
    color: var(--color-text-secondary, #6b7280);
  }

  .attempt-tab.active .attempt-date {
    color: rgba(255, 255, 255, 0.7);
  }

  .feedback-content {
    background: #fafafa;
    border-radius: 8px;
    padding: 20px;
  }

  .feedback-section {
    margin-bottom: 16px;
  }

  .feedback-heading {
    font-size: 16px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .feedback-text {
    font-size: 14px;
    line-height: 1.7;
    color: #374151;
  }

  .empty-message {
    text-align: center;
    color: var(--color-text-secondary, #6b7280);
    padding: 40px 20px;
    font-size: 14px;
  }

  .empty-message-inline {
    color: var(--color-text-secondary, #6b7280);
    padding: 16px 0;
    font-size: 14px;
  }

  /* Loading indicator for KSAT */
  .loading-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    color: var(--color-text-secondary, #6b7280);
    font-size: 14px;
  }
  .spinner {
    width: 36px;
    height: 36px;
    border: 3px solid var(--color-border, #e5e7eb);
    border-top-color: var(--color-ksat, #c44536);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Submit confirmation modal */
  .submit-confirm-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #fef3c7;
    color: #b45309;
    margin-right: 10px;
  }

  .submit-confirm-body {
    padding: 4px 0;
  }

  .submit-confirm-lead {
    font-size: 15px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 12px 0;
  }

  .submit-confirm-unfilled {
    background: #fef3c7;
    color: #92400e;
    border-left: 3px solid #f59e0b;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 14px;
  }

  .submit-confirm-note {
    font-size: 14px;
    line-height: 1.6;
    color: #374151;
    margin: 0;
  }

  .submit-confirm-note strong {
    color: #b91c1c;
  }

  .onboarding-banner {
    background: var(--color-ksat-pale, #fdf0ee);
    border: 1px solid var(--color-ksat, #c44536);
    border-radius: var(--radius-md, 8px);
    padding: 12px 16px;
    margin: 0 24px 12px 24px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-text-primary, #1f2937);
  }
  .onboarding-banner a {
    color: var(--color-ksat, #c44536);
    text-decoration: underline;
  }
  .onboarding-link {
    background: none;
    border: none;
    color: var(--color-ksat, #c44536);
    text-decoration: underline;
    cursor: pointer;
    padding: 0;
    font-size: inherit;
  }

  /* Responsive: mobile */
  @media (max-width: 768px) {
    .ksat-layout {
      flex-direction: column;
      height: auto;
      min-height: 100vh;
    }
    .ksat-sidebar {
      width: 100%;
      min-width: 100%;
      max-height: 200px;
      border-right: none;
      border-bottom: 1px solid var(--color-border, #e5e7eb);
      padding: 12px;
    }
    .university-list {
      flex-direction: row;
      flex-wrap: wrap;
      gap: 4px;
    }
    .university-item {
      padding: 6px 10px;
      font-size: 13px;
      width: auto;
    }
    .uni-badge {
      width: 24px;
      height: 24px;
      font-size: 11px;
    }
    .write-layout {
      grid-template-columns: 1fr;
      height: auto;
    }
    .ksat-tabs {
      padding: 0 12px;
      overflow-x: auto;
    }
    .ksat-content {
      padding: 16px;
    }
    .per-question-scores {
      flex-wrap: wrap;
    }
  }
</style>
