<script>
  let query = '';
  let loading = false;
  let status = '';
  let messages = [];
  let error = '';
  let messageListElement;

  let feedback = '';
  let feedbackLoading = false;
  let feedbackSuccess = '';
  let feedbackError = '';

  function scrollToBottom() {
    if (messageListElement) {
      messageListElement.scrollTop = messageListElement.scrollHeight;
    }
  }

  async function submitFeedback() {
    if (!feedback.trim()) {
      feedbackError = 'Please enter feedback';
      return;
    }

    feedbackLoading = true;
    feedbackError = '';
    feedbackSuccess = '';

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: feedback,
          last_query: query || null
        }),
      });

      const data = await response.json();

      if (response.ok) {
        feedbackSuccess = data.message;
        feedback = '';
        setTimeout(() => { feedbackSuccess = ''; }, 3000);
      } else {
        feedbackError = data.error || 'Failed to submit feedback';
      }
    } catch (err) {
      feedbackError = 'Failed to connect to backend';
    } finally {
      feedbackLoading = false;
    }
  }

  async function generateSheet() {
    if (!query.trim()) {
      error = 'Please enter a query';
      return;
    }

    loading = true;
    error = '';
    messages = [];
    status = 'Connecting to backend...';

    try {
      const response = await fetch('/api/generate-sheet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const data = await response.json();
        error = data.error || 'Something went wrong';
        status = '';
        loading = false;
        return;
      }

      // Set up EventSource to receive streaming updates
      status = 'Starting...';
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.message) {
              status = data.message;
              messages = [...messages, data.message];
              setTimeout(scrollToBottom, 10);
            }

            if (data.done) {
              if (data.success) {
                status = '🎉 Complete!';
                setTimeout(() => { status = ''; }, 3000);
              } else {
                error = data.error || 'Generation failed';
                status = '';
              }
              loading = false;
            }
          }
        }
      }

    } catch (err) {
      error = 'Failed to connect to backend. Make sure Flask server is running.';
      status = '';
      loading = false;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      generateSheet();
    }
  }
</script>

<main>
  <h1>Wine Tasting Sheet Generator</h1>

  <div class="input-section">
    <label for="query">
      Enter wine query (e.g., "both scopa and both realce")
    </label>
    <input
      id="query"
      type="text"
      bind:value={query}
      on:keypress={handleKeyPress}
      placeholder="both scopa and both realce"
      disabled={loading}
    />
    <button on:click={generateSheet} disabled={loading || !query.trim()}>
      {loading ? 'Generating...' : 'Generate Sheet'}
    </button>
  </div>

  {#if status}
    <div class="status">
      <div class="spinner"></div>
      <span>{status}</span>
    </div>
  {/if}

  {#if error}
    <div class="error">
      <strong>Error:</strong> {error}
    </div>
  {/if}

  {#if messages.length > 0}
    <div class="messages">
      <h3>Progress</h3>
      <div class="message-list" bind:this={messageListElement}>
        {#each messages as message}
          <div class="message">{message}</div>
        {/each}
      </div>
    </div>
  {/if}

  <div class="feedback-section">
    <h3>Feedback</h3>
    <p class="feedback-label">Have suggestions or found an issue? Let us know:</p>
    <textarea
      bind:value={feedback}
      placeholder="Enter your feedback here..."
      rows="4"
      disabled={feedbackLoading}
    ></textarea>
    <button on:click={submitFeedback} disabled={feedbackLoading || !feedback.trim()}>
      {feedbackLoading ? 'Sending...' : 'Send Feedback'}
    </button>

    {#if feedbackSuccess}
      <div class="feedback-success">
        ✓ {feedbackSuccess}
      </div>
    {/if}

    {#if feedbackError}
      <div class="feedback-error">
        {feedbackError}
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, sans-serif;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .input-section {
    margin-bottom: 2rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #666;
    font-size: 0.9rem;
  }

  input {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    margin-bottom: 1rem;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #646cff;
  }

  input:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
  }

  button {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    background: #646cff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) {
    background: #535bf2;
  }

  button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-radius: 4px;
    color: #1976d2;
    margin-bottom: 1rem;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 3px solid #90caf9;
    border-top-color: #1976d2;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    padding: 1rem;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c33;
    margin-bottom: 1rem;
  }

  .messages {
    padding: 1rem;
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .messages h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
    color: #333;
    font-size: 1rem;
  }

  .message-list {
    max-height: 400px;
    overflow-y: auto;
  }

  .message {
    padding: 0.5rem;
    margin-bottom: 0.25rem;
    background: white;
    border-left: 3px solid #646cff;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
    color: #333;
  }

  .feedback-section {
    margin-top: 3rem;
    padding: 1.5rem;
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .feedback-section h3 {
    margin-top: 0;
    margin-bottom: 0.5rem;
    color: #333;
    font-size: 1.1rem;
  }

  .feedback-label {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
  }

  textarea {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, sans-serif;
    border: 2px solid #ddd;
    border-radius: 4px;
    margin-bottom: 1rem;
    box-sizing: border-box;
    resize: vertical;
  }

  textarea:focus {
    outline: none;
    border-color: #646cff;
  }

  textarea:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
  }

  .feedback-success {
    padding: 0.75rem;
    margin-top: 0.75rem;
    background: #e8f5e9;
    border: 1px solid #81c784;
    border-radius: 4px;
    color: #2e7d32;
  }

  .feedback-error {
    padding: 0.75rem;
    margin-top: 0.75rem;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c33;
  }
</style>
