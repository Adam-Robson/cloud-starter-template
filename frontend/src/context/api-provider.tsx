import { QueryClientProvider } from '@tanstack/react-query';
import type { ApiProviderProps } from '../types/api-provider-props';
import { ApiContext } from './use-api-client';
  
/** Supplies the API client and query cache; inject fakes in tests. */
export function ApiProvider({
  client,
  queryClient,
  children,
}: ApiProviderProps) {
  return (
    <ApiContext value={client}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ApiContext>
  );
}
