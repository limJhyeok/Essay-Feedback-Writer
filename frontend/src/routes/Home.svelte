<script>
  import { faBars, faComments, faEllipsis } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
  import { isLogin, isSignUpPage, chatTitles, sessionMessages, accessToken, userEmail } from "../lib/store"
  import fastapi from "../lib/api";
  import { onMount, tick } from 'svelte';
  import { marked } from 'marked'
    import active from 'svelte-spa-router/active';

  $: chatTitles, sessionMessages
  let activeMessages = []
  let userMessage = '';
  let activeChatSessionId = -1;
  let isSidebarVisible = true;
  let newChatTitle = '새 채팅';
  let isNewChatModalOpen = false;
  let answer = '';
  let generateLoading = false;
  let checkDeleteChatModalOpen = false;
  let selectedChatId = null;
  let fileInput;
  let isFileUploading = false;
  function openNewChatModal() {
    isNewChatModalOpen = true;
  }

  function closeNewChatModal() {
    isNewChatModalOpen = false;
    newChatTitle = '';
  }

  function sendMessage() {
    if (userMessage.trim()) {
      let url = '/api/v1/chat/session'
      let params = {
        chat_session_id: activeChatSessionId,
        sender: 'user',
        message: userMessage
      }
      fastapi('post', url, params,
        (json) => {
          sessionMessages.update(state => {
            return {
              ...state,
              messages: [...state.messages, { sender: 'user', text: userMessage }]
            };
          });
          if (activeChatSessionId === -1){
            getChatTitles();
            setRecentChatSessionAsActive(() => {
              selectChat(activeChatSessionId);
              generateAnswer();
            })
          } else {
            generateAnswer();
          }
          userMessage = '';

        },
        (json_error) => {
          error = json_error
        }
      )
    }
  }

  function generateAnswer() {
    generateLoading = true;
    let _url = "/api/v1/chat/generate-answer"
    let url = import.meta.env.VITE_SERVER_URL + _url
    let method = "POST"
    let headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
    let params = {
            chat_session_id: activeChatSessionId,
            bot_id: 1,
            question: userMessage,
            context: $sessionMessages.messages
        }
    fetch(url, {
        method: method,
        headers: headers,
        body: JSON.stringify(params)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        function read() {
            reader.read().then(({ done, value }) => {
              try {
                generateLoading = false;
                if (done) {
                      sessionMessages.update(state => {
                                    return {
                                        ...state,
                                        messages: [...state.messages, { sender: 'bot', text: answer }]
                                    };
                                });
                      answer = '';
                      return;
                }
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                lines.forEach(line => {
                    if (line.trim()) {
                        const parsedLine = JSON.parse(line);
                        const status = parsedLine.status;
                        const data = parsedLine.data;
                        if (status === 'processing') {
                            answer = (answer ?? '') + data;
                        }
                    }
                });
                read();
              } catch (err) {
                handleGenerateError(err)
              }
            }
          );
        }
        read();
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });
  }

  function handleGenerateError(err){
    answer = ''
    generateLoading = false;
    console.error(err)
  }

  function getChatTitles() {
    let url = "/api/v1/chat/titles"
    let params = {}

    fastapi('get', url, params,
        (json) => {
          chatTitles.set(json.data);
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  getChatTitles()

  function setRecentChatSessionAsActive(callback) {
    let url = "/api/v1/chat/recent";
    let params = {}

    fastapi('get', url, params,
        (json) => {
          activeChatSessionId = json.id
        if (callback) {
          callback();
          }
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  function getSessionMessages(chat_id) {
    let url = "/api/v1/chat/session/" + chat_id
    let params = {}
    fastapi('get', url, params,
        (json) => {
          sessionMessages.set(json.message_history)
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  function createNewChat(){
    let url = "/api/v1/chat/create"
    let params = {title: newChatTitle}
    let recentChatSessionId = -1;
    fastapi('post', url, params,
        (json) => {
            newChatTitle=''
            getChatTitles();
            closeNewChatModal();
            setRecentChatSessionAsActive(() => {
              selectChat(activeChatSessionId);
            })
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  function selectChat(id) {
    activeChatSessionId = id
    getSessionMessages(id)
  }
  function toggleSidebar() {
    isSidebarVisible = !isSidebarVisible;
  }
  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function goToSignUp(){
    $isSignUpPage = true
    window.location.hash = '#/authorize';
  }
  function goToLogin(){
    $isSignUpPage = false
    window.location.hash = '#/authorize';
  }
  function handleLogOut(){
    $accessToken=""
    $isLogin=false
    $userEmail=""
    window.location.reload();
  }
  function autoResizeTextArea(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

  let editingChatTitleId = null;
  let inputElement = null;
  function handleRenameChatButton(chatId){
    editingChatTitleId = chatId
    closePopup();
    tick().then(() => {
      if (inputElement) {
        inputElement.focus();
      }
    });
  }
  function openCheckDeleteChatModal(chatId){
    closePopup();
    checkDeleteChatModalOpen = true;
    selectedChatId = chatId;
  }
  function closeCheckDeleteChatModal(){
    checkDeleteChatModalOpen = false;
  }
  function deleteChat(chatId){
    openCheckDeleteChatModal(chatId);
  }
  function renameChatTitle(chatTitle) {
    if (newChatTitle.trim() === '' || newChatTitle === chatTitle.title) {
      return
    }
    let url = `/api/v1/chat/rename/${chatTitle.id}`;  // TODO: url 및 inDTO 변경
    let params = { renamed_title: newChatTitle };

    fastapi('put', url, params,
      (json) => {
        editingChatTitleId = null;
        newChatTitle='';
        getChatTitles();
      },
      (json_error) => {
        console.error("Error updating chat title:", json_error);
      }
    );
  }
  function cancelEdit() {
    newChatTitle = '';
    inputElement=null;
    editingChatTitleId = null;

  }

  function handleKeyPress(event, chatTitle) {
    if (event.key === 'Enter') {
      renameChatTitle(chatTitle);
      cancelEdit();
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }

  function confirmDeleteChat() {
    let url = `/api/v1/chat/delete/${selectedChatId}`
    let params = {}

    fastapi('delete', url, params,
      (json) => {
        selectedChatId = null;
        activeChatSessionId = -1;
        closeCheckDeleteChatModal();
        getChatTitles();
        selectChat(activeChatSessionId);
      },
      (json_error) => {
        error = json_error;
        selectedChatId = null;
        closeCheckDeleteChatModal();
      }
    );
  }
  let activePopupId = null
  let popupContainer;

  function togglePopup(chatId, event) {
    event.stopPropagation();
    const button = event.currentTarget;
    const buttonRect = button.getBoundingClientRect();

    if (activePopupId === chatId) {
      closePopup();
    } else {
      activePopupId = chatId;
      if (popupContainer) {
        popupContainer.style.display = 'block';
        popupContainer.style.top = `${buttonRect.bottom}px`;
        popupContainer.style.left = `${buttonRect.right}px`;
      }
    }
  }

  function closePopup() {
    activePopupId = null;
    if (popupContainer) {
      popupContainer.style.display = 'none';
    }
  }

  function handleClickOutside(event) {
    if (popupContainer && !popupContainer.contains(event.target) && !event.target.closest('.options-container')) {
      closePopup();
    }
  }
  function handleFileIconClick() {
    fileInput.click();
  }
  async function uploadPDF() {
    const file = fileInput.files[0];
    if (!file) return;
    isFileUploading = true;
    const formData = new FormData();
    formData.append('file', file);
    try {
      // TODO: activeChatSessionId가 -1일 때 새로운 chat session 생성 후 select
      if (activeChatSessionId === -1){
        alert("왼쪽 sidebar에서 chat을 선택하거나 새로운 chat을 생성해주세요.")
        return;
      }
      let _url = `/api/v1/chat/${activeChatSessionId}/upload-pdf/`
      let url = import.meta.env.VITE_SERVER_URL + _url
      const response = await fetch(url, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        alert('PDF uploaded and processed successfully');
        fileInput.value = '';
      } else {
        alert('Error uploading PDF');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isFileUploading = false;
    }
  }
  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<!-- TODO: refactoring style sheet -->
<style>
  .sidebar {
    width: 200px;
    height: calc(100vh - 66px);
    display: flex;
    flex-direction: column;
    transition: width 0.3s;
  }
  .sidebar.hidden {
    width: 0;
    overflow: hidden;
    transition: width 0.3s;
  }
  .message-container {
    position: relative;
    display: grid;
    grid-template-rows: fit-content(100%) 1fr fit-content(100%);
    width: 100vw;
    height: 100vh;
    max-height: 100vh;
    margin: 0 5vw;
    overflow-y: hidden;
  }
  .fa-bars-comments-container {
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
  }
  .chat-item {
  position: relative;
  }

  .chat-button-container {
    display: flex;
    align-items: center;
    transition: background-color 0.3s ease;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    padding: 10px 10px 5px 0;
    text-align: center;
  }

  .chat-button-container:hover,
  .chat-button-container.active {
    background-color: #eee;
  }

  .sidebar button {
    flex-grow: 1;
    background: transparent;
    border: none;
    text-align: left;
  }
  .options-container {
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .chat-button-container:hover .options-container,
  .chat-button-container.active .options-container {
    opacity: 1;
  }

  .options-popup {
    position: fixed;
    background-color: white;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    z-index: 9999;
    width: 150px;
  }
  .sidebar button.active {
    background-color: #eee;
  }
  .sidebar button:hover {
    background-color: #eee;
  }
  .sidebar ul {
    list-style-type: none; /* 불릿(점) 제거 */
    padding: 0; /* 기본 패딩 제거 */
    margin: 15px 20px;
    cursor: pointer;
  }
  .top-bar {
    padding: 15px 0;
    display: flex;
    justify-content: flex-end;
    width: 100%;
    background-color: white;
  }
  .messages {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    max-height: 100%;
  }
  .input-container {
    display: grid;
    grid-template-columns: 1fr fit-content(100%) fit-content(100%);
    grid-template-rows: fit-content(100%) fit-content(100%);
    width: 100%;
    height: fit-content;
    padding: 10px 0 0 0;
    background-color: #fff;
  }
  .input-container textarea {
    padding: 0.5rem;
    font-size: 1rem;
    overflow-y: auto;
    resize: none;
    transition: all 0.3s ease;
    max-height: 30vh;
  }
  .input-container textarea:disabled {
    background-color: #f0f0f0;
    color: #a0a0a0;
    opacity: 1;
  }
  .input-container button {
    font-size: 1rem;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    padding: 20px 18px;
    height: fit-content;
    width: fit-content;
  }
  .input-container button:hover {
    background-color: #0056b3;
  }
  .message {
    margin-bottom: 1rem;
    border-radius: 10px;
    white-space: pre-wrap;
    /* margin-right: 20%; */
    /* margin-left: 20%; */
    max-width: 70%;
    display: flex;
    justify-content: flex-start;
    overflow-wrap: break-word;
    height: fit-content;
  }
  .message.user {
    background-color: #eee;
    align-self: flex-end;
    border-radius: 0.5rem;
    padding: 1rem;
  }
  .message.bot {
    text-align: left;
    align-self: flex-start;
    display: flex;
  }
  .message.bot::before {
    content: "\f544";
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    color: black;
    margin-right: 18px;
    display: inline-block;
    font-size: 1.3rem;
  }
  .toggle-button-box {
    position: sticky;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 15px 10px;
    z-index: 2;
  }
  .toggle-button-box.off {
    position: absolute;
    top: 0;
  }
  .toggle-button {
    display: flex;
    justify-content: center;
    align-items: center;
    color: black;
    border: none;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
    margin: 0 10px;
  }
  .toggle-button:hover {
    background-color: #f5f5f5;
  }
  .h-14 {
    height: 3.5rem;
  }
  .nav-bg-grey {
    background-color: #e3e3e3;
  }
  .message-input {
    min-width: 30vw;
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 5px;
    resize: none;
  }
  .message-input:focus {
    outline: none;
    border-color: #007BFF;
  }
  .center-text {
    text-align: center;
    grid-column-start: 1;
    grid-column-end: 4;
    background-color: white;
    white-space: nowrap;
    text-overflow: ellipsis;
    padding: 10px;
    overflow: hidden;
    font-size: 0.8rem;
  }
  .mr-6 {
    margin-right: 6px;
  }


  .options-icon {
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    color: #bbb;
  }

  .options-popup button {
    display: block;
    width: 100%;
    padding: 5px 10px;
    border: none;
    background-color: #fff;
  }
  .options-popup button:hover {
    background-color: #eee;
  }
  .message-content{
    display: flex;
    flex-direction: column;
    height: fit-content;
    overflow: auto;
  }
  :global(.message-content p) {
    margin: 0;
  }
  :global(.message-content pre) {
    background-color: #eee;
    padding: 1rem;
    margin: 0;
    border-radius: 0.5rem;
    overflow-x: auto;
  }
  :global(.message code) {
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9em;
  }


  .upload-tooltip {
    position: relative;
    display: inline-block;
    margin: 0 5px;
  }

  .upload-tooltip .tooltiptext {
    position: absolute;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #555;
    border-radius: 5px;
    padding: 7px 10px 5px 10px;
    bottom: calc(100% + 10px);
    left: 50%;
    transform: translate(-55%, 0);
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 0.8rem;
    white-space: nowrap;
    color: #fff;

  }

  .upload-tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
  }

  .upload-tooltip.disabled .tooltiptext {
    background-color: #aaa;
  }
</style>

<!-- TODO: Component -->

<div bind:this={popupContainer} class="options-popup" style="display: none;">
  <button on:click={() => handleRenameChatButton(activePopupId)}>Rename</button>
  <button on:click={() => openCheckDeleteChatModal(activePopupId)} class="text-danger">Delete</button>
</div>

<!-- TODO: modal refactoring -->
<!-- delete chat modal -->
{#if checkDeleteChatModalOpen}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">해당 채팅을 삭제하고 싶습니까? 돌이킬 수 없습니다.</h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeCheckDeleteChatModal}"></button>
        </div>
        <div class="modal-body">
          <p>정말로 이 채팅을 삭제하시겠습니까?</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" on:click="{closeCheckDeleteChatModal}">취소</button>
          <button type="button" class="btn btn-danger" on:click="{confirmDeleteChat}">삭제</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- 새 채팅 생성 modal -->
{#if isNewChatModalOpen}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">새 채팅 생성</h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeNewChatModal}"></button>
        </div>
        <div class="modal-body">
          <input
            type="text"
            class="form-control"
            bind:value={newChatTitle}
            placeholder="채팅 제목을 입력하세요"
          />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" on:click="{closeNewChatModal}">취소</button>
          <button type="button" class="btn btn-primary" on:click="{createNewChat}">생성</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<div class="d-flex">
  <nav class="{isSidebarVisible ? 'nav-bg-grey' : ''}">
    <div class="{isSidebarVisible ? 'toggle-button-box' : 'toggle-button-box off'}">
      <button class="toggle-button" on:click="{toggleSidebar}">
        <FontAwesomeIcon icon={faBars} />
      </button>
      <button class="toggle-button" on:click="{openNewChatModal}">
        <FontAwesomeIcon icon={faComments} />
      </button>
    </div>
    <div class="sidebar overflow-auto border-end {isSidebarVisible ? '' : 'hidden'}">
      <ul>
        {#each $chatTitles as chatTitle}
        <li class="chat-item">
          <div class="chat-button-container rounded
          {activeChatSessionId === chatTitle.id ? 'active' : ''}
          {activePopupId === chatTitle.id ? 'active' : ''}">
          {#if editingChatTitleId === chatTitle.id}
            <input
              bind:this={inputElement}
              type="text"
              class="form-control"
              bind:value={newChatTitle}
              on:keydown={(event) => handleKeyPress(event, chatTitle)}
              on:blur={(cancelEdit)}
              placeholder={chatTitle.title}
            />
          {:else}
            <button
              on:click={() => selectChat(chatTitle.id)}
              class="btn w-100 text-start py-2 {chatTitle.id === activeChatSessionId ? 'active' : ''}"
            >
              {chatTitle.title}
            </button>
          {/if}
            <div class="options-container">
              <button
                class="options-icon btn btn-link p-0 border-0"
                on:click={(event) => togglePopup(chatTitle.id, event)}
              >
                <FontAwesomeIcon icon={faEllipsis} />
              </button>
            </div>
          </div>
        </li>
        {/each}
      </ul>
    </div>
  </nav>

  <div class="message-container">
    <div class="top-bar">

      {#if $isLogin == false}
      <button class="btn relative btn-primary btn-small mr-6" on:click|preventDefault={goToLogin}>
        <div class="flex items-center justify-center">
          로그인
        </div>
      </button>
      <button class="btn relative btn-secondary btn-small" on:click|preventDefault={goToSignUp}>
        <div class = "flex items-center justify-center">
          회원가입
        </div>
      </button>
      {:else}
        <button class="btn relative btn-primary btn-small" on:click|preventDefault={handleLogOut}>
          <div class="flex items-center justify-center">
            로그아웃
          </div>
        </button>
      {/if}

    </div>
    <div class="messages">
      {#if activeChatSessionId !== -1}
        {#each $sessionMessages.messages as message }
          <div class="message {message.sender}">
            <div class="message-content">
              {@html marked.parse(message.text)}
            </div>
          </div>
        {/each}
        {#if answer !== ''}
          <div class="message bot">
            <div class="message-content">
              {@html marked.parse(answer)}
            </div>
          </div>
        {/if}
        {#if generateLoading === true}
          <div class="message bot">
            loading...
          </div>
        {/if}
      {/if}
    </div>
    <div class="input-container">
      <textarea
        bind:value={userMessage}
        on:keydown={handleKeyDown}
        on:input={autoResizeTextArea}
        placeholder="대화를 입력하세요..."
        class="message-input"
        disabled = {isFileUploading}
      ></textarea>

      <div class="upload-tooltip {isFileUploading || activeChatSessionId === -1 ? 'disabled' : ''}">
        <button class="file-upload-icon" on:click={handleFileIconClick} disabled={isFileUploading || activeChatSessionId === -1}>
          {isFileUploading? '⏳' : '📁'}
        </button>
        <span class="tooltiptext">
          {isFileUploading || activeChatSessionId === -1 ? '대화를 시작한 후 파일을 올려주세요' : 'PDF 파일을 올려주세요'}
        </span>
      </div>

      <input
      type="file"
      accept=".pdf"
      style="display: none;"
      bind:this={fileInput}
      on:change={uploadPDF}
      />
      <button on:click="{sendMessage}" disabled={isFileUploading}>Send</button>
      <div class="center-text">
        LLM은 실수할 수 있습니다. 중요한 정보를 확인하세요.
      </div>
    </div>
  </div>
</div>
