<script>
  import Router from 'svelte-spa-router'
  import Home from './routes/Home.svelte'
  import Auth from './routes/Auth.svelte'
  import Passoword from './routes/Password.svelte';

  const routes = {
    '/': Home,
    '/authorize': Auth,
    '/password': Passoword
  }
</script>

<Router {routes}/>
