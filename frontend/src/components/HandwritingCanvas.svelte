<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let canvas;
  let cursorCanvas;
  let cursorCtx;
  let ctx;
  let isDrawing = false;
  let tool = 'pen';
  let penSize = 2;
  let penColor = '#000000';
  let eraserSize = 20;

  let cursorPos = { x: -100, y: -100 };
  let showEraserCursor = false;
  let activePointerId = null;
  let lastStrokeEndTime = 0;

  let history = [];
  let historyIndex = -1;

  const PEN_SIZES = [4, 6, 8];
  const COLORS = ['#000000', '#ff0000', '#0000ff'];

  onMount(() => {
    ctx = canvas.getContext('2d');
    cursorCtx = cursorCanvas.getContext('2d');
    resizeCanvas();
    saveState();
    window.addEventListener('resize', resizeCanvas);
  });

  onDestroy(() => {
    window.removeEventListener('resize', resizeCanvas);
  });

  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const displayWidth = rect.width;
    const displayHeight = Math.max(400, window.innerHeight * 0.5);
    const tempImage = ctx.getImageData(0, 0, canvas.width, canvas.height);
    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    cursorCanvas.width = displayWidth * dpr;
    cursorCanvas.height = displayHeight * dpr;
    cursorCanvas.style.width = displayWidth + 'px';
    cursorCanvas.style.height = displayHeight + 'px';
    ctx.scale(dpr, dpr);
    ctx.putImageData(tempImage, 0, 0);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }

  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX ?? e.touches?.[0]?.clientX) - rect.left;
    const y = (e.clientY ?? e.touches?.[0]?.clientY) - rect.top;
    return { x, y };
  }

  function drawEraserCursor(x, y) {
    const dpr = window.devicePixelRatio || 1;
    cursorCtx.setTransform(1, 0, 0, 1, 0, 0);
    cursorCtx.clearRect(0, 0, cursorCanvas.width, cursorCanvas.height);
    if (tool !== 'eraser' || !showEraserCursor) return;
    cursorCtx.scale(dpr, dpr);
    cursorCtx.beginPath();
    cursorCtx.arc(x, y, eraserSize / 2, 0, Math.PI * 2);
    cursorCtx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
    cursorCtx.lineWidth = 1.5;
    cursorCtx.stroke();
  }

  function handlePointerEnter(e) {
    if (e.pointerType === 'touch') return;
    showEraserCursor = true;
    const { x, y } = getPos(e);
    drawEraserCursor(x, y);
  }

  function handlePointerLeaveCanvas(e) {
    showEraserCursor = false;
    drawEraserCursor(-100, -100);
    endDraw(e);
  }

  function handlePointerMoveCanvas(e) {
    if (e.pointerType !== 'touch' && tool === 'eraser') {
      showEraserCursor = true;
      const { x, y } = getPos(e);
      drawEraserCursor(x, y);
    }
    draw(e);
  }

  function startDraw(e) {
    if (e.pointerType === 'touch') return;
    e.preventDefault();
    e.stopPropagation();
    canvas.setPointerCapture(e.pointerId);
    activePointerId = e.pointerId;
    isDrawing = true;
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);

    if (tool === 'eraser') {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.lineWidth = eraserSize;
    } else {
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = penColor;
      const pressure = e.pressure > 0 ? e.pressure : 0.5;
      ctx.lineWidth = penSize * Math.max(0.3, Math.min(1.5, pressure * 1.5));
    }
  }

  function draw(e) {
    if (!isDrawing || e.pointerId !== activePointerId) return;
    e.preventDefault();

    const events = e.getCoalescedEvents?.() ?? [e];
    for (const ce of events) {
      const { x, y } = getPos(ce);

      if (tool === 'pen') {
        const pressure = ce.pressure > 0 ? ce.pressure : 0.5;
        ctx.lineWidth = penSize * Math.max(0.3, Math.min(1.5, pressure * 1.5));
      }

      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  function endDraw(e) {
    if (!isDrawing) return;
    if (e && e.pointerId != null && e.pointerId !== activePointerId) return;
    e?.preventDefault();
    if (activePointerId != null) {
      try { canvas.releasePointerCapture(activePointerId); } catch (_) {}
    }
    activePointerId = null;
    isDrawing = false;
    lastStrokeEndTime = Date.now();
    ctx.closePath();
    ctx.globalCompositeOperation = 'source-over';
    saveState();
  }

  function handleToolbarPointerDown(e) {
    if (e.pointerType === 'pen') {
      e.preventDefault();
      e.stopPropagation();
    }
  }

  function handleToolbarPointerUp(e) {
  if (e.pointerType === 'pen') {
    e.preventDefault();
    e.stopPropagation();
  }
}

  function handleToolbarClick(e) {
    if (Date.now() - lastStrokeEndTime < 250) {
      e.preventDefault();
      e.stopPropagation();
    }
  }

  function saveState() {
    historyIndex++;
    history = history.slice(0, historyIndex);
    history.push(canvas.toDataURL());
  }

  function undo() {
    if (historyIndex <= 0) return;
    historyIndex--;
    restoreState();
  }

  function redo() {
    if (historyIndex >= history.length - 1) return;
    historyIndex++;
    restoreState();
  }

  function restoreState() {
    const img = new Image();
    img.onload = () => {
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      ctx.restore();
    };
    img.src = history[historyIndex];
  }

  function clearCanvas() {
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
    saveState();
  }

  export function exportBlob() {
    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/png');
    });
  }

  export function isEmpty() {
    return historyIndex <= 0;
  }
