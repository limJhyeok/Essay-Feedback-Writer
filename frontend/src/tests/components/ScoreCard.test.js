import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import ScoreCard from '../../components/ScoreCard.svelte';

const feedback = {
  overall_score: 7.5,
  feedback_by_criteria: {
    taskResponse: { score: 8 },
    coherenceCohesion: { score: 5 },
  },
};

const criteriaLabels = {
  taskResponse: 'Task Response',
  coherenceCohesion: 'Coherence & Cohesion',
};

describe('ScoreCard component', () => {
  it('renders nothing when feedback is null', () => {
    const { container } = render(ScoreCard, { props: { feedback: null } });
    expect(container.querySelector('.score-card')).toBeNull();
  });

  it('renders overall score value', () => {
    const { getByText } = render(ScoreCard, {
      props: { feedback, criteriaLabels, maxScore: 9 },
    });
    expect(getByText('7.5')).toBeInTheDocument();
  });

  it('renders band label for IELTS (maxScore=9)', () => {
    const { getByText } = render(ScoreCard, {
      props: { feedback, criteriaLabels, maxScore: 9 },
    });
    // 7.5 >= 7.5 -> 'Very Good'
    expect(getByText('Very Good')).toBeInTheDocument();
  });

  it('does not render band label when maxScore is not 9', () => {
    const { container } = render(ScoreCard, {
      props: { feedback, criteriaLabels, maxScore: 60 },
    });
    expect(container.querySelector('.band-label')).toBeNull();
  });

  it('renders per-criteria scores with mapped labels', () => {
    const { getByText } = render(ScoreCard, {
      props: { feedback, criteriaLabels, maxScore: 9 },
    });
    expect(getByText('Task Response')).toBeInTheDocument();
    expect(getByText('Coherence & Cohesion')).toBeInTheDocument();
    expect(getByText('8')).toBeInTheDocument();
    expect(getByText('5')).toBeInTheDocument();
  });

  it('falls back to criterion key when label not provided', () => {
    const { getByText } = render(ScoreCard, {
      props: { feedback, criteriaLabels: {}, maxScore: 9 },
    });
    expect(getByText('taskResponse')).toBeInTheDocument();
    expect(getByText('coherenceCohesion')).toBeInTheDocument();
  });
});
