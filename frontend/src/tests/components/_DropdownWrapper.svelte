<script>
  import Dropdown from '../../components/Dropdown.svelte';
  export let align = 'left';
</script>

<Dropdown {align}>
  <button slot="trigger" let:toggle on:click={toggle} data-testid="trigger">Toggle</button>
  <div slot="menu" let:close>
    <button on:click={close} data-testid="menu-item">Menu Item</button>
  </div>
</Dropdown>
