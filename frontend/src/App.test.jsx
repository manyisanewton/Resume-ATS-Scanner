import { render, screen } from '@testing-library/react';

import App from './App';
import { AuthProvider } from './context/AuthContext';

jest.mock('./api/authApi', () => ({
  getCurrentUser: jest.fn(() => Promise.reject(new Error('no session'))),
  login: jest.fn(),
  bootstrapAdmin: jest.fn(),
  createRecruiter: jest.fn(),
}));

describe('App', () => {
  test('renders login form after loading when no session exists', async () => {
    render(
      <AuthProvider>
        <App />
      </AuthProvider>
    );

    expect(await screen.findByText(/Welcome Back/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Sign In/i })).toBeInTheDocument();
  });
});
