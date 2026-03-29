<script>
  import Router from 'svelte-spa-router'
  import Auth from './routes/Auth.svelte'
  import Passoword from './routes/Password.svelte';
  import ResetPassword from './routes/ResetPassword.svelte';
  import IeltsFeedbackWriter from './routes/IELTSFeedbackWriter.svelte';
  import DomainSelector from './routes/DomainSelector.svelte';
  import KSATFeedbackWriter from './routes/KSATFeedbackWriter.svelte';
  const routes = {
    '/': DomainSelector,
    '/ielts': IeltsFeedbackWriter,
    '/ksat': KSATFeedbackWriter,
    '/authorize': Auth,
    '/password': Passoword,
    '/reset-password': ResetPassword
  }
</script>

<Router {routes}/>
