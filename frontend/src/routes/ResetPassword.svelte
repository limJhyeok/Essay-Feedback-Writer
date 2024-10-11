<script>
	import {link, push} from 'svelte-spa-router'
	import { isSignUpPage } from "../lib/store"
    import fastapi from '../lib/api';
	let user_email = ''

	function handleResetPasswordSubmit(){
		let user_id = 1
		let url = "/api/v1/user/reset-password"
		let params = {email: user_email}
		fastapi('post', url, params,
			(json) => {
				push('/')
			},
			(json_error) => {
				error = json_error
			}
		)
	}

	function handleLoginClick() {
		$isSignUpPage = false
	}
</script>
<main class="container vh-100 d-flex flex-column justify-content-center">
	<div class="row justify-content-center">
	  <div class="col-md-6 text-center">
		<h1 class="mb-3">비밀번호를 리셋하세요</h1>
		<p class="mb-4">이메일 주소를 입력하면 해당 이메일로 임시 비밀번호가 발송됩니다.</p>

		<form on:submit|preventDefault={handleResetPasswordSubmit}>
		  <div class="form-group mb-3">
			<label for="email" class="form-label">이메일 주소</label>
			<input
			  type="email"
			  id="email"
			  bind:value={user_email}
			  required
			  class="form-control"
			>
		  </div>
		  <button type="submit" class="btn btn-primary w-100">계속</button>
		</form>

		<a use:link href="/authorize" on:click|preventDefault={handleLoginClick} class="d-block mt-4">
			Login 페이지로 돌아가기
		</a>
	  </div>
	</div>

  </main>
