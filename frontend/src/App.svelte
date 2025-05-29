<script>
  import Router from 'svelte-spa-router'
  import Auth from './routes/Auth.svelte'
  import Passoword from './routes/Password.svelte';
  import ResetPassword from './routes/ResetPassword.svelte';
  import IeltsFeedbackWriter from './routes/IELTSFeedbackWriter.svelte';
  const routes = {
    '/': IeltsFeedbackWriter,
    '/authorize': Auth,
    '/password': Passoword,
    '/reset-password': ResetPassword
  }
</script>

<Router {routes}/>
