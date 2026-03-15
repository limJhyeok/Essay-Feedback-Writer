<script>
  export let tabs = [];
  export let activeTab = '';
  export let onTabChange = () => {};
</script>

<ul class="nav nav-tabs mb-3">
  {#each tabs as tab}
    <li class="nav-item" style="cursor: pointer;">
      <a
        class={"nav-link " + (activeTab === tab.id ? 'active' : '') + (tab.disabled ? ' disabled' : '')}
        on:click={() => !tab.disabled && onTabChange(tab.id)}
        style="box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
      >
        {tab.label}
      </a>
    </li>
  {/each}
</ul>
