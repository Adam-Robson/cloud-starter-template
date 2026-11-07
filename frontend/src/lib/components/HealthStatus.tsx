import { useHealth } from '../../hooks/use-health';

export function HealthStatus() {
  const { data, isPending, isError } = useHealth();

  if (isPending) {
    return <span className='status'>Checking API…</span>;
  }
  if (isError) {
    return <span className='status status-down'>API unreachable</span>;
  }
  return (
    <span className='status status-ok'>
      API {data.status} · v{data.version}
    </span>
  );
}
