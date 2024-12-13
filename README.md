# TassBeehBot

**TassBeehBot** automates point claiming and task management on the TassBeeh App using data extracted from the web client.

---

## Features

- **Automated Task Completion**: Logs into the TassBeeh Bot App and performs tasks automatically.
- **Point Claiming**: Automates the process of claiming points based on app-specific intervals.
- **Refill Timer Handling**: Automatically waits until tasks or points are ready to claim.
- **Randomized Delays**: Mimics realistic user behavior by adding random delays between tasks.
- **Error Handling**: Logs errors and auto-restarts the bot to ensure consistent operation.

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Praveensenpai/TassBeehBot.git
cd TassBeehBot
```

### 2. Install `uv` Package Manager

**Windows:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Sync Dependencies with `uv`

```bash
uv sync
```

### 4. Obtain `WebAppData.txt`

To get the necessary session data for authentication, follow these steps:

- **Open the TassBeeh Bot App** in Telegram.
- **Open Chrome Developer Tools**:
  - Right-click on the page → **Inspect** (or press `Ctrl+Shift+I` / `Cmd+Opt+I`).
- **Go to the Application Tab** in the Developer Tools window.
- **Select 'Session Storage'** from the left menu.
- **Find the entry for `https://app.tassbeeh.com`**.
- **Copy the value of the `tgWebAppData` key** (which starts with `query_id`).
- **Create a `WebAppData.txt` file** in the project directory and paste the copied data.

The contents of `WebAppData.txt` should look like this:

```plaintext
query_id=AAGtu1oyAAAAAK27WjIxngei&...
```

---

## Running the Bot

To run the bot, execute the following command:

```bash
uv run main.py
```

The bot will log in using the `WebAppData.txt` data, claim points, and repeat the process based on the app's refill intervals.

---

## Notes

- **Single Session Support**: The bot supports one active session at a time.
- **No API Key or Hash**: The bot does not require an API key or hash; authentication is handled using `WebAppData.txt`.
- **No Proxy Settings**: The bot operates without proxy configurations.
- **Planned Features**: Additional task completion functionalities are under development.

---
