<script>
  import { isLogin, isSignUpPage, accessToken, userEmail } from '../lib/store.js';
  import Dropdown from './Dropdown.svelte';
  import { Info, User, Key, LogOut } from 'lucide-svelte';

  export let onInfoClick = () => {};
  export let onManageKeyClick = () => {};

  const models = ['IELTS Feedback Writer'];
  let selectedModel = models[0];

  function goToSignUp() {
    $isSignUpPage = true;
    window.location.hash = '#/authorize';
  }

  function goToLogin() {
    $isSignUpPage = false;
    window.location.hash = '#/authorize';
  }

  function handleLogOut() {
    $accessToken = '';
    $isLogin = false;
    $userEmail = '';
    window.location.reload();
  }
</script>

<div class="top-bar">
  <div class="d-flex align-items-start gap-2 position-relative">
    <!-- Model selector dropdown -->
    <Dropdown>
      <svelte:fragment slot="trigger" let:toggle>
        <button
          type="button"
          aria-haspopup="menu"
          aria-expanded="false"
          class="d-flex align-items-center gap-1 py-2 fw-semibold text-secondary border-0 bg-white hover-bg-lightgray"
          on:click={toggle}
          style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
        >
          <div class="hover-bg-lightgray active-bg-lightgray">{selectedModel}</div>
          <i class="fas fa-chevron-down"></i>
        </button>
      </svelte:fragment>
      <svelte:fragment slot="menu" let:close>
        {#each models as model}
          <button
            class="dropdown-item w-100 text-start py-2 px-3"
            on:click={() => {
              selectedModel = model;
              close();
            }}
          >
            <div class="hover-bg-lightgray active-bg-lightgray">{model}</div>
          </button>
        {/each}
      </svelte:fragment>
    </Dropdown>

    <!-- Info desk button -->
    <button
      class="d-flex align-items-center gap-1 py-2 px-3 fw-semibold text-secondary border-0 bg-white"
      on:click={onInfoClick}
    >
      <Info class="w-4 h-4 mr-1" />
      Info
    </button>
  </div>

  {#if $isLogin == false}
    <div style="justify-content: end;">
      <button class="btn relative btn-primary btn-small mr-6" on:click|preventDefault={goToLogin}>
        <div class="flex items-center justify-center">Log In</div>
      </button>
      <button class="btn relative btn-secondary btn-small" on:click|preventDefault={goToSignUp}>
        <div class="flex items-center justify-center">Sign Up</div>
      </button>
    </div>
  {:else}
    <!-- User profile dropdown -->
    <div class="d-flex align-items-start gap-2 position-relative">
      <Dropdown align="right">
        <svelte:fragment slot="trigger" let:toggle>
          <button
            type="button"
            aria-haspopup="true"
            aria-expanded="false"
            class="d-flex align-items-center gap-1 py-2 fw-semibold text-secondary border-0 bg-white hover-bg-lightgray"
            on:click={toggle}
            style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
          >
            <span class="sr-only">User Profile</span>
            <User class="h-4 w-4" />
          </button>
        </svelte:fragment>
        <svelte:fragment slot="menu" let:close>
          <button
            class="dropdown-item w-100 text-start py-2 px-3"
            on:click={() => {
              onManageKeyClick();
              close();
            }}
          >
            <div class="hover-bg-lightgray active-bg-lightgray" style="border-radius: 5px;">
              <Key class="h-4 w-4 mr-3 text-gray-500" />
              Manage API key
            </div>
          </button>
          <button
            class="dropdown-item w-100 text-start py-2 px-3"
            on:click={() => {
              handleLogOut();
              close();
            }}
          >
            <div class="hover-bg-lightgray active-bg-lightgray" style="border-radius: 5px;">
              <LogOut class="h-4 w-4 mr-3 text-gray-500" />
              Log out
            </div>
          </button>
        </svelte:fragment>
      </Dropdown>
    </div>
  {/if}
</div>
