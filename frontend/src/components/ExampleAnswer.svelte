<script>
  import { Copy, Check } from 'lucide-svelte';
  import { safeHtml } from '../lib/sanitize.js';

  export let exampleAnswer = '';

  let copied = false;

  function copyToClipboard() {
    navigator.clipboard
      .writeText(exampleAnswer)
      .then(() => {
        copied = true;
        setTimeout(() => (copied = false), 2000);
      })
      .catch(() => {
        alert('Failed to copy text.');
      });
  }
</script>

<div class="p-4 mt-2" style="background-color: #f9f9f9;">
  <div class="d-flex justify-content-start mb-4">
    <h3 class="font-bold">Example Answer</h3>
    <div class="upload-tooltip">
      <button
        on:click={copyToClipboard}
        class="mx-2 p-2 text-gray-500 hover:text-gray-700 rounded hover:bg-gray-100"
        aria-label="Copy to clipboard"
        style="border: none; background: none; padding: 0;"
      >
        {#if copied}
          <Check size={18} />
        {:else}
          <span class="tooltiptext">Copy</span>
          <Copy size={18} />
        {/if}
      </button>
    </div>
  </div>
  <div
    class="border rounded mx-4 p-4 bg-gray-50 whitespace-pre-line"
    style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
  >
    {@html safeHtml(exampleAnswer)}
  </div>
</div>
