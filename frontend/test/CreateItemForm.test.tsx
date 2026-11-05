import { fireEvent, screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { CreateItemForm } from '../src/lib/components/CreateItemForm';
import { createFakeBackend } from './fakeBackend';
import { renderWithApi } from './renderWithApi';

function fillAndSubmit(name: string, description = '') {
  fireEvent.change(screen.getByLabelText('Name'), {
    target: { value: name },
  });
  fireEvent.change(screen.getByLabelText('Description'), {
    target: { value: description },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Add item' }));
}

describe('CreateItemForm', () => {
  it('posts the item and clears the form', async () => {
    const backend = createFakeBackend();
    renderWithApi(<CreateItemForm />, backend.fetch);

    fillAndSubmit('Gear', 'Small');

    await waitFor(() =>
      expect(screen.getByLabelText<HTMLInputElement>('Name').value).toBe(''),
    );
    const [request] = backend.requests;
    expect(request.method).toBe('POST');
    expect(await request.json()).toEqual({
      name: 'Gear',
      description: 'Small',
    });
  });

  it('sends a null description when left blank', async () => {
    const backend = createFakeBackend();
    renderWithApi(<CreateItemForm />, backend.fetch);

    fillAndSubmit('Gear');

    await waitFor(() => expect(backend.requests).toHaveLength(1));
    expect(await backend.requests[0].json()).toEqual({
      name: 'Gear',
      description: null,
    });
  });

  it('shows the backend error message', async () => {
    const backend = createFakeBackend();
    backend.override('POST /api/items', async () =>
      backend.errorResponse(422, 'Request validation failed'),
    );
    renderWithApi(<CreateItemForm />, backend.fetch);

    fillAndSubmit('Gear');

    expect((await screen.findByRole('alert')).textContent).toBe(
      'Request validation failed',
    );
  });
});
