<script>
  export let feedback = null;
  export let criteriaLabels = {};
</script>

{#if feedback}
  <div class="score-card">
    <div class="overall-score">
      <div class="score-label">Overall Score</div>
      <div class="score-value">{feedback?.overall_score ?? 'N/A'}</div>
    </div>

    <div class="score-details">
      {#each Object.entries(feedback?.feedback_by_criteria ?? {}) as [key, { score }]}
        <div class="score-item">
          <div class="score-label">{criteriaLabels[key] ?? key}</div>
          <div class="score-value">{score ?? 'N/A'}</div>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .score-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  .overall-score {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-right: 1px solid #eee;
    padding-right: 20px;
  }
  .score-label {
    font-size: 14px;
    color: #7f8c8d;
  }
  .score-value {
    font-size: 32px;
    font-weight: bold;
    color: #2c3e50;
  }
  .score-details {
    display: flex;
    flex: 1;
    justify-content: space-around;
  }
  .score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
</style>
