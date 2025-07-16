# YouTube Summarizer

This is a simple Python application that allows you to download YouTube video transcripts and summarize them using the OpenRouter API.

## Features

*   Download transcripts from YouTube videos and playlists.
*   Summarize transcripts using a configurable API (OpenRouter).
*   Save summaries to Markdown files.
*   Configurable API key, user prompt, system prompt, and context.

## Getting Started

### Prerequisites

*   Python 3.x
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/a45r78/yt-summary.git
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd /path/to/Youtubesummaries
    ```

3.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

    The application will also attempt to install `yt-dlp` if it's not found.

### Running the Application

To start the application, run the `main.py` file:

```bash
python main.py
```

### Configuration

The application uses an OpenRouter API key, which should be stored in a `.env` file. Other settings, such as prompts, are configured within the application's settings window.

1.  **API Key (`.env` file):**
    *   Create a file named `.env` in the root directory of the project.
    *   Add your OpenRouter API key to this file in the format:
        ```
        OPENROUTER_API_KEY="your_openrouter_api_key_here"
        ```
    *   You can create the `.env` file from the `.env.example` using the following commands:
        *   **Windows (Command Prompt):**
            ```cmd
            copy .env.example .env
            ```
        *   **Windows (PowerShell):**
            ```powershell
            Copy-Item .env.example .env
            ```
        *   **macOS/Linux:**
            ```bash
            cp .env.example .env
            ```
    *   **Important:** Do not commit your `.env` file to version control. A `.env.example` file is provided for reference.

2.  **Application Settings (Prompts):**
    *   Open the application and click the "Settings" button.
    *   **User Prompt:** This is the prompt sent to the AI along with the transcript.
    *   **System Prompt:** This sets the role and behavior of the AI.
    *   **Context:** (Optional) This text will be prepended to the System Prompt, allowing you to provide additional context for the summarization (e.g., "I am researching for a school project on AI.").
    *   **Save Settings:** Click the "Save" button to save your configuration. These settings will be saved to `config.json` and loaded automatically on subsequent launches.

## Usage

1.  Enter a YouTube video or playlist URL in the input field.
2.  Click "Download and Summarize".
3.  The summary will appear in the text area.
4.  You can copy the summary to your clipboard or save it as a Markdown file using the respective buttons.