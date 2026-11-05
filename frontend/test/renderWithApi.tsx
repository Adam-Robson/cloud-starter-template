import { QueryClient } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';

import { ApiProvider } from '../src/context/api-provider';
import { createApiClient } from '../src/api/create-api-client';

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
