import { CreateItemForm } from './lib/components/CreateItemForm';
import { HealthStatus } from './lib/components/HealthStatus';
import { ItemList } from './lib/components/ItemList';

export default function App() {
  return (
    <main className='app'>
      <header className='app-header'>
        <h1>Cloud Starter</h1>
        <HealthStatus />
      </header>
      <section>
        <h2>Items</h2>
        <CreateItemForm />
        <ItemList />
      </section>
    </main>
  );
}
