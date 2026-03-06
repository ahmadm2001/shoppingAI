# AI Final Project - Shopping Website

This repository contains the source code for a full end-to-end shopping website with AI capabilities, developed as a final project. The application is built with a modern Python stack, featuring a FastAPI backend, a Streamlit frontend, and several AI/ML integrations.

## Project Overview

The goal of this project is to create a functional e-commerce platform that mimics the core functionalities of popular sites like Amazon or eBay, with a strong emphasis on backend logic and AI-powered features rather than UI/UX design.

### Core Features

*   **Product Catalog & Search:** Browse and search for products with advanced filtering by name, price, and stock levels.
*   **User Authentication:** Secure user registration, login, and session management using JWT.
*   **Shopping Cart & Orders:** A persistent pending order (cart) system, allowing users to add, remove, and update item quantities before purchase.
*   **Order History:** View past orders.
*   **Favorites List:** Users can save items to a personal favorites list.
*   **AI Chat Assistant:** An integrated chatbot powered by the ChatGPT API that can answer questions about products.
*   **Stock Management:** The system automatically tracks and updates stock levels upon purchase.
*   **Supervised Learning (Bonus):** Two ML models are included:
    1.  A regression model to predict user spending.
    2.  A classification model to predict user churn.

---

## Technology Stack

The project is fully containerized using Docker and orchestrated with Docker Compose.

| Component         | Technology                               |
| ----------------- | ---------------------------------------- |
| **Backend**       | Python 3.11, FastAPI, SQLAlchemy        |
| **Frontend**      | Python 3.11, Streamlit                   |
| **Database**      | MySQL 8.0                                |
| **Caching**       | Redis 7                                  |
| **AI Chat**       | OpenAI API (ChatGPT)                     |
| **ML Models**     | Scikit-learn (RandomForest)              |
| **Containerization**| Docker & Docker Compose                  |

### Project Logic & Architecture

The application follows a microservices-oriented architecture, with separate containers for the backend, frontend, database, and cache.

*   **Backend (FastAPI):** A robust API server that handles all business logic. It follows a clean MVC-like pattern with:
    *   `routers`: Defines API endpoints.
    *   `services`: Contains the core business logic for each resource (items, users, orders, etc.).
    *   `models`: Defines SQLAlchemy database models.
    *   `schemas`: Defines Pydantic data validation models.
    *   `config`: Manages application settings and database connections.
    *   `utils`: Holds utility functions like security and enums.

*   **Frontend (Streamlit):** A simple and interactive user interface that consumes the backend API. The UI is divided into pages for a modular and organized structure.

*   **Database (MySQL):** Stores all persistent data, including users, items, orders, and favorites.

*   **Cache (Redis):** Used for two main purposes:
    1.  Caching the list of all items to reduce database load.
    2.  Storing chat session history and prompt counts for the AI assistant.

*   **ML Models (Scikit-learn):** The trained models are saved as `.pkl` files and loaded by the backend to provide predictions through a dedicated API endpoint.

---

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose
*   An OpenAI API key (for the chat assistant)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd shopping-website
    ```

2.  **Create an environment file:**
    Copy the `.env.example` file to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```

3.  **Configure your environment:**
    Open the `.env` file and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your-openai-api-key-here
    ```

4.  **Build and run the application:**
    Use Docker Compose to build and start all the services in detached mode.
    ```bash
    docker-compose up --build -d
    ```

### Accessing the Application

Once the containers are running, you can access the different parts of the application:

*   **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)
*   **Backend API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Running the ML Training Script

The repository includes the scripts to generate the dataset and train the ML models. The trained models are already included, but you can retrain them if you wish.

1.  **Generate the dataset:**
    ```bash
    docker-compose exec backend python ml_model/generate_dataset.py
    ```

2.  **Train the models:**
    ```bash
    docker-compose exec backend python ml_model/train_model.py
    ```

---

## Final Notes

*   The system is seeded with 15 initial products upon startup.
*   User passwords are encrypted using bcrypt.
*   The AI chat assistant has a limit of 5 prompts per session to manage API costs.
*   The project is designed for educational purposes and demonstrates a wide range of modern development practices.
