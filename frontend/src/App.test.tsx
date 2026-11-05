import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { createFakeBackend, makeItem } from '../test/fakeBackend';
import { renderWithApi } from '../test/renderWithApi';
import App from './App';

describe('App', () => {
  it('shows API health and the first page of items', async () => {
    const backend = createFakeBackend([makeItem(1)]);
    renderWithApi(<App />, backend.fetch);

    expect(await screen.findByText('API ok · v1.2.3')).toBeDefined();
    expect(await screen.findByText('Item 1')).toBeDefined();
  });

  it('reports when the API is unreachable', async () => {
    const backend = createFakeBackend();
    backend.override('GET /api/health', async () =>
      backend.errorResponse(503, 'Unavailable'),
    );
    renderWithApi(<App />, backend.fetch);

    expect(await screen.findByText('API unreachable')).toBeDefined();
  });
});
