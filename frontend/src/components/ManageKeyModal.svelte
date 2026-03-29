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
  export let locale = 'en';

  $: t = locale === 'ko' ? {
    title: 'API 키 관리',
    manage: '관리',
    register: '등록',
    name: '이름',
    provider: '제공자',
    registered: '등록일',
    lastUsed: '마지막 사용',
    status: '상태',
    action: '작업',
    registerNew: '새 API 키 등록',
    secretKey: '비밀 키',
    optional: '(선택사항)',
    cancel: '취소',
    registerKey: '비밀 키 등록',
    noKeys: '등록된 API 키가 없습니다.',
  } : {
    title: 'Manage API key',
    manage: 'Manage',
    register: 'Register',
    name: 'Name',
    provider: 'Provider',
    registered: 'Registered',
    lastUsed: 'Last Used',
    status: 'Status',
    action: 'Action',
    registerNew: 'Register New API Key',
    secretKey: 'Secret Key',
    optional: '(optional)',
    cancel: 'Cancel',
    registerKey: 'Register Secret Key',
    noKeys: 'No API keys registered yet.',
  };

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
  let errorMessage = '';

  $: tabs = [
    { id: 'manage', label: t.manage },
    { id: 'register', label: t.register },
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
      '/api/v1/shared/api_keys',
      {},
      (json) => {
        registeredAPIKeys = json;
      },
      (json_error) => {
        errorMessage = json_error?.detail || 'Failed to fetch API keys.';
      }
    );
  }

  function registerAPIKey() {
    if (!APIKey.trim()) return;
    errorMessage = '';
    fastapi(
      'post',
      '/api/v1/shared/api_keys',
      { provider_name: providerName, name: APIKeyName, api_key: APIKey },
      () => {
        APIKeyName = '';
        APIKey = '';
        activeTab = 'manage';
        getRegisteredAPIKeys();
      },
      (json_error) => {
        errorMessage = json_error?.detail || 'Failed to register API key.';
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
      `/api/v1/shared/api_keys/${apiKey.id}/name`,
      { name: editingNameOfApiKey },
      () => {
        inputElement = null;
        editingNameOfApiKey = '';
        renameActiveIndex = null;
        getRegisteredAPIKeys();
      },
      (json_error) => {
        errorMessage = json_error?.detail || 'Failed to rename API key.';
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
      `/api/v1/shared/api_keys/${activeApiKeyForDeleting.id}`,
      {},
      () => {
        activeApiKeyForDeleting = null;
        checkDeleteModalOpen = false;
        getRegisteredAPIKeys();
      },
      (json_error) => {
        errorMessage = json_error?.detail || 'Failed to delete API key.';
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

<Modal {open} title={t.title} {onClose}>
  <svelte:fragment slot="icon">
    <Key class="w-4 h-4 mx-2" />
  </svelte:fragment>

  <TabBar {tabs} activeTab={activeTab} onTabChange={setTab} />

  {#if errorMessage}
    <div class="alert alert-danger d-flex align-items-center justify-content-between mt-2 mx-3" role="alert">
      <span>{errorMessage}</span>
      <button type="button" class="btn-close btn-sm" on:click={() => (errorMessage = '')} aria-label="Close"></button>
    </div>
  {/if}

  {#if activeTab === 'manage'}
    <div class="table-responsive mt-3">
      <table class="table table-hover align-middle">
        <thead class="table-light">
          <tr class="text-center">
            <th>{t.name}</th>
            <th>{t.provider}</th>
            <th>{t.registered}</th>
            <th>{t.lastUsed}</th>
            <th>{t.status}</th>
            <th class="text-center">{t.action}</th>
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
        <div class="text-muted text-center py-4">{t.noKeys}</div>
      {/if}
    </div>
  {:else if activeTab === 'register'}
    <div class="p-3">
      <h5 class="mb-3 fw-bold">{t.registerNew}</h5>

      <div class="mb-3">
        <label class="form-label">{t.provider}</label>
        <select bind:value={providerName} class="form-select">
          {#each providerNameList as _provider_name}
            <option>{_provider_name}</option>
          {/each}
        </select>
      </div>

      <div class="mb-2 d-flex align-items-center">
        <label class="me-2 mb-0">{t.name}</label>
        <span class="text-muted small">{t.optional}</span>
      </div>
      <input
        bind:value={APIKeyName}
        class="form-control mb-3"
        placeholder="My Test Key"
        type="text"
      />

      <label class="form-label">{t.secretKey}</label>
      <input
        bind:value={APIKey}
        class="form-control mb-2"
        placeholder="sk-...eGNK"
        type="password"
        required
      />

      <div class="d-flex justify-content-end gap-2 pt-3">
        <button class="btn btn-secondary" on:click={onClose}>{t.cancel}</button>
        <button class="btn btn-primary" on:click={registerAPIKey} disabled={!APIKey.trim()}>
          {t.registerKey}
        </button>
      </div>
    </div>
  {/if}
</Modal>
