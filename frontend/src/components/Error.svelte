<script>
    export let error
  </script>

  {#if typeof error.detail === 'string'}
    <div class = "alert alert-danger" role = "alert">
      <dib>
        {error.detail}
      </dib>
    </div>

    <div class = "alert alert-danger" role = "alert">
      {#each error.detail as err, i}
      <li>
        <strong>{err.loc[1]}</strong> : {err.msg}
      </li>
      {/each}
    </div>
  {/if}
