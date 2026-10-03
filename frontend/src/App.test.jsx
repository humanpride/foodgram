// src/App.test.jsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import App from './App.jsx';

test('renders element', async () => {
  render(
    <HelmetProvider>
      <MemoryRouter>
        <App />
      </MemoryRouter>
    </HelmetProvider>
  );

  const elements = await screen.findAllByText('Sign Up');

  expect(elements.length).toBeGreaterThan(0);
  expect(elements[0]).toBeInTheDocument();
});
