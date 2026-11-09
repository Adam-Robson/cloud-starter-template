/** Mirrors openapi-fetch's result: exactly one of data or error is set. */
export type ApiResult =
  | { data: unknown; error?: never; response: Response }
  | { data?: never; error: object | string; response: Response };
