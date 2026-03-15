<script>
  import HandwritingCanvas from './HandwritingCanvas.svelte';
  import ModelSelector from './ModelSelector.svelte';

  export let promptContent = '';
  export let essayContent = '';
  export let inputMode = 'text';
  export let wordCount = 0;
  export let onSubmitEssay = () => {};
  export let onSubmitHandwriting = () => {};
  export let AIModelProviders = [];
  export let selectedAIModelProvider = null;
  export let feedbackModels = [];
  export let selectedFeedbackModel = null;

  let canvasComponent;

  export function getCanvasComponent() {
    return canvasComponent;
  }
</script>

<div class="p-4 feedback-content mt-2">
  <div class="mb-4">
    <h3 class="font-semibold">Prompt</h3>
    <div class="prompt-area" style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      {promptContent || 'Please select a prompt from the Prompts tab'}
    </div>
  </div>

  {#if promptContent}
    <div class="mb-4">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <h3 class="font-semibold" style="margin:0;">Your Essay</h3>
        <div style="display:flex; border:1px solid #ccc; border-radius:4px; overflow:hidden; margin-left:8px;">
          <button
            class="mode-toggle-btn"
            class:active={inputMode === 'text'}
            on:click={() => (inputMode = 'text')}
          >Text</button>
          <button
            class="mode-toggle-btn"
            class:active={inputMode === 'handwriting'}
            on:click={() => (inputMode = 'handwriting')}
          >Handwriting</button>
        </div>
      </div>

      {#if inputMode === 'text'}
        <textarea
          bind:value={essayContent}
          placeholder="Write your essay here..."
          class="message-input"
          style="width: 100%; height: 52vh"
        ></textarea>
      {:else}
        <HandwritingCanvas bind:this={canvasComponent} />
      {/if}
    </div>

    <div
      class="d-flex justify-content-between"
      style="padding: 10px; margin-bottom: 10px; background-color: #f5f7fa; border-radius: 8px; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
    >
      <ModelSelector
        {AIModelProviders}
        bind:selectedAIModelProvider
        {feedbackModels}
        bind:selectedFeedbackModel
      />

      <div style="display: flex; gap: 10px;">
        {#if inputMode === 'text'}
          <div class="text-gray-500 text-sm mt-2">Word count: {wordCount}</div>
          <div class="upload-tooltip">
            <button
              class="btn relative btn-primary btn-small"
              on:click={onSubmitEssay}
              disabled={!essayContent.trim()}
              style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            >
              Submit for Feedback
            </button>
            {#if !essayContent.trim()}
              <span class="tooltiptext">Please write your essay</span>
            {/if}
          </div>
        {:else}
          <div class="upload-tooltip">
            <button
              class="btn relative btn-primary btn-small"
              on:click={() => onSubmitHandwriting(canvasComponent)}
              style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            >
              Submit for Feedback
            </button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .feedback-content {
    background-color: white;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  .prompt-area {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 8px;
    border-left: 3px solid #3498db;
  }
  :global(.mode-toggle-btn) {
    padding: 4px 14px;
    font-size: 13px;
    border: none;
    background: #fff;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }
  :global(.mode-toggle-btn:hover) {
    background: #eee;
  }
  :global(.mode-toggle-btn.active) {
    background: #4a90d9;
    color: #fff;
  }
</style>
