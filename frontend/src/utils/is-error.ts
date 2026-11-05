import type { ErrorResponse } from '../lib/types/error-response';

export function isError(value: unknown): value is ErrorResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'statusCode' in value &&
    'message' in value
  );
}
