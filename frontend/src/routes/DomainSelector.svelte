<script>
  import { push } from 'svelte-spa-router';
  import { BookOpen, GraduationCap, Calculator, FlaskConical, ArrowRight } from 'lucide-svelte';

  const domains = [
    {
      id: 'ielts',
      title: 'IELTS Writing',
      subtitle: 'Academic — Task 2',
      description: 'Practice IELTS Writing Task 2 essays with feedback scored against official band descriptors: Task Response, Coherence, Lexical Resource, and Grammar.',
      tags: ['Band 1–9', '4 Criteria', '250+ words', 'English'],
      color: '#2c5f8a',
      colorPale: '#e8f0f8',
      icon: BookOpen,
      enabled: true,
      route: '/ielts',
    },
    {
      id: 'ksat',
      title: '대학별 논술',
      subtitle: 'Korean University Essay Exams',
      description: '대학별 논술 기출문제로 연습하고, 논증 구조·분석력·표현력 등 채점 기준에 맞춘 AI 피드백을 받아보세요.',
      tags: ['서울대', '인하대', '논술형', '한국어'],
      color: '#c44536',
      colorPale: '#fdf0ee',
      icon: GraduationCap,
      enabled: true,
      route: '/ksat',
    },
    {
      id: 'math',
      title: 'Math Problem Solving',
      subtitle: 'SAT · AP · University Entrance',
      description: 'Submit solutions to math problems and receive step-by-step feedback on logical reasoning, calculation accuracy, and proof structure.',
      tags: ['Step-by-step', 'Proof review'],
      color: '#8a8a8a',
      colorPale: '#f5f5f5',
      icon: Calculator,
      enabled: false,
    },
    {
      id: 'science',
      title: 'Science Essays',
      subtitle: 'Lab Reports · Research Writing',
      description: 'Get feedback on scientific writing including hypothesis structure, methodology clarity, data interpretation, and citation practices.',
      tags: ['Lab reports', 'Research'],
      color: '#8a8a8a',
      colorPale: '#f5f5f5',
      icon: FlaskConical,
      enabled: false,
    },
  ];

  function selectDomain(domain) {
    if (domain.enabled && domain.route) {
      push(domain.route);
    }
  }
</script>

<div class="domain-selector">
  <div class="header">
    <div class="header-line"></div>
    <h2 class="header-title">CHOOSE YOUR DOMAIN</h2>
    <div class="header-line"></div>
  </div>

  <div class="domain-grid">
    {#each domains as domain}
      <div
        class="domain-card"
        class:disabled={!domain.enabled}
        class:clickable={domain.enabled}
        style="--accent: {domain.color}; --accent-pale: {domain.colorPale};"
        on:click={() => selectDomain(domain)}
        role="button"
        tabindex={domain.enabled ? 0 : -1}
        on:keydown={(e) => e.key === 'Enter' && selectDomain(domain)}
      >
        {#if !domain.enabled}
          <span class="coming-soon-badge">COMING SOON</span>
        {/if}

        <div class="card-top-border"></div>

        <div class="card-icon">
          <svelte:component this={domain.icon} size={28} strokeWidth={1.5} />
        </div>

        <h3 class="card-title">{domain.title}</h3>
        <p class="card-subtitle">{domain.subtitle}</p>
        <p class="card-description">{domain.description}</p>

        <div class="card-tags">
          {#each domain.tags as tag}
            <span class="tag">{tag}</span>
          {/each}
        </div>

        {#if domain.enabled}
          <button class="card-arrow" aria-label="Go to {domain.title}">
            <ArrowRight size={18} />
          </button>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .domain-selector {
    max-width: 1080px;
    margin: 0 auto;
    padding: 48px 24px;
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
    justify-content: center;
  }

  .header-line {
    height: 1px;
    width: 50px;
    background: #ccc;
  }

  .header-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
    color: #6b7280;
    text-transform: uppercase;
  }

  .domain-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .domain-card {
    position: relative;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 32px;
    transition: all 0.2s ease;
    overflow: hidden;
  }

  .domain-card.clickable {
    cursor: pointer;
  }

  .domain-card.clickable:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  }

  .domain-card.disabled {
    opacity: 0.5;
    cursor: default;
  }

  .card-top-border {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--accent);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .domain-card.clickable:hover .card-top-border {
    opacity: 1;
  }

  .coming-soon-badge {
    position: absolute;
    top: 16px;
    right: 16px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    color: var(--color-text-secondary, #6b7280);
    background: #f3f4f6;
    padding: 4px 10px;
    border-radius: 4px;
  }

  .card-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    background: var(--accent-pale);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
  }

  .card-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 4px 0;
    font-family: 'Playfair Display', 'Noto Serif KR', serif;
  }

  .card-subtitle {
    font-size: 13px;
    color: var(--color-text-secondary, #6b7280);
    margin: 0 0 16px 0;
  }

  .card-description {
    font-size: 14px;
    line-height: 1.6;
    color: #4b5563;
    margin: 0 0 20px 0;
  }

  .card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag {
    font-size: 12px;
    color: #6b7280;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 4px 12px;
    border-radius: 4px;
  }

  .card-arrow {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: var(--accent);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    opacity: 0;
  }

  .domain-card.clickable:hover .card-arrow {
    opacity: 1;
    transform: translateX(2px);
  }

  @media (max-width: 768px) {
    .domain-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
