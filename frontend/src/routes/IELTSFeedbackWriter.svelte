<script>
  import { isLogin, accessToken } from '../lib/store.js';
  import { get } from 'svelte/store';
  import fastapi from '../lib/api.js';
  import { fastapiUpload } from '../lib/api.js';
  import { onMount, tick } from 'svelte';
  import { push } from 'svelte-spa-router';
  import './home.css';
  import { BookOpen, FileText, BarChart, Search } from 'lucide-svelte';

  import Error from '../components/Error.svelte';
  import TopBar from '../components/TopBar.svelte';
  import InfoDeskModal from '../components/InfoDeskModal.svelte';
  import ManageKeyModal from '../components/ManageKeyModal.svelte';
  import PromptList from '../components/PromptList.svelte';
  import EssayWriter from '../components/EssayWriter.svelte';
  import ExampleAnswer from '../components/ExampleAnswer.svelte';
  import FeedbackView from '../components/FeedbackView.svelte';

  // Core state
  let mainActiveTab = 'prompts';
  let promptContent = '';
  let promptId = null;
  let essayContent = '';
  let inputMode = 'text';
  let handwritingImageUrl = null;
  let loadedImageEssayId = null;

  let showInfoDeskModalOpen = false;
  let showManageKeyModalOpen = false;

  let activeIdOfessays = 0;
  let activeIdOfFeedbacks = 0;
  let rubricCriteria = [];
  let submittedEssayContent = null;
  let submittedEssayId = null;
  let registeredEssayList = [];
  let editing = false;

  let prompts = [];
  let feedbackList = [];
  let exampleAnswer = '';
  let exampleRequestId = 0;

  let AIModelProviders = [];
  let selectedAIModelProvider = null;
  let feedbackModels = [];
  let selectedFeedbackModel = null;

  let error = { detail: [] };
  let isSubmitting = false;
  let isGeneratingFeedback = false;
  let feedbackError = '';
  let hasApiKeys = null; // null = unknown, true/false

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
    alert('You need to login to use the service.');
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
        if (AIModelProviders.length > 0) {
          selectedAIModelProvider = AIModelProviders[0];
        }
      },
      (json_error) => { error = json_error; }
    );
  }
  read_providers();

  // Rubric criteria
  function getRubricCriteria() {
    fastapi('get', '/api/v1/ielts/criteria', { name: 'IELTS Writing Task 2' },
      (json) => { rubricCriteria = json; },
      (json_error) => { error = json_error; }
    );
  }
  getRubricCriteria();

  // Prompts
  function getPrompts() {
    fastapi('get', '/api/v1/ielts/prompts', {},
      (json) => {
        prompts = json.map((item) => ({ id: item.id, content: item.content }));
      },
      (json_error) => { error = json_error; }
    );
  }
  getPrompts();

  // Example answer
  function getExampleAnswer() {
    const requestId = ++exampleRequestId;
    fastapi('get', '/api/v1/ielts/example', { prompt_id: promptId },
      (json) => {
        if (requestId === exampleRequestId) exampleAnswer = json.content;
      },
      (json_error) => { error = json_error; }
    );
  }

  // Essays
  function getEssaysByPromptId() {
    return new Promise((resolve, reject) => {
      fastapi('get', '/api/v1/ielts/essays', { prompt_id: promptId },
        (json) => { registeredEssayList = json; resolve(); },
        (json_error) => { error = json_error; reject(json_error); }
      );
    });
  }

  function getFeedbacksByEssayId(essay_id) {
    fastapi('get', '/api/v1/ielts/feedbacks', { prompt_id: promptId, essay_id },
      (json) => { activeIdOfFeedbacks = 0; feedbackList = json; },
      (json_error) => { error = json_error; }
    );
  }

  // Prompt selection
  function selectPrompt(selectedPrompt) {
    promptContent = selectedPrompt.content;
    if (promptId !== selectedPrompt.id) essayContent = '';
    promptId = selectedPrompt.id;
    getExampleAnswer();
    mainActiveTab = 'write';
    getEssaysByPromptId().then(() => {
      activeIdOfFeedbacks = 0;
      activeIdOfessays = 0;
      if (registeredEssayList.length > 0) {
        getFeedbacksByEssayId(registeredEssayList[activeIdOfessays].id);
      }
    });
  }

  // Computed word count
  $: wordCount = essayContent.trim() ? essayContent.trim().split(/\s+/).filter(w => w.length > 0).length : 0;

  // Essay submission
  function submitEssay() {
    if (isSubmitting) return;
    isSubmitting = true;
    feedbackError = '';
    fastapi('post', '/api/v1/ielts/essays', { prompt_id: promptId, content: essayContent },
      (json) => {
        editing = false;
        submittedEssayId = json.id;
        submittedEssayContent = json.content;
        getEssaysByPromptId().then(() => {
          mainActiveTab = 'feedback';
          activeIdOfFeedbacks = 0;
          activeIdOfessays = 0;
          isSubmitting = false;
          generateFeedback();
        }).catch((err) => { error = err; isSubmitting = false; });
      },
      (json_error) => { error = json_error; isSubmitting = false; }
    );
  }

  async function submitHandwritingEssay(canvasComponent) {
    if (isSubmitting) return;
    if (!canvasComponent || canvasComponent.isEmpty()) {
      feedbackError = 'Please write something on the canvas first.';
      return;
    }
    isSubmitting = true;
    feedbackError = '';
    const blob = await canvasComponent.exportBlob();
    const formData = new FormData();
    formData.append('image', blob, 'essay.png');
    fastapiUpload(`/api/v1/ielts/essays/handwriting?prompt_id=${promptId}`, formData,
      (json) => {
        editing = false;
        submittedEssayId = json.id;
        submittedEssayContent = json.ocr_text || '(Handwriting submitted)';
        getEssaysByPromptId().then(() => {
          mainActiveTab = 'feedback';
          activeIdOfFeedbacks = 0;
          activeIdOfessays = 0;
          isSubmitting = false;
          generateFeedback();
        }).catch((err) => { error = err; isSubmitting = false; });
      },
      (json_error) => { error = json_error; isSubmitting = false; }
    );
  }

  function generateFeedback() {
    if (isGeneratingFeedback) return;
    isGeneratingFeedback = true;
    feedbackError = '';
    let params = {
      prompt: promptContent,
      rubric_name: 'IELTS Writing Task 2',
      model_provider_name: selectedAIModelProvider.name,
      api_model_name: selectedFeedbackModel.api_model_name,
    };
    if (essayContent && essayContent.trim()) params.essay_content = essayContent;
    feedbackList = [];
    fastapi('post', `/api/v1/ielts/essays/${submittedEssayId}/feedback`, params,
      () => {
        isGeneratingFeedback = false;
        getEssaysByPromptId();
        getFeedbacksByEssayId(submittedEssayId);
      },
      (json_error) => {
        isGeneratingFeedback = false;
        feedbackError = json_error?.detail || 'An unknown error occurred. Please check your API key and try again.';
      }
    );
  }

  // Handwriting image loading
  async function loadEssayImage(essayId) {
    if (essayId === loadedImageEssayId && handwritingImageUrl) return;
    if (handwritingImageUrl) {
      URL.revokeObjectURL(handwritingImageUrl);
      handwritingImageUrl = null;
    }
    loadedImageEssayId = essayId;
    const _access_token = get(accessToken);
    const url = import.meta.env.VITE_SERVER_URL + `/api/v1/ielts/essays/${essayId}/image`;
    const resp = await fetch(url, { headers: { Authorization: 'Bearer ' + _access_token } });
    if (resp.ok) {
      const blob = await resp.blob();
      handwritingImageUrl = URL.createObjectURL(blob);
    }
  }


