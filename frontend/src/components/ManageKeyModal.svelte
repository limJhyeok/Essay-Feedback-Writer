<script>
  import { tick } from 'svelte';
  import Modal from './Modal.svelte';
  import TabBar from './TabBar.svelte';
  import DeleteConfirmModal from './DeleteConfirmModal.svelte';
  import { Key, SquarePen, Trash2 } from 'lucide-svelte';
  import fastapi from '../lib/api.js';

  export let open = false;
  export let onClose = () => {};
  export let AIModelProviders = [];

  $: providerNameList = AIModelProviders.map((p) => p.name);

  let activeTab = 'manage';
  let registeredAPIKeys = [];
  let APIKey = '';
  let APIKeyName = '';
  let providerName = '';

  $: if (AIModelProviders.length > 0 && !providerName) {
    providerName = AIModelProviders[0].name;
  }

  let activeApiKeyForDeleting = null;
  let checkDeleteModalOpen = false;
  let renameActiveIndex = null;
  let inputElement = null;
  let editingNameOfApiKey = '';

  const tabs = [
    { id: 'manage', label: 'Manage' },
    { id: 'register', label: 'Register' },
  ];

  function setTab(id) {
    activeTab = id;
    if (id === 'manage') {
      getRegisteredAPIKeys();
    }
  }

  function getRegisteredAPIKeys() {
    fastapi(
      'get',
      '/api/v1/ielts/api_keys',
      {},
      (json) => {
        registeredAPIKeys = json;
      },
      (json_error) => {
        console.error('Error fetching API keys:', json_error);
      }
    );
  }

  function registerAPIKey() {
    if (!APIKey.trim()) return;
    fastapi(
      'post',
      '/api/v1/ielts/api_keys',
      { provider_name: providerName, name: APIKeyName, api_key: APIKey },
      () => {
        APIKeyName = '';
        APIKey = '';
      },
      (json_error) => {
        console.error('Error registering API key:', json_error);
      }
    );
  }

  function handleRenameApiKeyButton(index) {
    renameActiveIndex = index;
    tick().then(() => {
      if (inputElement) inputElement.focus();
    });
  }

  function handleRenameKeyPress(event, apiKey) {
    if (event.key === 'Enter') {
      renameApiKey(apiKey);
      cancelEdit();
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }

  function renameApiKey(apiKey) {
    if (editingNameOfApiKey.trim() === '' || editingNameOfApiKey === apiKey.name) return;
    fastapi(
      'put',
      `/api/v1/ielts/api_keys/${apiKey.id}/name`,
      { name: editingNameOfApiKey },
      () => {
        inputElement = null;
        editingNameOfApiKey = '';
        renameActiveIndex = null;
        getRegisteredAPIKeys();
      },
      (json_error) => {
        console.error('Error updating API key name:', json_error);
      }
    );
  }

  function cancelEdit() {
    inputElement = null;
    renameActiveIndex = null;
    editingNameOfApiKey = '';
  }

  function openDeleteModal(apiKey) {
    checkDeleteModalOpen = true;
    activeApiKeyForDeleting = apiKey;
  }

  function confirmDeleteApiKey() {
    fastapi(
      'delete',
      `/api/v1/ielts/api_keys/${activeApiKeyForDeleting.id}`,
      {},
      () => {
        activeApiKeyForDeleting = null;
        checkDeleteModalOpen = false;
        getRegisteredAPIKeys();
      },
      (json_error) => {
        console.error('Error deleting API key:', json_error);
      }
    );
  }

  // Load keys when modal opens
  $: if (open) {
    getRegisteredAPIKeys();
  }
</script>

<DeleteConfirmModal
  open={checkDeleteModalOpen}
  itemName={activeApiKeyForDeleting?.name ?? ''}
  onConfirm={confirmDeleteApiKey}
  onCancel={() => (checkDeleteModalOpen = false)}
/>

<Modal {open} title="Manage API key" {onClose}>
  <svelte:fragment slot="icon">
    <Key class="w-4 h-4 mx-2" />
  </svelte:fragment>

  <TabBar {tabs} activeTab={activeTab} onTabChange={setTab} />

  {#if activeTab === 'manage'}
    <div class="table-responsive mt-3">
      <table class="table table-hover align-middle">
        <thead class="table-light">
          <tr class="text-center">
            <th>Name</th>
            <th>Provider</th>
            <th>Registered</th>
            <th>Last Used</th>
            <th>Status</th>
            <th class="text-center">Action</th>
          </tr>
        </thead>
        <tbody class="text-center">
          {#each registeredAPIKeys as registeredKey, index}
            <tr>
              {#if renameActiveIndex === index}
                <td>
                  <input
                    type="text"
                    class="form-control"
                    bind:this={inputElement}
                    bind:value={editingNameOfApiKey}
                    placeholder={registeredKey.name}
                    on:keydown={(event) => handleRenameKeyPress(event, registeredKey)}
                  />
                </td>
              {:else}
                <td>{registeredKey.name}</td>
              {/if}
              <td>{registeredKey.provider_name}</td>
              <td>{registeredKey.registered_at}</td>
              <td>{registeredKey.last_used || ''}</td>
              <td>{registeredKey.is_active ? 'active' : 'inactive'}</td>
              <td class="text-center">
                <button
                  class="btn btn-sm btn-outline-secondary"
                  on:click={() => handleRenameApiKeyButton(index)}
                  aria-label="Rename API key"
                >
                  <SquarePen class="h-4 w-4" />
                </button>
                <button
                  class="btn btn-sm btn-outline-danger"
                  on:click={() => openDeleteModal(registeredKey)}
                  aria-label="Delete API key"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      {#if registeredAPIKeys.length === 0}
        <div class="text-muted text-center py-4">No API keys registered yet.</div>
      {/if}
    </div>
  {:else if activeTab === 'register'}
    <div class="p-3">
      <h5 class="mb-3 fw-bold">Register New API Key</h5>

      <div class="mb-3">
        <label class="form-label">Provider</label>
        <select bind:value={providerName} class="form-select">
          {#each providerNameList as _provider_name}
            <option>{_provider_name}</option>
          {/each}
        </select>
      </div>

      <div class="mb-2 d-flex align-items-center">
        <label class="me-2 mb-0">Name</label>
        <span class="text-muted small">(optional)</span>
      </div>
      <input
        bind:value={APIKeyName}
        class="form-control mb-3"
        placeholder="My Test Key"
        type="text"
      />

      <label class="form-label">Secret Key</label>
      <input
        bind:value={APIKey}
        class="form-control mb-2"
        placeholder="sk-...eGNK"
        type="password"
        required
      />

      <div class="d-flex justify-content-end gap-2 pt-3">
        <button class="btn btn-secondary" on:click={onClose}>Cancel</button>
        <button class="btn btn-primary" on:click={registerAPIKey} disabled={!APIKey.trim()}>
          Register Secret Key
        </button>
      </div>
    </div>
  {/if}
</Modal>
