<script>
  import { userEmail, accessToken, isLogin, isSignUpPage} from "../lib/store"
  import fastapi from "../lib/api";
  import { push } from "svelte-spa-router";

  let user_email = '';
  let user_password = '';

  function login(event) {
      event.preventDefault()
      let url = "/api/user/login"
      let params = {
          email: user_email,
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
      let url = "/api/user/create"
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
  .social-section {
    margin-top: 24px;
  }
  .social-btn {
    padding: 0 8px 0 52px;
    position: relative;
    width: 320px;
    border: 1px solid;
    border-radius: 6px;
    font-size: 16px;
    align-items: center;
    background-color: #fff;
    height: 52px;
    cursor: pointer;
    color: #2d333a;
    margin-bottom: 8px;
    display: flex;
    outline: 0;
  }
  .social-logo-wrapper {
    position: absolute;
    left: 26px;
    top: 50%;
    transform: translate(-50%) translateY(-50%);
  }
  .social-logo {
    width: 20px;
    height: 20px;
    display: inline-block;
}
</style>


<main class="main-container">
  <div class="row justify-content-center">
      <div class="col-md-6">
          <h1 class="text-center mt-5">{$isSignUpPage ? '회원가입' : '로그인'}</h1>
          <form on:submit={handleAuthSubmit}>
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" class="form-control" bind:value={user_email} required />
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" id="password" class="form-control" bind:value={user_password} required />
            </div>
            <button type="submit" class="btn btn-primary w-100">{$isSignUpPage ? '회원가입' : '로그인'}</button>
          </form>
          <button class="btn btn-link w-100 mt-3" on:click={toggleMode}>
              {$isSignUpPage ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
          </button>
          <div class = "social-section">
            <!-- TODO: on:click시 google로 로그인 -->
            <button class = "social-btn w-100">
              <span class="social-logo-wrapper">
                <img class="social-logo" src="/google-icon.svg" alt="Google 로고">
              </span>
                <span class = "social-text">
                  Google로 계속하기
                </span>
            </button>
            <!-- TODO: on:click시 MS로 로그인 -->
            <button class = "social-btn w-100">
              <span class="social-logo-wrapper">
                <img class="social-logo" src="/microsoft-icon.svg" alt="Microsoft 로고">
              </span>
                <span class = "social-text">
                  Microsoft로 계속하기
                </span>
            </button>
            <!-- TODO: on:click시 Apple로 로그인 -->
            <button class = "social-btn w-100">
              <span class="social-logo-wrapper">
                <img class="social-logo" src="/apple-icon.svg" alt="Apple 로고">
              </span>
                <span class = "social-text">
                  Apple로 계속하기
                </span>
            </button>
          </div>
      </div>

  </div>
</main>
