<script>
  import { faBars, faComments, faUpRightAndDownLeftFromCenter } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
  import { isLogin, isSignUpPage, chatTitles, sessionMessages, accessToken, userEmail } from "../lib/store"
  import fastapi from "../lib/api";

  $: chatTitles, sessionMessages
  let activeMessages = []
  let userMessage = '';
  let activeChatId = -1;
  let isSidebarVisible = true;
  let newChatTitle = '';
  let isNewChatModalOpen = false;

  function openNewChatModal() {
    isNewChatModalOpen = true;
  }

  function closeNewChatModal() {
    isNewChatModalOpen = false;
    newChatTitle = "";
  }

  function sendMessage() {
    if (userMessage.trim()) {
      let url = '/api/chat/session'
      let params = {
        chat_id: activeChatId,
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
          userMessage = '';
        },
        (json_error) => {
          error = json_error
        }
      )
    }
  }
  function getChatTitles() {
    let url = "/api/chat/titles"
    let params = {}

    fastapi('get', url, params, 
        (json) => {
          chatTitles.set(json);
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  getChatTitles()
  function getSessionMessages(chat_id) {
    let url = "/api/chat/session/" + chat_id
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
    let url = "/api/chat/create"
    let params = {title: newChatTitle}
    fastapi('post', url, params, 
        (json) => {
            newChatTitle=''
        },
        (json_error) => {
            error = json_error
        }
    )
  }
  function selectChat(id) {
    activeChatId = id
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
</script>

<!-- TODO: faRobot으로 import하면 왜 안되는지 모르겠음 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<!-- TODO: style sheet 부트스트랩으로 변경 -->
<style>
  .full-container {
    display: flex;
    height: 100vh;
  }
  .sidebar {
    width: 200px;
    border-right: 1px solid #ccc;
    display: flex;
    flex-direction: column;
    transition: width 0.3s;
    overflow-y: auto;
  }
  .sidebar.hidden {
    width: 0;
    overflow: hidden;
    transition: width 0.3s;
  }
  .sidebar button {
    display: block;
    width: 100%;
    padding: 10px;
    background: none;
    border: none;
    text-align: left;
    cursor: pointer;
  }

  .sidebar button.active {
    background-color: #eee;
  }

  .sidebar ul {
    list-style: none;
    padding: 15px 20px;
    cursor: pointer;
  }
  .top-bar {
    display: flex;
    justify-content: flex-end;
    padding: 10px;
  }
  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  .messages {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding: 1rem;
    height: 100vh;
  }
  .input-container {
    display: flex;
    padding: 1rem;
    background-color: #fff;
  }
  .input-container textarea {
    flex: 1;
    padding: 0.5rem;
    font-size: 1rem;
  }
  .input-container button {
    margin-left: 0.5rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 4px;
    cursor: pointer;
  }
  .input-container button:hover {
    background-color: #0056b3;
  }
  .message {
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    white-space: pre-wrap;
  }
  .message.user {
    text-align: right;
    background-color: #eee;
    align-self: flex-end;
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

  .toggle-button {
    color: black;
    border: white;
    border: none;
    top: 20px;
    left: 20px;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
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
    width: 100%;
    min-height: 50px;
    padding: 10px;
    box-sizing: border-box;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
    resize: none;
  }
  .message-input:focus {
    outline: none;
    border-color: #007BFF;
  }
  .center-text {
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  .mr-6 {
    margin-right: 6px;
  }
</style>

<div class="full-container">
  <nav class="h-full w-full {isSidebarVisible ? 'nav-bg-grey' : ''}">
    <div class="h-14 d-flex justify-content-between items-center px-4 align-items-center">
      <div>
        <button class="toggle-button" on:click="{toggleSidebar}">
          <FontAwesomeIcon icon={faBars} />
        </button>
      </div>
      <button class="toggle-button" on:click="{openNewChatModal}">
        <FontAwesomeIcon icon={faComments} />
      </button>
    </div>
    <div class="h-full w-full">
      <div class="sidebar {isSidebarVisible ? '' : 'hidden'}">
        <ul>
          {#each $chatTitles as chatTitle}
            <button
              on:click={() => selectChat(chatTitle.id)}
              class:active={chatTitle.id === activeChatId}
            >
              {chatTitle.name}
            </button>
          {/each}
        </ul>
      </div>
    </div>

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
  </nav>
    
  <!-- TODO: user와 bot의 채팅이 좌우로 넓게 배열되어있어서 유저가 읽기 불편함
   (ChatGPT처럼 가운데에 몰려있는 형식으로 변환 필요해보임) -->
  <div class="chat-container">
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
        <button class="btn relative btn-primary btn-small mr-6" on:click|preventDefault={handleLogOut}>
          <div class="flex items-center justify-center">
            로그아웃
          </div>
        </button>
      {/if}
      
    </div>
    <!-- TODO: Active Chat ID 가 -1일 경우 비어있는 chatting으로 화면 rendering(store 변수 때문에 계속 남아있음) -->
    <div class="messages">
      {#each $sessionMessages.messages as message}
        <div class="message {message.sender}">
          {message.text}
        </div>
      {/each}
    </div>
    <div class="input-container">
      <textarea
        bind:value={userMessage}
        on:keydown={handleKeyDown}
        placeholder="Type your message here..."
        class="message-input"
      ></textarea>
      <button on:click="{sendMessage}">Send</button>
    </div>
    <div class="center-text">
      LLM은 실수할 수 있습니다. 중요한 정보를 확인하세요.
    </div>
  </div>
</div>
