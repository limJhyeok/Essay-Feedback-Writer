<script>
  import { onMount } from 'svelte';

  export let align = 'left';

  let open = false;

  function close() {
    open = false;
  }

  function toggle() {
    open = !open;
  }

  function handleClickOutside(event) {
    if (!event.target.closest('.dropdown-wrapper')) {
      open = false;
    }
  }

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });
</script>

<div class="dropdown-wrapper position-relative d-inline-block">
  <slot name="trigger" {toggle} />
  {#if open}
    <div
      class="position-absolute bg-white border rounded mt-2 shadow-sm z-1"
      style="min-width: 200px; width: auto; {align === 'right' ? 'right: 0;' : ''}"
    >
      <slot name="menu" {close} />
    </div>
  {/if}
</div>
