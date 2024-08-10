<script>
  import Router from 'svelte-spa-router'
  import Home from './routes/Home.svelte'
  import Auth from './routes/Auth.svelte';
  const routes = {
    '/': Home,
    '/authorize': Auth,
  }
</script>

<Router {routes}/>
