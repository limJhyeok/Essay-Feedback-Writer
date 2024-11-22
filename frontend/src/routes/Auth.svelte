<script>
  import { userEmail, accessToken, isLogin, isSignUpPage} from "../lib/store"
  import fastapi from "../lib/api";
  import { push } from "svelte-spa-router";
	import {link} from 'svelte-spa-router'

  let user_email = '';
  let user_password = '';
  let social_account_providers = ['Google', 'Microsoft', 'Apple']

  function login(event) {
      event.preventDefault()
      let url = "/api/v1/user/login"
      let params = {
          username: user_email,
          password: user_password,
      }
      fastapi('login', url, params,
          (json) => {
              $accessToken = json.access_token
              $userEmail = json.user_email
              $isLogin = true
              push("/")
          },
          (json_error) => {
              error = json_error
          }
      )
  }
  function signup(event) {
      event.preventDefault()
      let url = "/api/v1/user/create"
      let params = {
          email: user_email,
          is_social: false,
          password: user_password
      }
      fastapi('post', url, params,
          (json) => {
              // TODO: 회원가입 후 자동으로 로그인한 상태로 만들 것인지 고려
              // $accessToken = json.access_token
              // $userEmail = json.user_email
              // $isLogin = true
              push("/")
          },
          (json_error) => {
              error = json_error
          }
      )
  }
  function handleAuthSubmit(event) {
    if ($isSignUpPage) {
      signup(event);
    } else {
      login(event);
    }
  }
  function toggleMode() {
      $isSignUpPage = !$isSignUpPage;
  }
</script>
<style>
  :global(body) {
    background-color: #f8f9fa;
  }

  main {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    padding: 2rem;
  }

  .form-control, .btn {
    border-radius: 0.25rem;
  }

  .btn-primary {
    background-color: #007bff;
    border-color: #007bff;
  }

  .btn-primary:hover {
    background-color: #0056b3;
    border-color: #0056b3;
  }

  .social-section .btn {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>

<main class="container vh-100 d-flex align-items-center justify-content-center">
  <div class="col-md-6 col-lg-4">
    <h1 class="text-center mb-4">{$isSignUpPage ? '회원가입' : '로그인'}</h1>
    <form on:submit={handleAuthSubmit} class="mb-3">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" id="email" class="form-control" bind:value={user_email} required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" id="password" class="form-control" bind:value={user_password} autoComplete = "off" required />
      </div>
      <button type="submit" class="btn btn-primary w-100">{$isSignUpPage ? '회원가입' : '로그인'}</button>
    </form>
    <div class="text-center mb-3">
      <button class="btn btn-link" on:click={toggleMode}>
        {$isSignUpPage ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
      </button>
    </div>
    <div class="text-center mb-4">
      <a use:link href="/password" class="text-decoration-none d-inline-block">
        비밀번호를 잃어버리셨나요?
      </a>
    </div>
    <div class="social-section">
      {#each social_account_providers as provider}
        <button class="btn btn-outline-secondary w-100 mb-2 text-start position-relative">
          <div class="position-absolute start-0 top-50 translate-middle-y ms-3">
            <img src="/{provider.toLowerCase()}-icon.svg" alt="{provider} 로고" width="20" height="20">
          </div>
          <span class="ms-5">{provider}로 계속하기</span>
        </button>
      {/each}
    </div>

</main>
