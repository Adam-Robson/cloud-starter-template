import { useQuery } from '@tanstack/react-query';

import { useApiClient } from '../context/use-api-client';
import { unwrap } from '../utils/unwrap';

export function useHealth() {
  const client = useApiClient();
  return useQuery({
    queryKey: ['health'],
    queryFn: () => unwrap(client.GET('/api/health')),
  });
}
