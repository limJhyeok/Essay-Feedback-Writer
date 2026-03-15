<script>
  export let open = false;
  export let title = '';
  export let size = 'lg';
  export let onClose = () => {};
</script>

{#if open}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered {size && size !== 'md' ? `modal-${size}` : ''}">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title d-flex align-items-center">
            <slot name="icon" />
            {title}
          </h5>
          <button type="button" class="btn-close" aria-label="Close" on:click={onClose}></button>
        </div>
        <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
          <slot />
        </div>
        {#if $$slots.footer}
          <div class="modal-footer">
            <slot name="footer" />
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
