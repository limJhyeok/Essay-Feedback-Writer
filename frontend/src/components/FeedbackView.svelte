<script>
  import ModelSelector from './ModelSelector.svelte';
  import ScoreCard from './ScoreCard.svelte';
  import { safeHtml } from '../lib/sanitize.js';

  export let registeredEssayList = [];
  export let activeIdOfessays = 0;
  export let feedbackList = [];
  export let activeIdOfFeedbacks = 0;
  export let promptContent = '';
  export let essayContent = '';
  export let editing = false;
  export let onSubmitEssay = () => {};
  export let onEssaySelect = (essay) => {};
  export let onLoadImage = async () => {};
  export let handwritingImageUrl = null;
  export let AIModelProviders = [];
  export let selectedAIModelProvider = null;
  export let feedbackModels = [];
  export let selectedFeedbackModel = null;

  const CRITERIA_LABELS = {
    taskResponse: 'Task Response',
    coherenceCohesion: 'Coherence & Cohesion',
    lexicalResource: 'Lexical Resource',
    grammaticalRange: 'Grammatical Range & Accuracy',
  };
</script>

<!-- Attempt tabs -->
<div class="gap-2 mt-4 px-2" style="display: flex; overflow-x: auto;">
  {#each registeredEssayList as registeredEssay, index}
    <div
      class="attempt-item {index === activeIdOfessays ? 'active' : ''}"
      style="min-width: 15%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
      on:click={() => {
        editing = false;
        activeIdOfessays = index;
        activeIdOfFeedbacks = 0;
        onEssaySelect(registeredEssay);
      }}
    >
      <div>
        <div>Attempt #{registeredEssayList.length - index}</div>
        <div class="attempt-model small text-secondary">Submitted at</div>
        <div class="attempt-model small text-secondary">{registeredEssay['submitted_at']}</div>
      </div>
    </div>
  {/each}
</div>

<!-- Feedback display -->
<div class="feedback-content">
  <div class="prompt-area" style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <strong>Essay Prompt:</strong>
    {promptContent}
  </div>

  {#if editing}
    <textarea
      bind:value={essayContent}
      rows="10"
      class="p-2 border rounded"
      style="width: 100%;"
    ></textarea>
  {:else if registeredEssayList[activeIdOfessays]?.input_type === 'handwriting'}
    {void onLoadImage(registeredEssayList[activeIdOfessays].id) ?? ''}
    <div class="essay-area" style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      {#if handwritingImageUrl}
        <img
          src={handwritingImageUrl}
          alt="Handwritten essay"
          style="max-width:100%; border-radius:4px;"
        />
      {/if}
      {#if registeredEssayList[activeIdOfessays].ocr_text}
        <details style="margin-top:12px;">
          <summary style="cursor:pointer; color:#4a90d9; font-size:14px;">Show OCR transcription</summary>
          <p style="margin-top:8px; padding:8px; background:#f9f9f9; border-radius:4px; white-space:pre-wrap;">{registeredEssayList[activeIdOfessays].ocr_text}</p>
        </details>
      {/if}
    </div>
  {:else}
    <div class="essay-area" style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <p>{registeredEssayList[activeIdOfessays]?.['content'] ?? ''}</p>
    </div>
  {/if}

  <div class="feedback-controls" style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <ModelSelector
      {AIModelProviders}
      bind:selectedAIModelProvider
      {feedbackModels}
      bind:selectedFeedbackModel
    />
    <div class="feedback-actions">
      <button
        class="btn btn-secondary"
        style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);"
        on:click={() => (editing = !editing)}
      >
        {editing ? 'Done Editing' : 'Edit Essay'}
      </button>
      <div class="upload-tooltip">
        <button
          class="btn btn-primary"
          on:click={onSubmitEssay}
          disabled={!essayContent.trim()}
          style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);"
        >
          Submit for Feedback
        </button>
        {#if registeredEssayList[activeIdOfessays]?.['content'] === essayContent}
          <span class="tooltiptext">Same essay — resubmission is OK.</span>
        {/if}
      </div>
    </div>
  </div>

  {#if feedbackList.length > 0}
    <div class="feedback-tabs">
      {#each feedbackList as feedback, index}
        <div
          class="feedback-tab"
          class:active={activeIdOfFeedbacks === index}
          on:click={() => (activeIdOfFeedbacks = index)}
          style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);"
        >
          {feedback.bot_name} ({feedback.created_at})
        </div>
      {/each}
    </div>

    <div class="feedback-content">
      <ScoreCard
        feedback={feedbackList[activeIdOfFeedbacks]['content']}
        criteriaLabels={CRITERIA_LABELS}
      />

      {#each Object.entries(feedbackList[activeIdOfFeedbacks]['content']?.feedback_by_criteria ?? {}) as [key, { score, feedback }]}
        <div class="feedback-section">
          <div class="feedback-heading">
            <i>△</i> feedback for the {CRITERIA_LABELS[key] ?? key}
          </div>
          <ul class="feedback-list">
            <li>{@html safeHtml(feedback ?? '')}</li>
          </ul>
        </div>
      {/each}

      <div class="feedback-section">
        <div class="feedback-heading"><i>△</i> Overall feedback</div>
        <ul class="feedback-list">
          <li>
            {@html safeHtml(feedbackList[activeIdOfFeedbacks]['content']?.overall_feedback ?? '')}
          </li>
        </ul>
      </div>
    </div>
  {/if}
</div>

<style>
  .feedback-content {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
  }
  .prompt-area {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 8px;
    border-left: 3px solid #3498db;
  }
  .essay-area {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    min-height: 200px;
  }
  .feedback-controls {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 8px;
    align-items: center;
  }
  .feedback-actions {
    display: flex;
    gap: 10px;
  }
  .feedback-tabs {
    display: flex;
    border-bottom: 1px solid #ddd;
    margin-bottom: 15px;
    overflow-x: auto;
  }
  .feedback-tab {
    padding: 8px 16px;
    margin-right: 5px;
    cursor: pointer;
    border: 1px solid #ddd;
    border-radius: 4px 4px 0 0;
    white-space: nowrap;
    background-color: #f9f9f9;
  }
  .feedback-tab:hover {
    background-color: #eef2f7;
  }
  .feedback-tab.active {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
  }
  .feedback-section {
    margin-bottom: 20px;
  }
  .feedback-heading {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #2c3e50;
    display: flex;
    align-items: center;
  }
  .feedback-heading i {
    margin-right: 8px;
  }
  .feedback-list {
    padding-left: 25px;
  }
  .feedback-list li {
    margin-bottom: 8px;
  }
  .attempt-item {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 4px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .attempt-item:hover {
    background-color: #eef2f7;
  }
  .attempt-item.active {
    background-color: #e1ebf5;
    border-left: 3px solid #3498db;
  }
</style>
