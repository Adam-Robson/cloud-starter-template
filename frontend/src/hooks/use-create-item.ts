import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useApiClient } from '../context/use-api-client';
import { unwrap } from '../utils/unwrap';
import type { CreateItem } from '../lib/types/create-item';

const itemsKey = ['items'] as const;

/**
 * Hook to create a new item.
 * @returns A mutation object for creating a new item.
 */
export function useCreateItem() {
  const client = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateItem) =>
      unwrap(client.POST('/api/items', { body })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: itemsKey }),
  });
}
