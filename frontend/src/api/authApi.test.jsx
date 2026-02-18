import { login } from './authApi';

describe('authApi', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('login resolves response body on success', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ access_token: 'abc', user: { id: 1 } }),
    });

    const data = await login({ username: 'admin', password: 'pass' });

    expect(data.access_token).toBe('abc');
  });

  test('login throws server error message on failure', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      status: 401,
      headers: { get: () => 'application/json' },
      json: async () => ({ error: 'invalid username or password' }),
    });

    await expect(login({ username: 'admin', password: 'bad' })).rejects.toThrow(
      'invalid username or password'
    );
  });
});
