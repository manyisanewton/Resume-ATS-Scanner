import { fireEvent, render, screen } from '@testing-library/react';

import AuthPage from './AuthPage';

describe('AuthPage', () => {
  test('switches between login and bootstrap modes', () => {
    render(
      <AuthPage onLogin={jest.fn()} onBootstrap={jest.fn()} loading={false} />
    );

    expect(screen.getByRole('heading', { name: /Sign In/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Register/i }));
    expect(screen.getByRole('heading', { name: /Register/i })).toBeInTheDocument();
  });
});
