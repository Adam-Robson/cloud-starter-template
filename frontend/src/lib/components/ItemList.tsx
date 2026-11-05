import { useState } from 'react';
import { useDeleteItem } from '../../hooks/use-delete-item';
import { useItems } from '../../hooks/use-items';

const PAGE_SIZE = 10;

export function ItemList() {
  const [page, setPage] = useState(1);
  const { data, isPending, isError, error } = useItems(page, PAGE_SIZE);
  const deleteItem = useDeleteItem();

  if (isPending) {
    return <p>Loading items…</p>;
  }
  if (isError) {
    return (
      <p role='alert' className='error'>
        {error.message}
      </p>
    );
  }
  if (data.total === 0) {
    return <p>No items yet.</p>;
  }

  const hasNext = data.page * data.pageSize < data.total;

  return (
    <>
      <ul className='item-list'>
        {data.items.map((item) => (
          <li key={item.id}>
            <div>
              <strong>{item.name}</strong>
              {item.description && <p>{item.description}</p>}
            </div>
            <button
              type='button'
              onClick={() => deleteItem.mutate(item.id)}
              disabled={deleteItem.isPending}
              aria-label={`Delete ${item.name}`}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      <nav className='pager' aria-label='Pagination'>
        <button
          type='button'
          onClick={() => setPage(page - 1)}
          disabled={page === 1}
        >
          Previous
        </button>
        <span>
          Page {data.page} of {Math.ceil(data.total / data.pageSize)}
        </span>
        <button
          type='button'
          onClick={() => setPage(page + 1)}
          disabled={!hasNext}
        >
          Next
        </button>
      </nav>
    </>
  );
}
