<script>
  import Router from 'svelte-spa-router'
  import Home from './routes/Home.svelte'
  import Auth from './routes/Auth.svelte'
  import Passoword from './routes/Password.svelte';
  import ResetPassword from './routes/ResetPassword.svelte';
  const routes = {
    '/': Home,
    '/authorize': Auth,
    '/password': Passoword,
    '/reset-password': ResetPassword
  }
</script>

<Router {routes}/>
