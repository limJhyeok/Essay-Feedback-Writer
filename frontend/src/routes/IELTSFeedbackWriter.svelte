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

  // Auth check
  function checkAuth() {
    fastapi('get', '/api/v1/user/auth', {}, () => {}, (json_error) => { error = json_error; });
  }
  checkAuth();

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
    fastapi('get', `/api/v1/ielts/api_models/${selectedAIModelProvider.name}`, {},
      (json) => {
        feedbackModels = json;
        if (feedbackModels.length > 0) selectedFeedbackModel = feedbackModels[0];
      },
      (json_error) => { error = json_error; }
    );
  }
  $: selectedAIModelProvider && read_bots();

  function read_providers() {
    fastapi('get', '/api/v1/ielts/providers', {},
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
  $: wordCount = essayContent.replace(/[\t\n\r]/g, '').length;

  // Essay submission
  function submitEssay() {
    fastapi('post', '/api/v1/ielts/essays', { prompt_id: promptId, content: essayContent },
      (json) => {
        editing = false;
        submittedEssayId = json.id;
        submittedEssayContent = json.content;
        getEssaysByPromptId().then(() => {
          mainActiveTab = 'feedback';
          activeIdOfFeedbacks = 0;
          activeIdOfessays = 0;
          generateFeedback();
        }).catch((err) => { error = err; });
      },
      (json_error) => { error = json_error; }
    );
  }

  async function submitHandwritingEssay(canvasComponent) {
    if (!canvasComponent || canvasComponent.isEmpty()) {
      alert('Please write something on the canvas first.');
      return;
    }
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
          generateFeedback();
        }).catch((err) => { error = err; });
      },
      (json_error) => { error = json_error; }
    );
  }

  function generateFeedback() {
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
        getEssaysByPromptId();
        getFeedbacksByEssayId(submittedEssayId);
      },
      (json_error) => {
        if (json_error?.detail) {
          error = json_error.detail;
          alert(`Error: ${error}`);
        } else {
          alert('Unknown error occurred.');
        }
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
      onInfoClick={() => (showInfoDeskModalOpen = true)}
      onManageKeyClick={() => (showManageKeyModalOpen = true)}
    />

    <div class="messages">
      <!-- Main tab bar -->
      <div class="main-tabs flex mb-6" style="border-bottom: 1px solid #ddd;">
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'prompts' ? 'active' : ''}"
          style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
          on:click={() => (mainActiveTab = 'prompts')}
        >
          <Search class="w-4 h-4 mr-2" />
          Prompts
        </button>
        {#if promptContent}
          <button
            class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'write' ? 'active' : ''}"
            style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            on:click={() => (mainActiveTab = 'write')}
          >
            <FileText class="w-4 h-4 mr-2" />
            Write Essay
          </button>
          <button
            class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'example' ? 'active' : ''}"
            style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            on:click={() => (mainActiveTab = 'example')}
          >
            <BookOpen class="w-4 h-4 mr-2" />
            Example
          </button>
          {#if registeredEssayList.length > 0}
            <button
              class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'feedback' ? 'active' : ''}"
              style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
              on:click={() => (mainActiveTab = 'feedback')}
            >
              <BarChart class="w-4 h-4 mr-2" />
              Feedback
            </button>
          {/if}
        {/if}
      </div>

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
          />
        {:else if mainActiveTab === 'feedback'}
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
    background-color: #f9f9f9;
  }
  .main-tabs button:hover {
    background-color: #eef2f7;
  }
  .main-tabs button.active {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
  }
</style>
