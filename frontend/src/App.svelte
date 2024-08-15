<script>
  import Router from 'svelte-spa-router'
  import Home from './routes/Home.svelte'
  import Auth from './routes/Auth.svelte'
  import ResetPassowrd from './routes/ResetPassowrd.svelte';
  const routes = {
    '/': Home,
    '/authorize': Auth,
    '/reset-password': ResetPassowrd
  }
</script>

<Router {routes}/>
