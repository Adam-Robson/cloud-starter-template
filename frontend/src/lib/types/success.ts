import type { ApiResult } from './api-result';
/**
 * Represents the successful result of an API call, where the error is not set.
 */
export type Success<R extends ApiResult> = Extract<R, { error?: never }>;
