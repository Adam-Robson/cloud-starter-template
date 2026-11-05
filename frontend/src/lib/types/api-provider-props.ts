import type { QueryClient } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import type { ApiClient } from './api-client';
/**
 * Props for the ApiProvider component, including the
 * API client, query client, and children.
 */
export interface ApiProviderProps {
  client: ApiClient;
  queryClient: QueryClient;
  children: ReactNode;
}
