<script>
  export let feedback = null;
  export let criteriaLabels = {};
  export let maxScore = 9;

  function getScoreColor(score, max) {
    if (score == null || max == null) return 'var(--color-text-secondary, #6b7280)';
    const ratio = score / max;
    if (ratio >= 0.75) return 'var(--color-score-high, #16a34a)';
    if (ratio >= 0.5) return 'var(--color-score-mid, #ca8a04)';
    return 'var(--color-score-low, #dc2626)';
  }

  function getScorePercent(score, max) {
    if (score == null || max == null) return 0;
    return Math.min(100, Math.max(0, (score / max) * 100));
  }

  function getBandLabel(score) {
    if (score == null) return '';
    const s = Number(score);
    if (maxScore === 9) {
      // IELTS band descriptors
      if (s >= 8.5) return 'Expert';
      if (s >= 7.5) return 'Very Good';
      if (s >= 6.5) return 'Competent';
      if (s >= 5.5) return 'Modest';
      if (s >= 4.5) return 'Limited';
      return 'Below Average';
    }
    return '';
  }
</script>

{#if feedback}
  <div class="score-card">
    <div class="overall-score">
      <div class="score-label">Overall Score</div>
      <div class="score-value" style="color: {getScoreColor(feedback?.overall_score, maxScore)}">
        {feedback?.overall_score ?? 'N/A'}
      </div>
      {#if getBandLabel(feedback?.overall_score)}
        <div class="band-label">{getBandLabel(feedback?.overall_score)}</div>
      {/if}
      <div class="score-bar-container">
        <div
          class="score-bar"
          style="width: {getScorePercent(feedback?.overall_score, maxScore)}%; background: {getScoreColor(feedback?.overall_score, maxScore)};"
        ></div>
      </div>
    </div>

    <div class="score-details">
      {#each Object.entries(feedback?.feedback_by_criteria ?? {}) as [key, { score }]}
        <div class="score-item">
          <div class="score-label">{criteriaLabels[key] ?? key}</div>
          <div class="score-value-sm" style="color: {getScoreColor(score, maxScore)}">
            {score ?? 'N/A'}
          </div>
          <div class="score-bar-container small">
            <div
              class="score-bar"
              style="width: {getScorePercent(score, maxScore)}%; background: {getScoreColor(score, maxScore)};"
            ></div>
          </div>
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
    border-radius: var(--radius-md, 8px);
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.1));
  }
  .overall-score {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-right: 1px solid #eee;
    padding-right: 20px;
    min-width: 100px;
  }
  .score-label {
    font-size: 14px;
    color: var(--color-text-secondary, #6b7280);
  }
  .score-value {
    font-size: 32px;
    font-weight: bold;
  }
  .score-value-sm {
    font-size: 22px;
    font-weight: bold;
  }
  .band-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--color-text-secondary, #6b7280);
    margin-top: 2px;
  }
  .score-bar-container {
    width: 100%;
    height: 4px;
    background: var(--color-border-light, #f3f4f6);
    border-radius: 2px;
    margin-top: 6px;
    overflow: hidden;
  }
  .score-bar-container.small {
    height: 3px;
    margin-top: 4px;
  }
  .score-bar {
    height: 100%;
    border-radius: 2px;
    transition: width 0.4s ease;
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
    min-width: 80px;
  }
</style>
