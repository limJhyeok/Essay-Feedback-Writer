import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock import.meta.env before importing api
vi.stubEnv('VITE_SERVER_URL', 'http://localhost:8000');

// Mock svelte-spa-router
const mockPush = vi.fn();
vi.mock('svelte-spa-router', () => ({
  push: mockPush,
}));

// Mock stores
const mockAccessTokenValue = { value: '' };
const mockUserEmailValue = { value: '' };
const mockIsLoginValue = { value: false };

const makeStoreMock = (holder) => ({
  subscribe: vi.fn(),
  set: vi.fn((val) => { holder.value = val; }),
});

const mockAccessToken = makeStoreMock(mockAccessTokenValue);
const mockUserEmail = makeStoreMock(mockUserEmailValue);
const mockIsLogin = makeStoreMock(mockIsLoginValue);

vi.mock('../../lib/store', () => ({
  accessToken: mockAccessToken,
  userEmail: mockUserEmail,
  isLogin: mockIsLogin,
}));

// Mock svelte/store get
vi.mock('svelte/store', () => ({
  get: vi.fn((store) => {
    if (store === mockAccessToken) return mockAccessTokenValue.value;
    if (store === mockUserEmail) return mockUserEmailValue.value;
    if (store === mockIsLogin) return mockIsLoginValue.value;
    return undefined;
  }),
  writable: vi.fn(),
}));

// Import after mocks
const { default: fastapi, fastapiUpload } = await import('../../lib/api.js');

