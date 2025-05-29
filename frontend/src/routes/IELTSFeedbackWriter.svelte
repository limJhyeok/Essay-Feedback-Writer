<script>
  import { isLogin, isSignUpPage, accessToken, userEmail } from "../lib/store"
  import fastapi from "../lib/api";
  import { onMount, tick, onDestroy } from 'svelte';
  import { marked } from 'marked'
  import { push } from 'svelte-spa-router'
  import "./home.css";
  import Error from "../components/Error.svelte"
  import { BookOpen, FileText, Award, BarChart, RefreshCw, History, Search, CheckCircle, Info, Copy, Check, Trash2,  SquarePen} from 'lucide-svelte';
  import { User, Settings, LogOut, HelpCircle, Key } from 'lucide-svelte';

  // Reactive state
  let mainActiveTab = 'prompts';
  let promptContent = '';
  let promptId = null;
  let essayContent = '';
  let showHistory = false;
  let showInfoDeskModalOpen = false;
  let showManageKeyModalOpen = false;

  let activeIdOfessays = 0;
  let activeIdOfFeedbacks = 0;

  let rubricCriteria = [];

  let submittedEssayContent = null;
  let submittedEssayId = null;
  let registeredEssayList = [];
  let editing = false;

  let providerName = "OpenAI";
  let providerNameList = ["OpenAI"]
  let APIKeyName = "";
  let APIKey = "";
  let registeredAPIKeys = [];

  let selectedApiKey = null;

  function cancel() {
    showManageKeyModalOpen = false;
  }

  let prompts = []

  let feedbackList = [];

  const CRITERIA_LABELS = {
    taskResponse: "Task Response",
    coherenceCohesion: "Coherence & Cohesion",
    lexicalResource: "Lexical Resource",
    grammaticalRange: "Grammatical Range & Accuracy"
  };

  // Sample example answer
  let exampleAnswer = "";

  let copied = false;

  function checkAuth(){
    let params = {
    }
    let url = "/api/v1/user/auth"
    fastapi("get", url, params,
      (json) => {
      },
      (json_error) => {
        error = json_error;
      }
    )
  }
  checkAuth();

  function registerAPIKey(){
    if (!APIKey.trim()) return;
    let params = {
      provider_name: providerName,
      name: APIKeyName,
      api_key: APIKey
    }
    let url = "/api/v1/ielts/api_keys"
    fastapi("post", url, params,
      (json) => {
        APIKeyName = "";
        APIKey = "";
      },
      (json_error) => {
        error = json_error;
      }
    )
  }


  function getRegisteredAPIKeys(){
    let params = {
    }
    let url = "/api/v1/ielts/api_keys"
    fastapi("get", url, params,
      (json) => {
        registeredAPIKeys = json;
      },
      (json_error) => {
        error = json_error;
      }
    )
  }

  function getRubricCriteria(){
    let params = {
      name: "IELTS Writing Task 2"
    }
    let url = "/api/v1/ielts/criteria"
    fastapi("get", url, params,
      (json) => {
        rubricCriteria = json;
      },
      (json_error) => {
        error = json_error;
      }
    )
  }
  getRubricCriteria();

  function getEssaysByPromptId() {
    return new Promise((resolve, reject) => {
      let params = {
        prompt_id: promptId
      };
      let url = "/api/v1/ielts/essays";

      fastapi("get", url, params,
        (json) => {
          registeredEssayList = json;
          resolve();
        },
        (json_error) => {
          error = json_error;
          reject(json_error);
        }
      );
    });
  }
  function getFeedbacksByEssayId(essay_id){
    let params = {
      prompt_id: promptId,
      essay_id: essay_id
    }
    let url = "/api/v1/ielts/feedbacks"
    fastapi("get", url, params,
      (json) => {
        activeIdOfFeedbacks = 0;
        feedbackList = json;
      },
      (json_error) => {
        error = json_error;
      }
    )
  }


  function copyToClipboard() {
    navigator.clipboard.writeText(exampleAnswer)
      .then(() => {
        copied = true;
        setTimeout(() => copied = false, 2000); // Re-enable after 2 seconds
      })
      .catch(() => {
        alert('Failed to copy text.');
      });
  }

  // Computed word count
  $: wordCount =  essayContent.replace(/[\t\n\r]/g, "").length;

  // Handle prompt selection
  function selectPrompt(selectedPrompt) {
    promptContent = selectedPrompt.content;
    if (promptId !== selectedPrompt.id) {
      essayContent = '';
    }
    promptId = selectedPrompt.id

    getExampleAnswer();
    mainActiveTab = 'write';
    getEssaysByPromptId().then(() => {
      activeIdOfFeedbacks = 0;
      activeIdOfessays = 0;
      if (registeredEssayList.length > 0) {
          getFeedbacksByEssayId(registeredEssayList[activeIdOfessays].id);
        }
    });
  }

  // Handle essay submission
  function submitEssay() {
    let params = {
      prompt_id: promptId,
      content: essayContent,
    }
    let url = "/api/v1/ielts/essays"
    fastapi("post", url, params,
      (json) => {
        editing = false;
        submittedEssayId = json.id;
        submittedEssayContent = json.content;


        getEssaysByPromptId().then(() => {
          mainActiveTab = "feedback";
          activeIdOfFeedbacks = 0;
          activeIdOfessays = 0;
          generateFeedback();
        }).catch(err => {
          error = err;
        });
      },
      (json_error) => {
            error = json_error;
      }
    )
  }

  function generateFeedback(){
    let params = {
      prompt: promptContent,
      rubric_name: "IELTS Writing Task 2",
      essay_content: essayContent,
      api_model_name: selectedFeedbackModel.api_model_name
    }
    feedbackList = [];
    let url = `/api/v1/ielts/essays/${submittedEssayId}/feedback`;
    fastapi("post", url, params,
      (json) => {
        getFeedbacksByEssayId(submittedEssayId);
      },
      (json_error) => {
        error = json_error;
      }
    )
  }

  let checkDeleteApiModalOpen = false;
  let error = {detail:[]}
  const models = ["IELTS Feedback Writer"]
  let showDropdown = false;
  let selectedModel = models[0];
  let feedbackModels = []
  let selectedFeedbackModel = null;

  function read_bots() {
    let params = {}
    let url = `/api/v1/ielts/api_models/${providerName}`;
    fastapi("get", url, params,
      (json) => {
        feedbackModels = json
        if (feedbackModels.length > 0) {
         selectedFeedbackModel = feedbackModels[0];
        }
      },
      (json_error) => {
        error = json_error;
      }
    )
  }
  read_bots();

  if ($isLogin == false){
    handleUnauthorized();
  }

  // top bar
  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function selectModel(model) {
    selectedModel = model;
    showDropdown = false;
  }

  async function handleUnauthorized() {
    alert("You need to login to use the service.")
    await tick();
    push('/authorize');
  }

  function getPrompts(){
    let params = {}
    let url = "/api/v1/ielts/prompts"
    fastapi("get", url, params,
      (json) => {
        prompts = json.map(item => ({
          id: item.id,
          content: item.content
        }));
      },
      (json_error) => {
            error = json_error
      }
    )
  }
  getPrompts();

  function getExampleAnswer(){
    let params = {
      prompt_id: promptId
    }
    let url = "/api/v1/ielts/example"
    fastapi("get", url, params,
      (json) => {
        exampleAnswer = json.content
      },
      (json_error) => {
            error = json_error
      }
    )
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
  function openCheckDeleteApiKeyModal(apiKey){
    closePopup();
    checkDeleteApiModalOpen = true;
    selectedApiKey = apiKey
  }

  let editingApiKey = null;
  function handleRenameApiKeyButton(apiKey){
    editingApiKey = apiKey
    tick().then(() => {
      if (inputElement) {
        inputElement.focus();
      }
    });
  }
  function renameApiKey(apiKey) {
    if (apiKey.name.trim() === '' || editingApiKey.name === apiKey.name) {
      editingApiKey = null;
      return;
    }

    const index = secretKeys.findIndex(k => k.id === apiKey.id);
    if (index !== -1) {
      secretKeys[index].name = apiKey.name;
      // Reassign to trigger reactivity in Svelte
      secretKeys = [...secretKeys];
    }
    editingApiKey = null;
  }
  function closeCheckDeleteApiKeyModal(){
    checkDeleteApiModalOpen = false;
  }
  function deleteApiKey(apiKey){
    openCheckDeleteApiKeyModal(apiKey)
  }

  function cancelEdit() {
    newChatTitle = '';
    inputElement=null;
    editingChatTitleId = null;

  }

  function confirmDeleteApiKey(){
    secretKeys = secretKeys.filter(k => k.id !== selectedApiKey.id);
    selectedApiKey = null;
    checkDeleteApiModalOpen = false;
  }
  let activePopupId = null
  let popupContainer;


  function closePopup() {
    activePopupId = null;
    if (popupContainer) {
      popupContainer.style.display = 'none';
    }
  }

  function handleClickOutside(event) {
    if (!event.target.closest('.dropdown-wrapper')) {
      showDropdown = false;
      showUserProfile = false;
    }
    if (popupContainer && !popupContainer.contains(event.target) && !event.target.closest('.options-container')) {
      closePopup();
    }
  }

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
  onDestroy(() => {
    document.removeEventListener('click', handleClickOutside);
  });

  function closeInfoDeskModal(){
    showInfoDeskModalOpen = false;
  }

  function closeManageKeyModal(){
    showManageKeyModalOpen = false;
  }

  let infoDeskTab = 'rubric';
  let manageKeyTab = 'manage';

  function setInfoDeskTab(tab) {
    infoDeskTab = tab;
  }

  function setManageKeyTab(tab){
    manageKeyTab = tab;
  }

  let showUserProfile = false;
  let dropdownRef;
  let buttonRef;
  let profileItems = [
    // { label: 'Settings', icon: 'settings', action: () => console.log('Settings') },
    { label: 'Key', icon: 'key', action: () => {showManageKeyModalOpen = true; getRegisteredAPIKeys();} },
    // { label: 'HelpCircle', icon: 'help-circle', action: () => console.log('help circle') },
    { label: 'Log Out', icon: 'log-out', action: () => handleLogOut() },
  ]


  // Toggle dropdown visibility
  function toggleProfileDropdown() {
    showUserProfile = !showUserProfile;
  }

</script>

<style>
  .main-tabs button {
    background-color: #f9f9f9;
  }
  .main-tabs button:hover {
    background-color: #eef2f7;
  }
  .main-tabs button.active {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
  }

  .feedback-content {
            flex: 3;
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .prompt-area {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 8px;
            border-left: 3px solid #3498db;
        }
        .essay-area {
            margin-bottom: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
            min-height: 200px;
        }
        .feedback-controls {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f5f7fa;
            border-radius: 8px;
            align-items: center;
        }
        .model-selector {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .model-dropdown {
            padding: 8px 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .feedback-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background-color: #3498db;
            color: white;
        }
        .btn-primary:hover {
            background-color: #2980b9;
        }
        .btn-secondary {
            background-color: #ecf0f1;
            color: #7f8c8d;
        }
        .btn-secondary:hover {
            background-color: #bdc3c7;
        }
        .feedback-tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
            overflow-x: auto;
        }
        .feedback-tab {
            padding: 8px 16px;
            margin-right: 5px;
            cursor: pointer;
            border: 1px solid #ddd;
            border-radius: 4px 4px 0 0;
            white-space: nowrap;
            background-color: #f9f9f9;
        }
        .feedback-tab:hover{
          background-color: #eef2f7;
        }
        .feedback-tab.active {
            background-color: #3498db;
            color: white;
            border-color: #3498db;
        }
        .feedback-content {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
        }
        .score-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .overall-score {
            display: flex;
            flex-direction: column;
            align-items: center;
            border-right: 1px solid #eee;
            padding-right: 20px;
        }
        .score-label {
            font-size: 14px;
            color: #7f8c8d;
        }
        .score-value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        .score-details {
            display: flex;
            flex: 1;
            justify-content: space-around;
        }
        .score-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .feedback-section {
            margin-bottom: 20px;
        }
        .feedback-heading {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
            display: flex;
            align-items: center;
        }
        .feedback-heading i {
            margin-right: 8px;
        }
        .feedback-list {
            padding-left: 25px;
        }
        .feedback-list li {
            margin-bottom: 8px;
        }
        .prompt-history {
            margin-bottom: 20px;
        }
        .prompt-item {
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .prompt-item:hover {
          background-color: #eef2f7;
        }
        .prompt-item.active {
          background-color: #e1ebf5;
          border-left: 3px solid #3498db;
        }
        .attempt-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .attempt-item:hover {
          background-color: #eef2f7;
        }
        .attempt-item.active {
            background-color: #e1ebf5;
            border-left: 3px solid #3498db;
        }
</style>


<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

{#if showInfoDeskModalOpen}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title d-flex align-items-center">
            <Info class="w-4 h-4 mx-1" />
             Info
          </h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeInfoDeskModal}"></button>
        </div>
        <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
          <!-- Tab Buttons -->
          <ul class="nav nav-tabs mb-3">
            <li class="nav-item" style="cursor: pointer;">
              <a class={"nav-link " + (infoDeskTab === 'rubric' ? 'active' : '')} on:click={() => setInfoDeskTab('rubric')}
                style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                Rubric
              </a>
            </li>
            <li class="nav-item" style="cursor: pointer">
              <a class={"nav-link " + (infoDeskTab === 'tips' ? 'active' : '')} on:click={() => setInfoDeskTab('tips')}
                style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                Tips
              </a>
            </li>
          </ul>

          <!-- Tab Content -->
          {#if infoDeskTab === 'rubric'}
            {#each rubricCriteria as criterion}
              <div>
                <h5><strong>Band Score {criterion.score}</strong></h5>
                <p><strong>{criterion.name}:</strong>
                  {@html marked.parse(criterion.description)}
                </p>
              </div>
            {/each}
          {:else if infoDeskTab === 'tips'}
            <div>
              <h6><strong>Tips</strong></h6>
              <ul>
                <li>You must write more than 20 words.</li>
                <li>Be specific and avoid generalisations.</li>
                <li>Use formal language — contractions like "don't" should be avoided.</li>
                <li>Check spelling, punctuation, and grammar carefully.</li>
              </ul>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

{#if showManageKeyModalOpen}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title d-flex align-items-center">
            <Key class="w-4 h-4 mx-2" />
             Manage API key
          </h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeManageKeyModal}"></button>
        </div>
        <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
          <!-- Tab Buttons -->
          <ul class="nav nav-tabs mb-3">
            <li class="nav-item" style="cursor: pointer;">
              <a class={"nav-link " + (manageKeyTab === 'manage' ? 'active' : '')} on:click={() => setManageKeyTab('manage')}
                style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                Manage
              </a>
            </li>
            <li class="nav-item" style="cursor: pointer;">
              <a class={"nav-link " + (manageKeyTab === 'register' ? 'active' : '')} on:click={() => setManageKeyTab('register')}
                style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                Register
              </a>
            </li>
          </ul>

          <!-- Tab Content -->
          {#if manageKeyTab === 'manage'}
          <div class="table-responsive mt-3">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Name</th>
                  <th>Provider</th>
                  <th>Registered</th>
                  <th>Last Used</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {#each registeredAPIKeys as registeredKey}
                  <tr>
                    {#if editingApiKey}
                    <td>
                      <input
                        type="text"
                        class="form-control {inputClass}"
                        bind:value={registeredKey.name}
                        placeholder={registeredKey.name}
                        on:keydown={(e) => {
                          if (e.key === 'Enter') {
                            renameApiKey(registeredKey);
                          }
                        }}
                      />
                    </td>
                    {:else}
                      <td>{registeredKey.name}</td>
                    {/if}
                    <td>{registeredKey.provider_name}</td>
                    <td>{registeredKey.registered_at}</td>
                    <td>{registeredKey.last_used || ''}</td>
                    <td class="text-center">
                      <button
                        class="btn btn-sm btn-outline-secondary"
                        on:click={() => handleRenameApiKeyButton(registeredKey)}
                        aria-label="Rename API key"
                      >
                        <SquarePen class = "h-4 w-4" />
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        on:click={() => openCheckDeleteApiKeyModal(registeredKey)}
                        aria-lxabel="Delete API key"
                      >
                        <Trash2 class="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>

            {#if registeredAPIKeys.length === 0}
              <div class="text-muted text-center py-4">
                No API keys registered yet.
              </div>
            {/if}
          </div>
          {:else if manageKeyTab === 'register'}
            <div class="p-3">
              <h5 class="mb-3 fw-bold">Register New API Key</h5>

              <!-- Provider Selection -->
              <div class="mb-3">
                <label class="form-label">Provider</label>
                <select bind:value={providerName} class="form-select">
                  {#each providerNameList as _provider_name}
                    <option>{_provider_name}</option>
                  {/each}
                </select>
              </div>
              <!-- Optional Name -->
              <div class="mb-2 d-flex align-items-center">
                <label class="me-2 mb-0">Name</label>
                <span class="text-muted small">(optional)</span>
              </div>
              <input
                bind:value={APIKeyName}
                class="form-control mb-3"
                placeholder="My Test Key"
                type="text"
              />

              <!-- Secret Key (Required) -->
              <label class="form-label">Secret Key</label>
              <input
                bind:value={APIKey}
                class="form-control mb-2"
                placeholder="sk-...eGNK"
                type="text"
                required
              />

              <!-- Footer Buttons -->
              <div class="d-flex justify-content-end gap-2 pt-3">
                <button class="btn btn-secondary" on:click={cancel}>
                  Cancel
                </button>
                <button
                  class="btn btn-primary"
                  on:click={registerAPIKey}
                  disabled={!APIKey.trim()}
                >
                  Register Secret Key
                </button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if checkDeleteApiModalOpen}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <Trash2 class ="h-4 w-4"/>
            Delete API key
          </h5>
          <button type="button" class="btn-close" aria-label="Close" on:click="{closeCheckDeleteApiKeyModal}"></button>
        </div>
        <div class="modal-body">
          <h5>Are you sure you want to delete
            <strong>{selectedApiKey?.name}</strong>
            ? This action cannot be undone.</h5>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" on:click="{closeCheckDeleteApiKeyModal}">Cancel</button>
          <button type="button" class="btn btn-danger" on:click="{confirmDeleteApiKey}">Yes, Delete</button>
        </div>
      </div>
    </div>
  </div>
  <!-- <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-labelledby="confirmDeleteModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title" id="confirmDeleteModalLabel">Delete API Key</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Are you sure you want to delete <strong></strong>? This action cannot be undone.
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger" on:click={confirmDeleteApiKey} data-bs-dismiss="modal">
            Yes, Delete
          </button>
        </div>
      </div>
    </div>
  </div> -->
{/if}


<div class="d-flex">
  <div class="message-container">
    <div class="top-bar">
      <!-- Wrapper for outside click detection -->
      <div class = "d-flex align-items-start gap-2 position-relative">
        <div class="dropdown-wrapper position-relative d-inline-block">

          <!-- Model selection Button -->
          <button
            type="button"
            aria-haspopup="menu"
            aria-expanded={showDropdown}
            class="d-flex align-items-center gap-1 py-2 fw-semibold text-secondary border-0 bg-white hover-bg-lightgray"
            on:click={toggleDropdown}
            style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
          >
            <div class = "hover-bg-lightgray active-bg-lightgray">{selectedModel}</div>
            <i class="fas fa-chevron-down"></i>
          </button>

          <!-- Dropdown list -->
          {#if showDropdown}
            <div class="position-absolute bg-white border rounded mt-2 shadow-sm z-1" style="min-width: 200px; width: auto;">
              {#each models as model}
                <button
                  class="dropdown-item w-100 text-start py-2 px-3"
                  on:click={() => selectModel(model)
                  }
                >
                <div class = "hover-bg-lightgray active-bg-lightgray">
                  {model}
                </div>
                </button>
              {/each}
            </div>
          {/if}
        </div>

        <!-- info desk button -->
        <button
          class="d-flex align-items-center gap-1 py-2 px-3 fw-semibold text-secondary border-0 bg-white"
          on:click={() => showInfoDeskModalOpen = true}
        >
        <Info class="w-4 h-4 mr-1" />
          Info
        </button>
    </div>

      {#if $isLogin == false}
      <div style="justify-content: end;">
        <button class="btn relative btn-primary btn-small mr-6" on:click|preventDefault={goToLogin}>
          <div class="flex items-center justify-center">
            Log In
          </div>
        </button>
        <button class="btn relative btn-secondary btn-small" on:click|preventDefault={goToSignUp}>
          <div class = "flex items-center justify-center">
            Sign Up
          </div>
        </button>
      </div>
      {:else}
      <!-- Wrapper for outside click detection -->
      <div class = "d-flex align-items-start gap-2 position-relative">
        <div class="dropdown-wrapper position-relative d-inline-block">

          <!-- selection Button -->
          <button
            type="button"
            aria-haspopup="true"
            aria-expanded={showUserProfile}
            class="d-flex align-items-center gap-1 py-2 fw-semibold text-secondary border-0 bg-white hover-bg-lightgray"
            on:click={toggleProfileDropdown}
            style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
          >
            <span class="sr-only">User Profile</span>
            <User class="h-4 w-4" />
          </button>

          <!-- Dropdown list -->
          {#if showUserProfile}
          <!-- TOOD: Change on:click -->
            <div class="position-absolute bg-white border rounded mt-2 shadow-sm z-1" style="min-width: 200px; width: auto; right: 0;">
              {#each profileItems as item}
                <button
                    class="dropdown-item w-100 text-start py-2 px-3"
                    on:click={() => {
                      item.action();
                      showUserProfile = false;
                    }}
                  >
                  <div class = "hover-bg-lightgray active-bg-lightgray" style = "border-radius: 5px;">
                    {#if item.icon === 'key'}
                      <Key class="h-4 w-4 mr-3 text-gray-500" />
                      Manage API key
                    {:else if item.icon === 'settings'}
                      <Settings class="h-4 w-4 mr-3 text-gray-500" />
                      Settings
                    {:else if item.icon === 'log-out'}
                      <LogOut class="h-4 w-4 mr-3 text-gray-500" />
                      Log out
                    {:else if item.icon === 'help-circle'}
                      <HelpCircle class= "h-4 w-4 mr-3 text-gray-500" />
                      Help & FAQ
                    {/if}
                  </div>
                </button>
              {/each}
            </div>
          {/if}
        </div>
        </div>
      {/if}

    </div>
    <div class = "messages">
      <div class="main-tabs flex mb-6" style = "border-bottom: 1px solid #ddd;">
        <button
          class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'prompts' ? 'active': ''}"
          style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
          on:click={() => mainActiveTab = 'prompts'}
        >
          <Search class="w-4 h-4 mr-2" />
          Prompts
        </button>
        {#if promptContent}
          <button
            class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'write' ? 'active': ''}"
            style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            on:click={() => mainActiveTab = 'write'}
          >
            <FileText class="w-4 h-4 mr-2" />
            Write Essay
          </button>
          <button
            class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'example' ? 'active': ''}"
            style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            on:click={() => mainActiveTab = 'example'}
          >
            <BookOpen class="w-4 h-4 mr-2" />
            Example
          </button>
          {#if registeredEssayList.length > 0}
            <button
              class="border border-gray-300 px-4 py-2 flex items-center {mainActiveTab === 'feedback' ? 'active': ''}"
              style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
              on:click={() => mainActiveTab = 'feedback'}
            >
              <BarChart class="w-4 h-4 mr-2" />
              Feedback
            </button>
          {/if}
        {/if}
      </div>

      <!-- Main content based on active tab -->
      <div class="flex-1">
        {#if mainActiveTab === 'prompts'}
          <!-- Prompt selection -->
          <div class=" p-4 mt-2" style = "background-color: #f9f9f9;">
            <h3 class="font-bold mb-4">Select a Prompt</h3>
            <div class="space-y-4">
              {#each prompts as p, index}
              <div
                  key={index}
                  class="prompt-item rounded p-4 mb-4"
                  class:active={promptContent === p.content}
                  style="cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                  on:click={() => {selectPrompt(p);}}
                  >
                {p.content}
              </div>
              {/each}
            </div>
          </div>
        {:else if mainActiveTab === 'write'}
          <!-- Essay writing interface -->
          <div class="p-4 feedback-content mt-2">
            <div class="mb-4">
              <h3 class="font-semibold">Prompt</h3>
              <div class="prompt-area" style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                {promptContent || "Please select a prompt from the Prompts tab"}
              </div>
            </div>

            {#if promptContent}
              <div class="mb-4">
                <h3 class="font-semibold">Your Essay</h3>
                <textarea
                  bind:value={essayContent}
                  on:keydown={handleKeyDown}
                  placeholder="Write your essay here..."
                  class="message-input"
                  style="width: 100%; height: 52vh"
                ></textarea>
              </div>
              <div class="d-flex justify-content-between " style = "padding: 10px; margin-bottom: 10px;
            background-color: #f5f7fa;
            border-radius: 8px;
            align-items: center;box-shadow: 0 1px 3px rgba(0,0,0,0.1);">

              <div class="model-selector">
                <span>Select AI Model:</span>
                <select bind:value={selectedFeedbackModel} class="model-dropdown">
                    {#each feedbackModels as feedbackModel}
                      <option value={feedbackModel}>{feedbackModel.alias}</option>
                    {/each}
                </select>
              </div>
              <div style="display: flex; gap: 10px;">

              <div class="text-gray-500 text-sm mt-2">
                Word count: {wordCount}
              </div>
              <div class="upload-tooltip">
                <button
                class="btn relative btn-primary btn-small"
                on:click={submitEssay}
                disabled={!essayContent.trim()}
                style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                >
                Submit for Feedback
                </button>
                {#if !essayContent.trim()}
                  <span class="tooltiptext">Please write your essay</span>
                {/if}
              </div>
            </div>
            </div>
            {/if}
          </div>
        {:else if mainActiveTab === 'feedback'}
          <div class="gap-2 mt-4 px-2" style = "display: flex; overflow-x: auto;">
            {#each registeredEssayList as registeredEssay, index}
              <div
                class="attempt-item {index === activeIdOfessays ? 'active' : ''}"
                style="min-width: 15%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                on:click={() => {activeIdOfessays = index; getFeedbacksByEssayId(registeredEssay.id);}}
              >
                <div>
                  <div>Attempt #{(registeredEssayList.length - index)}</div>
                  <div class="attempt-model small text-secondary">Submitted at</div>
                  <div class="attempt-model small text-secondary">{registeredEssay["submitted_at"]}</div>
                </div>
                <!-- <div class="attempt-score fw-bold text-dark mt-2">{attempt.score}</div> -->
              </div>
            {/each}
          </div>

          <!-- Feedback display -->
          <div class="feedback-content">
            <div class="prompt-area" style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <strong>Essay Prompt:</strong> {promptContent}
            </div>

            {#if editing}
              <textarea
                bind:value={essayContent}
                rows="10"
                class="p-2 border rounded"
                style = "width: 100%;"
              ></textarea>
            {:else}
              <div class="essay-area" style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <p>{registeredEssayList[activeIdOfessays]["content"]}</p>
              </div>
            {/if}

            <div class="feedback-controls" style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div class="model-selector">
                    <span>Select AI Model:</span>
                    <select bind:value={selectedFeedbackModel} class="model-dropdown" style = "box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                      {#each feedbackModels as feedbackModel}
                        <option value={feedbackModel}>{feedbackModel.alias}</option>
                      {/each}
                    </select>
                </div>
                <div class="feedback-actions">
                  <button
                    class="btn btn-secondary"
                    style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);"
                    on:click={() => editing = !editing}
                  >
                    {editing ? 'Done Editing' : 'Edit Essay'}
                  </button>
                  <div class="upload-tooltip">
                    <button class="btn btn-primary"
                    on:click={submitEssay}
                    disabled={!essayContent.trim()}
                    style = "box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                      Submit for Feedback
                    </button>
                    {#if registeredEssayList[activeIdOfessays]["content"] === essayContent}
                      <span class="tooltiptext">Same essay — resubmission is OK.</span>
                    {/if}
                  </div>
                </div>
            </div>
            {#if feedbackList.length > 0}
              <div class="feedback-tabs">
                  {#each feedbackList as feedback, index}
                    <div class="feedback-tab"
                    class:active={activeIdOfFeedbacks === index ? 'active': ''}
                    on:click={() => activeIdOfFeedbacks = index}
                    style = "box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                    {feedback.bot_name} ({feedback.created_at})
                  </div>
                  {/each}
              </div>

              <div class="feedback-content">
                <div class="score-card">
                  <div class="overall-score">
                      <div class="score-label">Overall Score</div>
                        <div class="score-value">{feedbackList[activeIdOfFeedbacks]["content"]?.overall_score ?? 'N/A'}</div>
                  </div>

                  <div class="score-details">
                      {#each Object.entries(feedbackList[activeIdOfFeedbacks]["content"]?.feedback_by_criteria ?? {}) as [key, { score, feedback }]}
                        <div class="score-item">
                            <div class="score-label">{CRITERIA_LABELS[key] ?? key} </div>
                            <div class="score-value">{score ?? 'N/A'}</div>
                        </div>
                      {/each}
                  </div>
                </div>

                {#each Object.entries(feedbackList[activeIdOfFeedbacks]["content"]?.feedback_by_criteria ?? {}) as [key, { score, feedback }]}
                  <div class="feedback-section">
                    <div class="feedback-heading">
                        <i>△</i> feedback for the {CRITERIA_LABELS[key] ?? key}
                    </div>
                    <ul class="feedback-list">
                        <li>{@html marked.parse(feedback ?? '')}</li>
                    </ul>
                  </div>
                {/each}
                <div class="feedback-section">
                  <div class="feedback-heading">
                      <i>△</i> Overall feedback
                  </div>
                  <ul class="feedback-list">
                      <li>{@html marked.parse(feedbackList[activeIdOfFeedbacks]["content"]?.overall_feedback ?? '')}</li>
                  </ul>
                </div>
              </div>
            {/if}
          </div>

        {:else if mainActiveTab === 'example'}
        <div class = "p-4 mt-2" style = "background-color: #f9f9f9;">
          <div class="d-flex justify-content-start mb-4">
            <h3 class="font-bold">Example Answer</h3>
            <div class="upload-tooltip">
              <button
                on:click={copyToClipboard}
                class="mx-2 p-2 text-gray-500 hover:text-gray-700 rounded hover:bg-gray-100"
                aria-label="Copy to clipboard"
                style="border: none; background: none; padding: 0;"
              >
                {#if copied}
                  <Check size={18} />
                {:else}
                  <span class="tooltiptext">Copy</span>
                  <Copy size={18} />
                {/if}
              </button>
            </div>

          </div>
          <div class="border rounded mx-4 p-4 bg-gray-50 whitespace-pre-line" style = "box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            {@html marked.parse(exampleAnswer)}
          </div>
        </div>
        {/if}
      </div>
    </div>
  </div>
</div>
