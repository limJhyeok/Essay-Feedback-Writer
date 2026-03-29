<script>
  import { isLogin, isSignUpPage, accessToken, userEmail } from '../lib/store.js';
  import Dropdown from './Dropdown.svelte';
  import { Info, User, Key, LogOut, ArrowLeft } from 'lucide-svelte';

  export let onInfoClick = () => {};
  export let onManageKeyClick = () => {};
  export let domainName = 'IELTS Feedback Writer';
  export let showBackLink = true;
  export let locale = 'en';

  $: t = locale === 'ko' ? {
    info: '안내',
    login: '로그인',
    signup: '회원가입',
    manageKey: 'API 키 관리',
    logout: '로그아웃',
  } : {
    info: 'Info',
    login: 'Log In',
    signup: 'Sign Up',
    manageKey: 'Manage API key',
    logout: 'Log out',
  };

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

  function goToDomains() {
    window.location.hash = '#/';
  }
</script>

<div class="top-bar">
  <div class="d-flex align-items-start gap-2 position-relative">
    {#if showBackLink}
      <button
        type="button"
        class="d-flex align-items-center gap-1 py-2 px-2 fw-semibold text-secondary border-0 bg-white hover-bg-lightgray"
        on:click={goToDomains}
        style="white-space: nowrap;"
      >
        <ArrowLeft class="w-4 h-4" />
      </button>
    {/if}

    <div class="d-flex align-items-center gap-1 py-2 fw-semibold text-secondary" style="white-space: nowrap;">
      {domainName}
    </div>

    <!-- Info desk button -->
    <button
      class="d-flex align-items-center gap-1 py-2 px-3 fw-semibold text-secondary border-0 bg-white"
      on:click={onInfoClick}
    >
      <Info class="w-4 h-4 mr-1" />
      {t.info}
    </button>
  </div>

  {#if $isLogin == false}
    <div style="justify-content: end;">
      <button class="btn relative btn-primary btn-small mr-6" on:click|preventDefault={goToLogin}>
        <div class="flex items-center justify-center">{t.login}</div>
      </button>
      <button class="btn relative btn-secondary btn-small" on:click|preventDefault={goToSignUp}>
        <div class="flex items-center justify-center">{t.signup}</div>
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
              {t.manageKey}
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
              {t.logout}
            </div>
          </button>
        </svelte:fragment>
      </Dropdown>
    </div>
  {/if}
</div>
