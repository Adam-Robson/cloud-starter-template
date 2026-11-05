import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useApiClient } from '../context/use-api-client';
import { unwrap } from '../utils/unwrap';

const itemsKey = ['items'] as const;

export function useDeleteItem() {
  const client = useApiClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (itemId: string) =>
      unwrap(
        client.DELETE('/api/items/{item_id}', {
          params: { path: { item_id: itemId } },
        }),
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: itemsKey }),
  });
}
