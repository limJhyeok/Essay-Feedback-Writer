<script>
  export let AIModelProviders = [];
  export let selectedAIModelProvider = null;
  export let feedbackModels = [];
  export let selectedFeedbackModel = null;
</script>

<div class="model-selector">
  <span>AI Provider:</span>
  <select bind:value={selectedAIModelProvider} class="model-dropdown">
    {#each AIModelProviders as provider}
      <option value={provider}>{provider.name}</option>
    {/each}
  </select>

  <span>AI Model:</span>
  <select bind:value={selectedFeedbackModel} class="model-dropdown">
    {#each feedbackModels as feedbackModel}
      <option value={feedbackModel}>{feedbackModel.alias}</option>
    {/each}
  </select>
</div>

<style>
  .model-selector {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .model-dropdown {
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
  }
</style>
