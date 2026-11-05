import { QueryClient } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { createApiClient } from '../src/api/create-api-client';
import { ApiProvider } from '../src/context/api-provider';

/** Renders `ui` against the given fetch, with a fresh, non-retrying cache. */
export function renderWithApi(
  ui: ReactElement,
  fetch: typeof globalThis.fetch,
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <ApiProvider
      client={createApiClient('http://api.test', fetch)}
      queryClient={queryClient}
    >
      {ui}
    </ApiProvider>,
  );
}
