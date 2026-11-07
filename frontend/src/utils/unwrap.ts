import { ApiError } from '../api/api-error';
import type { ApiResult } from '../lib/types/api-result';
import type { Success } from '../lib/types/success';
import { isSuccess } from './is-success';

/** Returns the response data, or throws an ApiError on failure. */
export async function unwrap<R extends ApiResult>(
  request: Promise<R>,
): Promise<Success<R>['data']> {
  const result = await request;
  if (!isSuccess(result)) {
    throw new ApiError(result.response.status, result.error);
  }
  return result.data;
}
