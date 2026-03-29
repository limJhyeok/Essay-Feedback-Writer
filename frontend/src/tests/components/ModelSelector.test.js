import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import ModelSelector from '../../components/ModelSelector.svelte';

const providers = [{ name: 'OpenAI' }, { name: 'Anthropic' }];
const models = [{ alias: 'GPT-4o' }, { alias: 'Claude Sonnet' }];

describe('ModelSelector component', () => {
  it('renders provider options', () => {
    const { getByText, container } = render(ModelSelector, {
      props: { AIModelProviders: providers, feedbackModels: [] },
    });
    expect(getByText('OpenAI')).toBeInTheDocument();
    expect(getByText('Anthropic')).toBeInTheDocument();
    expect(container.querySelectorAll('select').length).toBe(2);
  });

  it('renders feedback model options', () => {
    const { getByText } = render(ModelSelector, {
      props: { AIModelProviders: providers, feedbackModels: models },
    });
    expect(getByText('GPT-4o')).toBeInTheDocument();
    expect(getByText('Claude Sonnet')).toBeInTheDocument();
  });
});
