import { fireEvent, screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ItemList } from '../src/lib/components/ItemList';
import { createFakeBackend, makeItem } from './fakeBackend';
import { renderWithApi } from './renderWithApi';

const seed = (count: number) =>
  Array.from({ length: count }, (_, i) => makeItem(i + 1));

describe('ItemList', () => {
  it('shows an empty state', async () => {
    renderWithApi(<ItemList />, createFakeBackend().fetch);
    expect(await screen.findByText('No items yet.')).toBeDefined();
  });

  it('pages through items with camelCase query params', async () => {
    const backend = createFakeBackend(seed(12));
    renderWithApi(<ItemList />, backend.fetch);

    expect(await screen.findByText('Page 1 of 2')).toBeDefined();
    expect(
      screen.getByRole<HTMLButtonElement>('button', { name: 'Previous' })
        .disabled,
    ).toBe(true);

    fireEvent.click(screen.getByRole('button', { name: 'Next' }));

    expect(await screen.findByText('Item 11')).toBeDefined();
    const lastUrl = new URL(backend.requests.at(-1)?.url ?? '');
    expect(lastUrl.searchParams.get('pageSize')).toBe('10');
    expect(lastUrl.searchParams.get('page')).toBe('2');
  });

  it('deletes an item and refreshes the list', async () => {
    const backend = createFakeBackend(seed(2));
    renderWithApi(<ItemList />, backend.fetch);

    fireEvent.click(
      await screen.findByRole('button', { name: 'Delete Item 1' }),
    );

    await waitFor(() => expect(screen.queryByText('Item 1')).toBeNull());
    expect(screen.getByText('Item 2')).toBeDefined();
  });

  it('shows the backend error message when loading fails', async () => {
    const backend = createFakeBackend();
    backend.override('GET /api/items', async () =>
      backend.errorResponse(500, 'Database offline'),
    );
    renderWithApi(<ItemList />, backend.fetch);

    expect((await screen.findByRole('alert')).textContent).toBe(
      'Database offline',
    );
  });
});
