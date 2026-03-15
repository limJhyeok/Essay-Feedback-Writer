<script>
  import Modal from './Modal.svelte';
  import { Trash2 } from 'lucide-svelte';

  export let open = false;
  export let itemName = '';
  export let onConfirm = () => {};
  export let onCancel = () => {};
</script>

<Modal {open} title="Delete API key" size="md" onClose={onCancel}>
  <svelte:fragment slot="icon">
    <Trash2 class="h-4 w-4" />
  </svelte:fragment>

  <h5>Are you sure you want to delete
    <strong>{itemName}</strong>
    ? This action cannot be undone.</h5>

  <svelte:fragment slot="footer">
    <button type="button" class="btn btn-secondary" on:click={onCancel}>Cancel</button>
    <button type="button" class="btn btn-danger" on:click={onConfirm}>Yes, Delete</button>
  </svelte:fragment>
</Modal>
