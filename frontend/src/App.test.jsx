// src/App.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
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

  await waitFor(() => {
    const element = screen.getByText('Технологии');
    expect(element).toBeInTheDocument();
  });
});
