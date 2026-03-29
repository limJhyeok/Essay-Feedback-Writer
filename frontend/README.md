# Essay Feedback Writer - Frontend

Svelte + Vite single-page application for the Essay Feedback Writer.

## Setup

```bash
npm install
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build
```

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode).

## Project Structure

```
src/
├── App.svelte                        # Root component with svelte-spa-router
├── routes/
│   ├── DomainSelector.svelte         # Landing page — domain selection (IELTS, KSAT, etc.)
│   ├── IELTSFeedbackWriter.svelte    # IELTS essay submission and feedback UI
│   ├── KSATFeedbackWriter.svelte     # KSAT exam browsing, per-question essay/feedback UI
│   ├── Auth.svelte                   # Login / Register
│   ├── Password.svelte               # Password change
│   └── ResetPassword.svelte          # Password reset via email
├── components/
│   ├── HandwritingCanvas.svelte      # Stylus/touch canvas for handwriting input
│   ├── FeedbackView.svelte           # Renders AI feedback (per-criterion scores + overall)
│   ├── TopBar.svelte                 # Navigation bar with user info
│   └── ManageKeyModal.svelte         # API key CRUD modal
├── lib/
│   ├── api.js                        # Fetch wrapper with JWT Bearer token
│   └── store.js                      # Svelte writable stores (localStorage-backed)
```

## Routes

| Path | Component | Description |
|---|---|---|
| `/` | DomainSelector | Choose essay domain |
| `/ielts` | IELTSFeedbackWriter | IELTS Writing Task 2 |
| `/ksat` | KSATFeedbackWriter | Korean university entrance exams |
| `/authorize` | Auth | Login / Register |
| `/password` | Password | Change password |
| `/reset-password` | ResetPassword | Email-based password reset |

## Testing

```bash
npm run test         # Run Vitest + @testing-library/svelte tests
```
