import createClient from 'openapi-fetch';
import type { ApiClient } from '../lib/types/api-client';
import type { paths } from './schema';
/**
 * The API is served from the same origin in every environment: the Vite dev
 * server and nginx both proxy `/api` to the backend.
 */
export function createApiClient(
  baseUrl: string = window.location.origin,
  fetch: typeof globalThis.fetch = globalThis.fetch,
): ApiClient {
  return createClient<paths>({ baseUrl, fetch });
}
  