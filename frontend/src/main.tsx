import { QueryClient } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { ApiProvider } from './api/ApiProvider';
import { createApiClient } from './api/client';
import './index.css';

const root = document.getElementById('root');
if (root === null) {
  throw new Error('index.html is missing the #root element');
}

createRoot(root).render(
  <StrictMode>
    <ApiProvider client={createApiClient()} queryClient={new QueryClient()}>
      <App />
    </ApiProvider>
  </StrictMode>,
);
