# 🎙️ Kokoro-Podcast: AI Text-to-Dialogue Generator

An application that uses the Gemini API to transform any text into a conversational, two-person podcast script and generates a fully voiced, streaming audio output using Text-to-Speech.

---

### Key Features

* **🤖 AI Scriptwriting**: Leverages the Gemini API to intelligently convert unstructured text into an engaging dialogue between a "Host" and a "Guest."
* **🗣️ Dual-Voice Synthesis**: Assigns distinct voices to each speaker in the script, creating a natural and dynamic conversational experience.
* **📡 Real-Time Audio Streaming**: Begins playing the podcast audio as it's generated, providing a seamless, real-time listening experience without long waits.
* **✨ Interactive UI**: A simple and clean web interface built with Gradio allows for easy text input and voice selection.

![Demo Image of the Kokoro-Podcast Interface](https://i.imgur.com/your-demo-image.png) 
*(Suggestion: Replace this link with a screenshot or GIF of your application in action!)*

---

### How It Works

The application follows a simple yet powerful pipeline:
1.  A user **inputs source text** and selects distinct voices for the "Host" and "Guest."
2.  A detailed prompt is sent to the **Gemini API**, instructing it to return a structured JSON object representing a two-person conversational script.
3.  The returned JSON is validated against a **Pydantic schema** to ensure data integrity.
4.  The application iterates through each paragraph of the script, using the **Kokoro TTS engine** to synthesize audio with the correctly assigned voice.
5.  The audio is **streamed chunk-by-chunk** to the Gradio interface, allowing for immediate playback.

---

### Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.10+**
* **Git** for cloning the repository.
* A **Gemini API Key** from Google AI Studio.

---

### Installation

Follow these steps to set up the project on your local machine.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Yusif3li/Audio_Podacast_genetator__-KOKORO-BASED-.git](https://github.com/Yusif3li/Audio_Podacast_genetator__-KOKORO-BASED-.git)
    cd Audio_Podacast_genetator__-KOKORO-BASED-
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # Create the environment
    python -m venv env1
    
    # Activate on Windows
    .\env1\Scripts\activate
    
    # Activate on macOS/Linux
    # source env1/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Your API Key:**
    * Create a file in the root directory named `.env`.
    * Open the `.env` file and add your Gemini API key like this:
        ```
        GEMINI_API_KEY=AIzaSy...your...key...here...
        ```

5.  **Install Ffmpeg:**
    * Download the latest release build from gyan.dev/ffmpeg/builds
    * Extract the archive to a permanent location
    * Add the bin folder (e.g., C:\ffmpeg\bin) to your Windows PATH environment variable.
    
---

### Usage

With your environment activated and dependencies installed, running the application is simple.

1.  **Run the Gradio App:**
    ```bash
    python app_gradio.py
    ```

2.  **Access the Interface:**
    * Open your web browser and navigate to the local URL provided in your terminal (usually `http://localhost:7860`).

> **Note:** The first time you run the application, it will download the necessary Kokoro TTS models from Hugging Face Hub. This may take a few minutes depending on your internet connection.

### License

This project is open-source. Please refer to the license of the Kokoro library (Apache 2.0) and other dependencies.
