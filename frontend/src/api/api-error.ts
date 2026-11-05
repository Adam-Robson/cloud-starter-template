import type { ErrorResponse } from '../lib/types/error-response';
import { isError } from '../utils/is-error';

/**
 * Raised for any non-2xx response. `body` is the backend's ErrorResponse, or
 * undefined when something else (e.g. a proxy) produced the error.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly body: ErrorResponse | undefined;

  constructor(status: number, error: unknown) {
    const body = isError(error) ? error : undefined;
    super(body?.message ?? `Request failed with status ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}
