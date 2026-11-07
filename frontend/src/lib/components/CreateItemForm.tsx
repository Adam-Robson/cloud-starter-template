import { type SubmitEvent, useState } from 'react';

import { useCreateItem } from '../../hooks/use-create-item';

export function CreateItemForm() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const createItem = useCreateItem();

  const handleSubmit = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    createItem.mutate(
      { name, description: description || null },
      {
        onSuccess: () => {
          setName('');
          setDescription('');
        },
      },
    );
  };

  return (
    <form className='create-item' onSubmit={handleSubmit}>
      <input
        aria-label='Name'
        placeholder='Name'
        value={name}
        onChange={(event) => setName(event.target.value)}
        required
      />
      <input
        aria-label='Description'
        placeholder='Description (optional)'
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
      <button type='submit' disabled={createItem.isPending}>
        Add item
      </button>
      {createItem.isError && (
        <p role='alert' className='error'>
          {createItem.error.message}
        </p>
      )}
    </form>
  );
}
