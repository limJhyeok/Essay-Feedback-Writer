<script>
  import { faBars } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
  import { isLogin, isSignUpPage } from "../lib/store"
  
  // TODO: messages will be empty list after applying backend
  let activeMessages = []
  let userInput = '';
  // TODO: chatHistory will be empty list after applying backend
  let chatHistory = [
    {
      message: [
        { sender: 'user', text: 'Hello\nHow are you?' },
        { sender: 'bot', text: 'I am fine, thank you!\nHow can I assist you today?' }
      ]
    },
    {
      message: [
        { sender: 'user', text: 'Hello\nHow are you2?' },
        { sender: 'bot', text: 'I am fine2, thank you!2\nHow can I assist you today?' }
      ]
    }
  ]  
  let chatHistoryTitles = [
    { id: 0, name: "Chat 1" },
    { id: 1, name: "Chat 2" },
  ];
  let activeChatId = -1;
  let isSidebarVisible = true;

  function sendMessage() {
    if (userInput.trim()) {
      activeMessages = [...activeMessages, { sender: 'user', text: userInput }];
      userInput = '';
      // 여기서 API 호출을 통해 ChatGPT 응답을 받는 로직을 추가하세요.
    }
  }

  function selectChat(id) {
    activeChatId = id;
    activeMessages = chatHistory[activeChatId].message
    // id를 사용하여 특정 채팅 기록을 로드하는 로직을 추가하세요.
  }
  function toggleSidebar() {
    isSidebarVisible = !isSidebarVisible;
  }
  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent the default new line behavior
      sendMessage();
    }
  }
  function goToSignUp(){
    event.preventDefault();
    $isSignUpPage = true
    window.location.hash = '#/authorize';
  }
  function goToLogin(){
    event.preventDefault();
    $isSignUpPage = false
    window.location.hash = '#/authorize';
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
    position: absolute;
    top: 20px;
    left: 20px;
    color: black;
    border: white;
    border: none;
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
  <nav class="h-full w-full {isSidebarVisible ? 'nav-bg-grey' : ''}" >
    <div class=" h-14">
      <button class = "toggle-button" on:click="{toggleSidebar}">
        {#if isSidebarVisible}
          <FontAwesomeIcon icon = {faBars} />
        {:else}
          <FontAwesomeIcon icon = {faBars} />
        {/if}
      </button>
    </div>
    <div class = "h-full w-full">
      <div class="sidebar {isSidebarVisible ? '': 'hidden'}">
        <ul>
          {#each chatHistoryTitles as chatTitles}
            <button on:click={() => selectChat(chatTitles.id)} class:active={chatTitles.id === activeChatId}>
              {chatTitles.name}
            </button>
          {/each}
        </ul>
      </div>
    </div>
  </nav>
  
  <!-- TODO: user와 bot의 채팅이 좌우로 넓게 배열되어있어서 유저가 읽기 불편함
   (ChatGPT처럼 가운데에 몰려있는 형식으로 변환 필요해보임) -->
  <div class="chat-container">
    <!-- TODO: User Login 여부에 따른 top-bar 변환 필요 -->
    <!-- if isLogin == false  else user profile-->
    <div class="top-bar">
      <button class="btn relative btn-primary btn-small mr-6" on:click={goToLogin}>
        <div class="flex items-center justify-center">
          로그인
        </div>
      </button>
      <button class="btn relative btn-secondary btn-small" on:click={goToSignUp}>
        <div class = "flex items-center justify-center">
          회원가입
        </div>
      </button>
    </div>
    <div class="messages">
      {#each activeMessages as message}
        <div class="message {message.sender}">
          {message.text}
        </div>
      {/each}
    </div>
    <div class="input-container">
      <textarea
        bind:value={userInput}
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
