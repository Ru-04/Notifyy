# NOTIFY

NOTIFY is an AI-powered notification filtering system for Google Chat that only alerts users for important workplace messages.

## Features

- Detects new Google Chat messages
- Uses a carefully engineered AI prompt to classify message importance
- Shows desktop notifications only for critical messages
- Filters out routine and low-priority chats
- Supports VIP sender prioritization

## Tech Stack

- Python
- FastAPI
- Google Gemini API
- Prompt Engineering
- Chrome Extension
- JavaScript

## AI Prompting

The project relies on a detailed prompt engineering approach to guide Gemini into acting as a workplace message triage engine. Instead of generating conversational responses, the model follows strict instructions and returns structured JSON indicating whether a message is critical.

## Project Structure

```
backend/
extension/
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/Ru-04/Notifyy.git
cd NOTIFY
```

2. Create a virtual environment.

```bash
python -m venv .venv
```

3. Activate the virtual environment.

**Windows**

```bash
.venv\Scripts\activate
```

4. Install dependencies.

```bash
pip install -r requirements.txt
```

5. Create a `.env` file and add your Gemini API key.

```env
GEMINI_API_KEY=your_api_key
```

6. Start the backend.

```bash
uvicorn main:app --reload
```

7. Load the Chrome extension.

- Open Chrome
- Go to `chrome://extensions`
- Enable **Developer mode**
- Click **Load unpacked**
- Select the `extension` folder
