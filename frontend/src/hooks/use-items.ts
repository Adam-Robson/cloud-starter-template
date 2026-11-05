import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { useApiClient } from '../context/use-api-client';
import { unwrap } from '../utils/unwrap';

const itemsKey = ['items'] as const;

export function useItems(page: number, pageSize: number) {
  const client = useApiClient();
  return useQuery({
    queryKey: [...itemsKey, { page, pageSize }],
    queryFn: () =>
      unwrap(
        client.GET('/api/items', { params: { query: { page, pageSize } } }),
      ),
    placeholderData: keepPreviousData,
  });
}
