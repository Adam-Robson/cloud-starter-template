import type { CreateItem } from '../src/lib/types/create-item';
import type { ErrorResponse } from '../src/lib/types/error-response';
import type { Item } from '../src/lib/types/item';

type Handler = (request: Request) => Promise<Response>;

function errorResponse(statusCode: number, message: string): Response {
  const body: ErrorResponse = { statusCode, message, detail: null };
  return Response.json(body, { status: statusCode });
}

/**
 * In-memory stand-in for the backend API, used as the client's `fetch`.
 * `override` lets a test replace one route's response (e.g. to fail it).
 */
export function createFakeBackend(items: Item[] = []) {
  const store = [...items];
  const requests: Request[] = [];
  const overrides = new Map<string, Handler>();

  const route: Handler = async (request) => {
    const { pathname, searchParams } = new URL(request.url);
    const key = `${request.method} ${pathname}`;
    const override = overrides.get(key);
    if (override) {
      return override(request);
    }
    if (key === 'GET /api/health') {
      return Response.json({ status: 'ok', version: '1.2.3' });
    }
    if (key === 'GET /api/items') {
      const page = Number(searchParams.get('page'));
      const pageSize = Number(searchParams.get('pageSize'));
      const start = (page - 1) * pageSize;
      return Response.json({
        items: store.slice(start, start + pageSize),
        total: store.length,
        page,
        pageSize,
      });
    }
    if (key === 'POST /api/items') {
      const body: CreateItem = await request.json();
      const item: Item = {
        id: `item-${store.length + 1}`,
        createdAt: new Date(0).toISOString(),
        ...body,
      };
      store.push(item);
      return Response.json(item, { status: 201 });
    }
    const deleteMatch = /^DELETE \/api\/items\/(.+)$/.exec(key);
    if (deleteMatch) {
      const index = store.findIndex((item) => item.id === deleteMatch[1]);
      if (index === -1) {
        return errorResponse(404, 'Item not found');
      }
      store.splice(index, 1);
      return new Response(null, { status: 204 });
    }
    return errorResponse(404, 'Not Found');
  };

  const fetch: typeof globalThis.fetch = async (input, init) => {
    const request = new Request(input, init);
    requests.push(request.clone());
    return route(request);
  };

  return {
    fetch,
    requests,
    override: (key: string, handler: Handler) => overrides.set(key, handler),
    errorResponse,
  };
}

export function makeItem(index: number): Item {
  return {
    id: `seed-${index}`,
    name: `Item ${index}`,
    description: null,
    createdAt: new Date(0).toISOString(),
  };
}
