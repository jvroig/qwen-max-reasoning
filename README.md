# Qwen-Max with Reasoning
## Overview

Just a super short demo to show how to add reasoning behavior to any non-reasoning model.

Very useful for agentic systems - being able to inject reasoning in the stages that need it - and only the stages that need it!

### Installation

To get started with this project, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/jvroig/qwen-max-reasoning.git
   cd qwen-max-reasoning

2. **Run the Backend API Server**

    ```bash
    python setup.py #this will install dependencies and create start.sh file
    bash start.sh #this will start the API server
    ```
    This will start the Python backend server on http://localhost:5001.

### Access the Web Interface

In your file browser, double-click the file index.html to load the chat interface in your default browser.

In this demo, reasoning is always triggered, as this code is just to show emulation of reasoning behavior.

In a real production app, you would apply reasoning selectively as needed.