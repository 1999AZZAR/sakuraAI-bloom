# SakuraAI Bloom - Setup Guide

This setup guide will walk you through the process of setting up SakuraAI Bloom on your system. Follow these steps to ensure a smooth installation and configuration.

## Folder Structure

```text
sakuraAI_Bloom/
│
├── bot/
│   ├── global_helper.py
│   ├── palmai_helper.py
│   ├── datamanager.py
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│
├── database/
│   ├── user_data.db
│
├── out/
│   ├── (Generated images from Stability API)
│
├── setup.md
├── README.md
```

## Prerequisites

Before you begin, make sure you have the following prerequisites installed on your system:

- Python (version 3.6 or higher)
- Pip (Python package installer)
- Virtualenv (optional but recommended for isolated environments)

## Installation Steps

1. **Clone the Repository:**

   Clone the SakuraAI Bloom repository to your local machine.

   ```bash
   git clone https://github.com/1999AZZAR/sakuraAI_Bloom.git
   ```

2. **Navigate to the Project Directory:**

   Change into the project directory.

   ```bash
   cd sakuraai-bloom/code
   ```

3. **Create a Virtual Environment (Optional):**

   It's recommended to use a virtual environment to isolate dependencies.

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies:**

   Install the required Python dependencies.

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables:**

   Create a `.env` file in the project root directory and add the following environment variables:

   ```env
   USER_ID=your_user_id
   ADMIN_ID=your_admin_id
   PALM_API_KEY=your_palm_api_key
   STABILITY_API_KEY=your_stability_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

   Replace `your_user_id`, `your_admin_id`, `your_palm_api_key`, `your_stability_api_key`, and `your_telegram_bot_token` with your specific values.

   - **Telegram API Key:**
     Obtain your Telegram Bot Token by creating a new bot on Telegram. Follow the instructions [here](https://core.telegram.org/bots#botfather) to create a new bot and obtain the token.

   - **Palm AI API Key:**
     Obtain your Palm AI API Key from [Google Makersuite](https://makersuite.google.com/app/apikey). Sign in with your Google account, create a project, and generate an API key for the Chat and Text models.

   - **Stability API Key:**
     Obtain your Stability API Key from [Stability AI](https://platform.stability.ai/account/keys). Log in or sign up for an account, create a project, and generate an API key.

6. **Run the Bot:**

   Start SakuraAI Bloom by running:

   ```bash
   python main.py
   ```

   The bot should now be active and ready to respond to your interactions.

7. **Interact with the Bot:**

   Interact with SakuraAI Bloom through your preferred messaging platform. Enjoy chatting, generating text, and creating images with the bot!

## Additional Configuration (Optional)

- Adjust the configuration in the `.env` file to customize the behavior of the bot.
- Explore and modify the source code in the project directory for advanced customization.

That's it! You have successfully set up SakuraAI Bloom on your system. If you encounter any issues or have questions, refer to the documentation or seek assistance from the community. Happy interacting!
