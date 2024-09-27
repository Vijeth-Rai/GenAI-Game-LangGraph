# AI-Powered Interactive Storytelling Game

## Project Overview

This project is an innovative AI-powered interactive storytelling game that combines natural language processing, dynamic game state management, and intelligent character interactions. Players engage in a rich, evolving narrative experience guided by an AI GameMaster.

## Key Features

### 1. AI GameMaster (Chatbot)
- Facilitates user interaction through natural language conversations.
- Guides story progression and responds to user inputs.
- Manages saving checkpoints and loading previous game states.

### 2. Automated State Management
- **MongoDBSaver**: Automatically saves and updates game checkpoints.
- Creates and manages short-term and long-term memories for enhanced game continuity.

### 3. Intelligent Agents
- **EnvironmentAgent**: Creates and manages environmental memories, enriching the game world.
- **CharacterAgent**: Stores and manages character details, allowing for complex NPC interactions.
- **StatsAgent**: Maintains and updates character statistics, enabling dynamic character progression.

### 4. Dynamic Storytelling
- Allows for branching narratives based on user choices.
- Utilizes AI to create unique and personalized story experiences.

### 5. Persistent Game World
- Automatically saves game progress.
- Enables players to return to previous checkpoints for exploring different story paths.

## Technical Implementation

### Backend
- Python-based backend utilizing LangChain and LangGraph for AI processing and graph-based state management.
- MongoDB for persistent storage of game states, characters, and environments.
- Custom agents (ChatAgent, EnvironmentAgent, CharacterAgent, StatsAgent) for specialized processing.

### Frontend
- Next.js-based web interface for user interaction.
- Real-time communication between frontend and backend using Server-Sent Events (SSE).
- Tailwind CSS for styling, providing a responsive and modern UI.

### AI Integration
- Utilizes Groq API for natural language processing and generation.
- Custom prompt engineering for various game aspects (character creation, environment description, etc.).

### State Management
- Implements a sophisticated state management system using LangGraph.
- Facilitates complex decision-making and branching narratives.

## Key Components

### Chat Interface
The main interface for user interaction, handling message display, input, and state visualization.

### MongoDBSaver
Manages the saving and loading of game states, including memory management.

### EnvironmentAgent
Handles the creation and management of game environments, enhancing the game world.

### CharacterAgent
Manages character information, including the creation and retrieval of character details.

## Current Progress
- Implemented user interaction with the AI GameMaster.
- Developed an automatic checkpoint saving and memory creation system.
- Created specialized agents for environment, character, and stats management.
- Established a checkpoint management system controlled by the GameMaster.

## Future Developments
- Enhance natural language processing for more nuanced user interactions.
- Expand the game world and character roster.
- Implement more complex decision-making algorithms for the AI GameMaster.
- Develop a user interface for easier game interaction and state visualization.

This project aims to push the boundaries of AI-driven interactive storytelling, creating immersive and personalized narrative experiences for users. By combining advanced AI technologies with game design principles, it offers a unique and evolving gameplay experience that adapts to each player's choices and interactions.