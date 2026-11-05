import type { ApiResult } from '../lib/types/api-result';
import type { Success } from '../lib/types/success';

export function isSuccess<R extends ApiResult>(
  result: R,
): result is Success<R> {
  return result.error === undefined;
}