</script>

<div class="canvas-wrapper">
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="toolbar" on:pointerdown={handleToolbarPointerDown} on:pointerup={handleToolbarPointerUp} on:click|capture={handleToolbarClick}>
    <div class="tool-group">
      <button
        class="tool-btn"
        class:active={tool === 'pen'}
        on:click={() => tool = 'pen'}
        title="Pen"
      >Pen</button>
      <button
        class="tool-btn"
        class:active={tool === 'eraser'}
        on:click={() => tool = 'eraser'}
        title="Eraser"
      >Eraser</button>
      <button class="tool-btn" on:click={undo} title="Undo" disabled={historyIndex <= 0}>Undo</button>
      <button class="tool-btn" on:click={redo} title="Redo" disabled={historyIndex >= history.length - 1}>Redo</button>
      <button class="tool-btn" on:click={clearCanvas} title="Clear">Clear</button>
    </div>

    <div class="tool-group">
      <span class="tool-label">Size:</span>
      {#each PEN_SIZES as size}
        <button
          class="size-btn"
          class:active={penSize === size}
          on:click={() => penSize = size}
        >
          <span class="size-dot" style="width:{size * 3}px;height:{size * 3}px;background:{penColor}"></span>
        </button>
      {/each}
    </div>

    <div class="tool-group">
      <span class="tool-label">Color:</span>
      {#each COLORS as color}
        <button
          class="color-btn"
          class:active={penColor === color}
          style="background:{color}"
          on:click={() => penColor = color}
        ></button>
      {/each}
    </div>
  </div>

  <div class="canvas-container">
    <canvas
      bind:this={canvas}
      on:pointerdown={startDraw}
      on:pointermove={handlePointerMoveCanvas}
      on:pointerenter={handlePointerEnter}
      on:pointerup={endDraw}
      on:pointerleave={handlePointerLeaveCanvas}
      on:lostpointercapture={endDraw}
      style="touch-action:none; cursor:{tool === 'eraser' ? 'none' : 'crosshair'}; border:1px solid #ccc; border-radius:0 0 6px 6px; background:#fff; width:100%; display:block;"
    ></canvas>
    <canvas
      bind:this={cursorCanvas}
      class="cursor-overlay"
    ></canvas>
  </div>
</div>

<style>
  .canvas-wrapper {
    width: 100%;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
  }

  .canvas-container {
    position: relative;
  }

  .cursor-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    border-radius: 0 0 6px 6px;
  }

  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    padding: 8px 12px;
    background: #f5f7fa;
    border: 1px solid #ccc;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    /* user-select: none; */
    /* -webkit-user-select: none; */
  }

  .tool-group {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .tool-label {
    font-size: 13px;
    color: #555;
    margin-right: 2px;
  }

  .tool-btn {
    padding: 4px 10px;
    font-size: 13px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    transition: background 0.15s;
  }

  .tool-btn:hover {
    background: #eee;
  }

  .tool-btn.active {
    background: #4a90d9;
    color: #fff;
    border-color: #4a90d9;
  }

  .tool-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .size-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
  }

  .size-btn.active {
    border-color: #4a90d9;
    background: #e8f0fe;
  }

  .size-dot {
    border-radius: 50%;
    display: block;
  }

  .color-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid #ccc;
    cursor: pointer;
    padding: 0;
  }

  .color-btn.active {
    border-color: #4a90d9;
    box-shadow: 0 0 0 2px #4a90d9;
  }
</style>
