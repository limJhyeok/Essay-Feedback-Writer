<script>
  import Modal from './Modal.svelte';
  import TabBar from './TabBar.svelte';
  import { Info } from 'lucide-svelte';
  import { safeHtml } from '../lib/sanitize.js';

  export let open = false;
  export let onClose = () => {};
  export let rubricCriteria = [];

  let activeTab = 'rubric';

  const tabs = [
    { id: 'rubric', label: 'Rubric' },
    { id: 'tips', label: 'Tips' },
  ];
</script>

<Modal {open} title="Info" {onClose}>
  <svelte:fragment slot="icon">
    <Info class="w-4 h-4 mx-1" />
  </svelte:fragment>

  <TabBar {tabs} {activeTab} onTabChange={(id) => (activeTab = id)} />

  {#if activeTab === 'rubric'}
    {#each rubricCriteria as criterion}
      <div>
        <h5><strong>Band Score {criterion.score}</strong></h5>
        <p><strong>{criterion.name}:</strong>
          {@html safeHtml(criterion.description)}
        </p>
      </div>
    {/each}
  {:else if activeTab === 'tips'}
    <div>
      <h6><strong>Tips</strong></h6>
      <ul>
        <li>You must write more than 20 words.</li>
        <li>Be specific and avoid generalisations.</li>
        <li>Use formal language — contractions like "don't" should be avoided.</li>
        <li>Check spelling, punctuation, and grammar carefully.</li>
      </ul>
    </div>
  {/if}
</Modal>
