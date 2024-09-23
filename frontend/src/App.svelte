<script>
  import Router from 'svelte-spa-router'
  import Home from './routes/Home.svelte'
  import Auth from './routes/Auth.svelte'
  import ResetPassoword from './routes/ResetPassword.svelte';

  const routes = {
    '/': Home,
    '/authorize': Auth,
    '/reset-password': ResetPassoword
  }
</script>

<Router {routes}/>