describe('fastapi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAccessTokenValue.value = '';
    global.fetch = vi.fn();
    global.alert = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('GET: constructs URL with query params and calls success callback with parsed JSON', async () => {
    const responseData = { id: 1, title: 'test' };
    global.fetch.mockResolvedValueOnce({
      status: 200,
      json: vi.fn().mockResolvedValueOnce(responseData),
    });

    const successCb = vi.fn();
    fastapi('get', '/api/v1/essays', { page: 1, size: 10 }, successCb, null);

    await vi.waitFor(() => expect(successCb).toHaveBeenCalledWith(responseData));

    const [calledUrl] = global.fetch.mock.calls[0];
    expect(calledUrl).toContain('http://localhost:8000/api/v1/essays');
    expect(calledUrl).toContain('page=1');
    expect(calledUrl).toContain('size=10');
  });

  it('POST: sends JSON body with correct Content-Type and calls success callback', async () => {
    const responseData = { id: 2 };
    global.fetch.mockResolvedValueOnce({
      status: 201,
      json: vi.fn().mockResolvedValueOnce(responseData),
    });

    const successCb = vi.fn();
    const body = { title: 'My Essay', content: 'Hello world' };
    fastapi('post', '/api/v1/essays', body, successCb, null);

    await vi.waitFor(() => expect(successCb).toHaveBeenCalledWith(responseData));

    const [, options] = global.fetch.mock.calls[0];
    expect(options.method).toBe('post');
    expect(options.headers['Content-Type']).toBe('application/json');
    expect(options.body).toBe(JSON.stringify(body));
  });

  it('login: sends form-urlencoded body', async () => {
    const responseData = { access_token: 'tok123' };
    global.fetch.mockResolvedValueOnce({
      status: 200,
      json: vi.fn().mockResolvedValueOnce(responseData),
    });

    const successCb = vi.fn();
    fastapi('login', '/api/v1/login/access-token', { username: 'u', password: 'p' }, successCb, null);

    await vi.waitFor(() => expect(successCb).toHaveBeenCalledWith(responseData));

    const [, options] = global.fetch.mock.calls[0];
    expect(options.method).toBe('post');
    expect(options.headers['Content-Type']).toBe('application/x-www-form-urlencoded');
    expect(options.body).toContain('username=u');
    expect(options.body).toContain('password=p');
  });

  it('204: calls success callback with no arguments', async () => {
    global.fetch.mockResolvedValueOnce({
      status: 204,
      json: vi.fn(),
    });

    const successCb = vi.fn();
    fastapi('delete', '/api/v1/essays/1', {}, successCb, null);

    await vi.waitFor(() => expect(successCb).toHaveBeenCalledWith());
    expect(successCb).toHaveBeenCalledTimes(1);
  });

  it('401 (non-login): clears auth stores and redirects to /authorize', async () => {
    global.fetch.mockResolvedValueOnce({
      status: 401,
      json: vi.fn().mockResolvedValueOnce({ detail: 'Unauthorized' }),
    });

    fastapi('get', '/api/v1/me', {}, null, null);

    await vi.waitFor(() => expect(mockPush).toHaveBeenCalledWith('/authorize'));
    expect(mockAccessToken.set).toHaveBeenCalledWith('');
    expect(mockUserEmail.set).toHaveBeenCalledWith('');
    expect(mockIsLogin.set).toHaveBeenCalledWith(false);
  });

  it('error (4xx/5xx): calls failure callback with error JSON', async () => {
    const errorData = { detail: 'Bad Request' };
    global.fetch.mockResolvedValueOnce({
      status: 400,
      json: vi.fn().mockResolvedValueOnce(errorData),
    });

    const failureCb = vi.fn();
    fastapi('post', '/api/v1/essays', {}, null, failureCb);

    await vi.waitFor(() => expect(failureCb).toHaveBeenCalledWith(errorData));
  });

  it('network error: calls failure callback with network error message object', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Failed to fetch'));

    const failureCb = vi.fn();
    fastapi('get', '/api/v1/essays', {}, null, failureCb);

    await vi.waitFor(() => expect(failureCb).toHaveBeenCalled());
    const [arg] = failureCb.mock.calls[0];
    expect(arg).toHaveProperty('detail');
    expect(arg.detail).toContain('Network error');
  });

  it('Authorization header: included when accessToken is non-empty', async () => {
    mockAccessTokenValue.value = 'mytoken123';
    global.fetch.mockResolvedValueOnce({
      status: 200,
      json: vi.fn().mockResolvedValueOnce({}),
    });

    fastapi('get', '/api/v1/essays', {}, vi.fn(), null);

    await vi.waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe('Bearer mytoken123');
  });

  it('Authorization header: omitted when accessToken is empty', async () => {
    mockAccessTokenValue.value = '';
    global.fetch.mockResolvedValueOnce({
      status: 200,
      json: vi.fn().mockResolvedValueOnce({}),
    });

    fastapi('get', '/api/v1/essays', {}, vi.fn(), null);

    await vi.waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBeUndefined();
  });
});

describe('fastapiUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAccessTokenValue.value = '';
    global.fetch = vi.fn();
    global.alert = vi.fn();
  });

  it('sends FormData without Content-Type header and handles response', async () => {
    const responseData = { id: 5 };
    global.fetch.mockResolvedValueOnce({
      status: 200,
      json: vi.fn().mockResolvedValueOnce(responseData),
    });

    const formData = new FormData();
    formData.append('file', new Blob(['img'], { type: 'image/png' }), 'test.png');

    const successCb = vi.fn();
    fastapiUpload('/api/v1/essays/handwriting', formData, successCb, null);

    await vi.waitFor(() => expect(successCb).toHaveBeenCalledWith(responseData));

    const [, options] = global.fetch.mock.calls[0];
    expect(options.method).toBe('post');
    expect(options.headers['Content-Type']).toBeUndefined();
    expect(options.body).toBe(formData);
  });

  it('network error: calls failure callback with network error message object', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Failed to fetch'));

    const failureCb = vi.fn();
    fastapiUpload('/api/v1/essays/handwriting', new FormData(), null, failureCb);

    await vi.waitFor(() => expect(failureCb).toHaveBeenCalled());
    const [arg] = failureCb.mock.calls[0];
    expect(arg).toHaveProperty('detail');
    expect(arg.detail).toContain('Network error');
  });
});
