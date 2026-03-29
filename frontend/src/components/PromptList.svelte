<script>
  export let prompts = [];
  export let activePromptContent = '';
  export let onSelectPrompt = () => {};
</script>

<div class="p-4 mt-2" style="background-color: #f9f9f9;">
  <h3 class="font-bold mb-4">Select a Prompt</h3>
  <div class="space-y-4">
    {#each prompts as p, index}
      <div
        key={index}
        class="prompt-item rounded p-4 mb-4"
        class:active={activePromptContent === p.content}
        style="cursor: pointer; box-shadow: var(--shadow-sm);"
        role="button"
        tabindex="0"
        on:click={() => onSelectPrompt(p)}
        on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), onSelectPrompt(p))}
      >
        {p.content}
      </div>
    {/each}
  </div>
</div>

<style>
  .prompt-item {
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 4px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .prompt-item:hover {
    background-color: #eef2f7;
  }
  .prompt-item.active {
    background-color: #e1ebf5;
    border-left: 3px solid var(--color-ielts, #2c5f8a);
  }
</style>
