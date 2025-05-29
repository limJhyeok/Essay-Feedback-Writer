<script>
  import { faRobot } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
  import { userEmail, accessToken, isLogin, isSignUpPage} from "../lib/store"
  import fastapi from "../lib/api";
  import { push } from "svelte-spa-router";
	import {link} from 'svelte-spa-router'
  import Error from "../components/Error.svelte"
  import "./auth.css";
  let user_email = '';
  let user_password = '';
  let social_account_providers = ['Google', 'Microsoft', 'Apple']

  let error = {detail:[]}

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
          is_superuser: false,
          password: user_password
      }
      fastapi('post', url, params,
          (json) => {
              $isSignUpPage = false;
              user_email = "";
              user_password = "";
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

<main class="container vh-100 d-flex align-items-center justify-content-center">
  <div class="col-md-6 col-lg-4">

    <div class = "text-center">
      <div class="mb-4 home-tooltip">
        <a href="/" class="d-inline-block">
          <FontAwesomeIcon icon={faRobot} size="2x" />
        </a>
        <span class="tooltiptext">
          Go to Home
        </span>
      </div>
    </div>

    <h1 class="text-center mb-4">{$isSignUpPage ? 'Sign up' : 'Log in'}</h1>
    <form on:submit={handleAuthSubmit} class="mb-3">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" id="email" class="form-control" bind:value={user_email} required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" id="password" class="form-control" bind:value={user_password} autoComplete = "off" required />
      </div>

      <Error error={error} />

      <button type="submit" class="btn btn-primary w-100">{$isSignUpPage ? 'Sign up' : 'Log in'}</button>
    </form>
    <div class="text-center mb-3">
      <button class="btn btn-link" on:click={toggleMode}>
        {$isSignUpPage ? "Already have an account? Log in" : "Don't have an account? Sign up"}
      </button>
    </div>
    <div class="text-center mb-4">
      <a use:link href="/password" class="text-decoration-none d-inline-block">
        Forgot your password?
      </a>
    </div>
    <!-- <div class="social-section">
      {#each social_account_providers as provider}
        <button class="btn btn-outline-secondary w-100 mb-2 text-start position-relative">
          <div class="position-absolute start-0 top-50 translate-middle-y ms-3">
            <img src="/{provider.toLowerCase()}-icon.svg" alt="{provider} 로고" width="20" height="20">
          </div>
          <span class="ms-5">{provider}로 계속하기</span>
        </button>
      {/each}
    </div> -->

</main>
