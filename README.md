# SakuraAI Bloom

SakuraAI Bloom is an advanced chatbot with versatile capabilities, designed to enhance your interactive experiences. The bot incorporates various modules to facilitate conversations, generate creative content, and manage user-specific data. Below is a detailed overview of the components that constitute SakuraAI Bloom.

## Table of Contents

1. [Introduction](#introduction)
2. [Features and Details](#features-and-details)
    - [Text Generation and chat  Module](#text-generation-module-chat-module)
    - [Image Generation Module](#image-generation-module)
    - [User Data Management](#user-data-management)
3. [Setup](#setup)
4. [Usage](#usage)
5. [Flowchart](#flowchart)
6. [Folder Structure](#folder-scructure)
7. [Contributing](#contributing)
8. [License](#license)
9. [Example](#example)

## Introduction

SakuraAI Bloom is powered by advanced AI models and designed to operate seamlessly in various scenarios. It provides an interactive and creative environment for users to engage with, offering features such as chat, text generation, and image creation. Additionally, the bot efficiently manages user-specific data, ensuring a personalized experience.

## Features and Details

### Text Generation Module Chat Module

SakuraAI Bloom's chat module enables natural and dynamic conversations. It leverages state-of-the-art language models to understand and respond contextually to user inputs. The chat module supports multi-turn conversations, making interactions more engaging.

With the text generation module, SakuraAI Bloom can generate creative and contextually relevant text based on user prompts. Whether you need a story, poem, or any other textual content, this module delivers diverse and imaginative results.

The text generation module generates creative and contextually relevant text based on user prompts uses advanced language models to engage in dynamic conversations. It understands context and responds intelligently to user inputs. Explore different styles and themes by interacting with the bot. For implementation details, see [palmai_helper.py](bot/palmai_helper.py).

### Image Generation Module

The image generation module allows SakuraAI Bloom to create visually stunning images based on provided prompts. Users can explore various styles and themes, enhancing their visual content creation experience.

SakuraAI Bloom's image generation module creates visually appealing images based on user prompts. Users can experiment with various styles for unique visual content. Implementation details can be found in [global_helper.py](bot/global_helper.py).

### User Data Management

SakuraAI Bloom efficiently manages user-specific data through the user data management module. This includes storing and retrieving user interactions and preferences, creating a personalized experience for each user.

The user data management module efficiently stores and retrieves user-specific data. It ensures a personalized experience by managing interactions and preferences. Refer to [datamanager.py](bot/datamanager.py) for implementation details.

## Setup

To set up SakuraAI Bloom, follow the instructions in the [SETUP.md](SETUP.md) file. This guide provides step-by-step instructions to ensure a smooth installation process.

## Usage

To use SakuraAI Bloom, interact with it through your preferred messaging platform. Simply start a conversation, provide prompts for text or image generation, and enjoy the personalized and creative responses.

## Flowchart

```mermaid
graph TD

subgraph User
  A[User Interaction] -->|Sends message or command| B[Bot]
end

subgraph Bot
  B -->|Processes message| C{Command?}
  C -- No --> D[Chat Generation]
  C -- Yes --> E{Specific Command?}
  E -- Yes --> F[Execute Command]
  E -- No --> G[Handle Unknown Command]
  F -->|Generate Text, Images, or Perform Action| H[Generate Response]
end

subgraph Database
  H --> I[Store Data in SQLite]
end

subgraph External APIs
  B -->|Utilizes Palm API| J{Text Generation or Chat}
  B -->|Utilizes Stability API| K{Image Generation}
end

subgraph Logging
  D -->|Log Interactions| L[Log]
  E -->|Log Commands| L
  F -->|Log Command Execution| L
end

subgraph User Output
  H -->|Send Response| A
end
```

This flowchart represents the flow of interactions within the SakuraAI Bloom bot. Here's a breakdown of the flow:

1.User Interaction:

- The user sends a message or command to the bot.

2.Bot Processing:

- The bot processes the incoming message.
- Checks if the message contains a command.

3.Chat Generation:

- If it's a regular chat message, the bot generates a response using its chat generation capabilities.

4.Command Processing:

- If the message contains a command:
- Checks if it's a specific command.

5.Execute Command:

- If it's a specific command, the bot executes the corresponding action.

6.Handle Unknown Command:

- If the command is unknown, the bot handles it appropriately.

7.Database Interaction:

- The bot stores relevant data in an SQLite database.

8.External APIs:

- The bot utilizes external APIs (Palm API for text-related tasks and Stability API for image generation).

9.Logging:

- Logs interactions, commands, and command execution for debugging and analysis.

10.User Output:

- The bot generates a response and sends it back to the user.
This flowchart illustrates the key steps and interactions in the operation of SakuraAI Bloom.

## Folder Scructure

```c#
sakuraAI_Bloom/
│
├── bot/
│   ├── global_helper.py
│   ├── palmai_helper.py
│   ├── datamanager.py
│   ├── main.py
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

## Contributing

We welcome contributions to SakuraAI Bloom. If you have ideas for new features, improvements, or bug fixes, please check our [Contribution Guidelines](CONTRIBUTING.md).

## License

SakuraAI Bloom is licensed under the [GPL-3.0 License](LICENSE).

Feel free to explore, engage, and contribute to make SakuraAI Bloom even better!

## Example

Explore SakuraAI Bloom in action on [Telegram](https://t.me/SakuraAI_bot). Engage in dynamic conversations, generate creative text, and experiment with image creation. Enjoy the personalized and imaginative responses!