</script>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

<InfoDeskModal
  open={showInfoDeskModalOpen}
  onClose={() => (showInfoDeskModalOpen = false)}
  {rubricCriteria}
/>

<ManageKeyModal
  open={showManageKeyModalOpen}
  onClose={() => (showManageKeyModalOpen = false)}
  {AIModelProviders}
/>

<div class="d-flex">
  <div class="message-container">
    <TopBar
      domainName="IELTS Feedback Writer"
      onInfoClick={() => (showInfoDeskModalOpen = true)}
      onManageKeyClick={() => (showManageKeyModalOpen = true)}
    />

    {#if hasApiKeys === false}
      <div class="onboarding-banner">
        <strong>Getting Started:</strong> You need an API key to generate feedback.
        <button class="onboarding-link" on:click={() => (showManageKeyModalOpen = true)}>Register your API key</button>
        to get started. You can get one from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">OpenAI</a> or <a href="https://console.anthropic.com/" target="_blank" rel="noopener">Anthropic</a>.
      </div>
    {/if}

    <div class="messages">
      <!-- Main tab bar -->
      <div class="main-tabs flex mb-6" style="border-bottom: 1px solid var(--color-border, #ddd);">
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'prompts' ? 'active' : ''}"
          on:click={() => (mainActiveTab = 'prompts')}
        >
          <Search class="w-4 h-4 mr-2" />
          Prompts
        </button>
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'write' ? 'active' : ''}"
          disabled={!promptContent}
          on:click={() => promptContent && (mainActiveTab = 'write')}
        >
          <FileText class="w-4 h-4 mr-2" />
          Write Essay
        </button>
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'example' ? 'active' : ''}"
          disabled={!promptContent}
          on:click={() => promptContent && (mainActiveTab = 'example')}
        >
          <BookOpen class="w-4 h-4 mr-2" />
          Example
        </button>
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'feedback' ? 'active' : ''}"
          disabled={!promptContent || registeredEssayList.length === 0}
          on:click={() => promptContent && registeredEssayList.length > 0 && (mainActiveTab = 'feedback')}
        >
          <BarChart class="w-4 h-4 mr-2" />
          Feedback
        </button>
      </div>

      <!-- Error banner -->
      {#if feedbackError}
        <div class="error-banner">
          <span>{feedbackError}</span>
          <button class="error-dismiss" on:click={() => (feedbackError = '')}>✕</button>
        </div>
      {/if}

      <!-- Tab content -->
      <div class="flex-1">
        {#if mainActiveTab === 'prompts'}
          <PromptList {prompts} activePromptContent={promptContent} onSelectPrompt={selectPrompt} />
        {:else if mainActiveTab === 'write'}
          <EssayWriter
            {promptContent}
            bind:essayContent
            bind:inputMode
            {wordCount}
            onSubmitEssay={submitEssay}
            onSubmitHandwriting={submitHandwritingEssay}
            {AIModelProviders}
            bind:selectedAIModelProvider
            {feedbackModels}
            bind:selectedFeedbackModel
            {isSubmitting}
          />
        {:else if mainActiveTab === 'feedback'}
          {#if isGeneratingFeedback}
            <div class="loading-indicator">
              <div class="spinner"></div>
              <p>Generating feedback... This may take 10–30 seconds.</p>
            </div>
          {/if}
          <FeedbackView
            {registeredEssayList}
            bind:activeIdOfessays
            {feedbackList}
            bind:activeIdOfFeedbacks
            {promptContent}
            bind:essayContent
            bind:editing
            onSubmitEssay={submitEssay}
            onEssaySelect={(essay) => getFeedbacksByEssayId(essay.id)}
            onLoadImage={loadEssayImage}
            {handwritingImageUrl}
            {AIModelProviders}
            bind:selectedAIModelProvider
            {feedbackModels}
            bind:selectedFeedbackModel
          />
        {:else if mainActiveTab === 'example'}
          <ExampleAnswer {exampleAnswer} />
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .main-tabs button {
    background-color: var(--color-bg-surface, #f9fafb);
  }
  .main-tabs button:hover {
    background-color: var(--color-bg-hover, #eef2f7);
  }
  .main-tabs button.active {
    background-color: var(--color-ielts, #2c5f8a);
    color: white;
    border-color: var(--color-ielts, #2c5f8a);
  }
  .main-tabs button:disabled {
    opacity: 0.4;
    cursor: default;
  }
  .main-tabs button:disabled:hover {
    background-color: var(--color-bg-surface, #f9fafb);
  }
  .error-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
    padding: 12px 16px;
    border-radius: var(--radius-md, 8px);
    margin-bottom: 16px;
    font-size: 14px;
  }
  .error-dismiss {
    background: none;
    border: none;
    color: #991b1b;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
  }
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
    border-top-color: var(--color-ielts, #2c5f8a);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .onboarding-banner {
    background: var(--color-ielts-pale, #e8f0f8);
    border: 1px solid var(--color-ielts, #2c5f8a);
    border-radius: var(--radius-md, 8px);
    padding: 12px 16px;
    margin-bottom: 12px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-text-primary, #1f2937);
  }
  .onboarding-banner a {
    color: var(--color-ielts, #2c5f8a);
    text-decoration: underline;
  }
  .onboarding-link {
    background: none;
    border: none;
    color: var(--color-ielts, #2c5f8a);
    text-decoration: underline;
    cursor: pointer;
    padding: 0;
    font-size: inherit;
  }
</style>
