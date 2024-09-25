<div align="center">
  <a href="http://neuralnet.solutions" target="_blank">
    <img width="450" src="https://raw.githubusercontent.com/NeuralNet-Hub/assets/main/logo/LOGO_png_orig.png">
  </a>
</div>

# ChatBot for Telegram by NeuralNet

Welcome to the ChatBot for Telegram repository! This repository contains a chatbot designed to work seamlessly with Telegram using various utilities for authentication, chat management, and user management.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Support](#support)
- [Contact](#contact)
- [License](#license)

## Features

This repository includes:

- **AuthManager**: Handles authentication processes such as signup and JWT token management.
- **ChatManager**: Manages chat sessions, including creating new chats, updating chat history, and generating chat completions.
- **UserManager**: Manages user data, including fetching, creating, and updating users in the database.
- **Telegram Integration**: Utilizes the Python Telegram Bot library to handle commands and messages.

## Installation

### Prerequisites

Ensure you have Docker and Docker Compose installed. You can verify the installation by running:

```bash
docker --version
docker compose --version
```

### Setup

1. Clone the repository.

```bash
git clone https://github.com/your-username/chatbot-telegram.git
cd chatbot-telegram
```

2. Create a `.env` file in the root directory and populate it with the necessary environment variables.

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
BOT_TOKEN=your_telegram_bot_token
BASE_URL=your_base_url
PRIVATEGPT_ADMIN_TOKEN=your_privategpt_admin_token
```

3. Build and start the Docker containers.

```bash
docker-compose -f docker-compose-telegram.yml up -d --build --force-recreate
```

## Usage

### Starting the Bot

Once the Docker containers are up and running, the chatbot will be active on Telegram. You can use the following commands:

- `/start` - Initiates the chat with the bot.
- `/models` - Provides information about the available models.
- `/login <jwt_token>` - Logs in a user with a provided JWT token.
- `/new_chat` - Creates a new chat session.
- Sending any text message will generate a response from the chatbot.

### Example Python Code

Here are some snippets demonstrating how different components of the chatbot can be used:

#### Initializing the ChatBot

```python
from bot.clientbot import ChatBot, AuthManager, ChatManager, UserManager
from bot.dbmanager import DatabaseManager

dbmanager = DatabaseManager(
    dbname="your_db_name",
    user="your_db_user",
    password="your_db_password",
    host="your_db_host",
    port="your_db_port"
)

auth_manager = AuthManager(base_url="your_base_url")
chat_manager = ChatManager(
    base_url="your_base_url",
    model="gpt-3.5-turbo",
    num_ctx=8192,
    max_tokens=4096
)
user_manager = UserManager(dbmanager=dbmanager)

bot = ChatBot(
    dbmanager=dbmanager,
    token="your_privategpt_admin_token",
    base_url="your_base_url"
)
```

## Contributing

We welcome contributions from the community! Here's how you can help:

1. Fork the repository.
2. Create a new branch: `git checkout -b my-feature-branch`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin my-feature-branch`.
5. Submit a pull request.

Please make sure your code follows our [contribution guidelines](CONTRIBUTING.md).

## Support

If you run into any issues or have questions, feel free to open an issue on GitHub or contact us directly via email.

## Contact

NeuralNet  
Website: [https://neuralnet.solutions](https://neuralnet.solutions)  
Email: info[at]neuralnet.solutions

## License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
