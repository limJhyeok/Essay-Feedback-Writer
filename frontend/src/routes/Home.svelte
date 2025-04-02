<script>
  import { faBars, faComments, faEllipsis } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
  import { isLogin, isSignUpPage, chatTitles, chatSessionMessages as chatSessionMessages, accessToken, userEmail } from "../lib/store"
  import fastapi from "../lib/api";
  import { onMount, tick } from 'svelte';
  import { marked } from 'marked'
  import { push } from 'svelte-spa-router'
  import active from 'svelte-spa-router/active';
  import "./home.css";
  import Error from "../components/Error.svelte"


  $: chatTitles, chatSessionMessages
  let activeMessages = []
  let userMessage = '';
  let activeChatSessionId = -1;
  let isSidebarVisible = true;
  let newChatTitle = 'New Chat';
  let isNewChatModalOpen = false;
  let answer = '';
  let generateLoading = false;
  let checkDeleteChatModalOpen = false;
  let selectedChatId = null;
  let fileInput;
  let isFileUploading = false;
  let inputClass = '';
  let error = {detail:[]}

  if ($isLogin == true){
    getChatTitles();
  } else {
    handleUnauthorized();
  }

  async function handleUnauthorized() {
    alert("로그인이 필요합니다.");
    await tick(); // Wait while UI update finishes
    push('/authorize');
  }

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
      // TODO: sender는 항상 user인데 params에 등록을 해야하는것인가?
      // sender가 항상 user임을 보장? 추후 확장 시 달라질 수 있는가?
      let params = {
        chat_session_id: activeChatSessionId,
        sender: 'user',
        message: userMessage
      }
      fastapi('post', url, params,
        (json) => {
          chatSessionMessages.update(state => {
            return [...state, { sender: 'user', text: userMessage }];
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
    let url = import.meta.env.VITE_EEVE_SERVER_URL + _url
    let method = "POST"
    let headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
    let params = {
            chat_session_id: activeChatSessionId,
            bot_id: 1,
            question: userMessage,
            context: $chatSessionMessages
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
                        chatSessionMessages.update(state => {
                          return [...state, { sender: 'bot', text: answer }];
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
          chatSessionMessages.set(json.data);
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  function createNewChat(){
    let url = "/api/v1/chat/create"
    if (!newChatTitle.trim()) {
      inputClass = 'is-invalid';
      return
    }
    inputClass = '';
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
    let url = `/api/v1/chat/rename/${chatTitle.id}`;
    let params = { title: newChatTitle };

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
      let url = import.meta.env.VITE_EEVE_SERVER_URL + _url
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
          <h5 class="modal-title">Create New Chat</h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeNewChatModal}"></button>
        </div>
        <div class="modal-body">
          <input
            type="text"
            class="form-control {inputClass}"
            bind:value={newChatTitle}
            placeholder="Please Enter The Chat Title"
          />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" on:click="{closeNewChatModal}">Cancel</button>
          <button type="button" class="btn btn-primary" on:click="{createNewChat}" o>Create</button>
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
        {#each $chatSessionMessages as message }
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
