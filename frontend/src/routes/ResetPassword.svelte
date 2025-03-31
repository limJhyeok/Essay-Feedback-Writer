<script>
import {link, push} from 'svelte-spa-router'
import { onMount } from "svelte";
import { isSignUpPage } from "../lib/store"
import fastapi from '../lib/api';
import "./reset_password.css";
let token = "";
let newPassword = "";
let confirmPassword="";
let error = "";

onMount(() => {
	const hash = window.location.hash;
	const queryString = hash.includes('?') ? hash.split('?')[1] : '';
	const urlParams = new URLSearchParams(queryString);
	token = urlParams.get('token');
});

function handleResetPasswordSubmit(){
		let url = "/api/v1/user/reset-password"
		if (newPassword !== confirmPassword) {
			error = 'Passwords do not match.';
			return;
		}
		let params = {
            token: token,
            new_password: newPassword,
        }
		fastapi('post', url, params,
			(json) => {
				push('/authorize')
			},
			(json_error) => {
				error = json_error
			}
		)
	}
function handleLoginClick() {
    $isSignUpPage = false
	push('/authorize')
}
</script>

<main class="container vh-100 d-flex flex-column justify-content-center">
	<div class="row justify-content-center">
	  <div class="col-md-6 text-center">
		<h1 class="mb-3">비밀번호를 리셋하세요</h1>
		<p class="mb-4">Please enter your new password and confirm it to reset your password.</p>

		<!-- 폼 -->
		<form on:submit|preventDefault={handleResetPasswordSubmit}>
		  <div class="form-group mb-3">
			<label for="password" class="form-label">Set Password</label>
			<input
			  type="password"
			  id="password"
			  bind:value={newPassword}
			  required
			  class="form-control"
			  placeholder="Enter your new password"
			/>
		  </div>

		  <div class="form-group mb-3">
			<label for="confirm_password" class="form-label">Confirm Password</label>
			<input
			  type="password"
			  id="confirm_password"
			  bind:value={confirmPassword}
			  required
			  class="form-control"
			  placeholder="Confirm your new password"
			/>
		  </div>

		  <!-- 오류 메시지 -->
		  {#if error}
			<div class="alert alert-danger">{error}</div>
		  {/if}

		  <button type="submit" class="btn btn-primary w-100">Reset Password</button>
		</form>

		<!-- 로그인 페이지로 이동 링크 -->
		<a
		  use:link
		  href="/authorize"
		  on:click|preventDefault={handleLoginClick}
		  class="d-block mt-4"
		>
		  Login 페이지로 돌아가기
		</a>
	  </div>
	</div>
  </main>
  