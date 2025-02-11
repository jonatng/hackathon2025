# Caregiver: AI-Powered Assistance for Assisted Living Facilities

Caregiver is an innovative application designed to streamline the management of assisted living facilities. It empowers administrators with AI-driven insights, efficient information retrieval, and data visualizations to enhance resident care and operational efficiency.  This README provides a comprehensive guide to the project, covering its architecture, functionalities, and setup.

## Table of Contents

*   Project Overview
*   Key Features
*   Technology Stack
*   Directory Structure
*   Backend API (`backend API`)
*   Data Analysis and Visualization (`data`)
*   Frontend Components (`front-end components`)
*   SQL Data Visualizations (`SQL`)
*   Vector Database Configuration (`Vector database configurations`)
*   Installation
*   Usage
*   Contributing
*   License

## Project Overview

Caregiver addresses the complex needs of assisted living facility management by integrating cutting-edge technologies.  At its core, Caregiver utilizes a Hugging Face Transformer-based LLM (Large Language Model) to provide intelligent assistance. This LLM, specifically the "tiny-zero" model (a distilled version of DeepSeek), powers a conversational chatbot capable of answering administrator queries, providing information about upcoming events, and retrieving resident-specific data.

The application leverages a Redis database as both a vector database and a store for conversation history.  The vector database stores crucial information about events, resident averages (e.g., dental work needs), and other relevant data. This allows the LLM to access and provide contextually relevant information. The conversation history feature enables the chatbot to maintain context and offer more personalized interactions.

Caregiver's user interface is built using Oracle Apex, a low-code development platform. Oracle Apex also hosts relational SQL databases that are used for generating insightful data visualizations related to resident health and well-being.  Furthermore, Caregiver includes a scheduled task that sends daily SMS notifications to the administrator via Twilio, informing them about upcoming events.  An interactive memory game is also included to support resident cognitive function.

## Key Features

*   **AI-Powered Assistance:**  The "tiny-zero" LLM provides intelligent responses to administrator queries, retrieves information from the vector database, and maintains conversation history.
*   **Vector Database:** Redis database stores event information, resident averages, and other critical data for quick and accurate retrieval by the LLM.
*   **Conversation History:**  Redis database stores conversation history, enabling contextual and personalized interactions.
*   **Data Visualization:** Oracle Apex and SQL queries generate visualizations of resident health and well-being data.
*   **SMS Event Notifications:** Daily SMS reminders about upcoming events are sent via Twilio.
*   **Interactive Memory Game:** A memory game is included as a cognitive exercise for residents.

## Technology Stack

*   **LLM:** Hugging Face Transformers (tiny-zero model - distilled DeepSeek)
*   **Database:** Redis
*   **Frontend:** Oracle Apex
*   **Data Visualization:** SQL (Oracle Apex)
*   **SMS Notifications:** Twilio
*   **Programming Languages:** Python, JavaScript, HTML, CSS
*   **Deployment:** Docker, Hugging Face Spaces

## Directory Structure
Caregiver/
├── backend API/
│   ├── app.py
│   ├── event_notifier.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── uwsgi.ini
│   └── .env (Not in repo)
├── data/
│   ├── *.ipynb (Jupyter Notebook)
│   └── environment.yml
├── front-end components/
│   ├── medical chatbot/
│   │   ├── index.html
│   │   ├── index.js
│   │   └── style.css
│   ├── memory game/
│   │   ├── index.html
│   │   ├── index.js
│   │   └── style.css
│   └── changing colors header/
│       ├── index.html
│       └── style.css
├── SQL/
│   ├── dental information page
│   ├── disability information page
│   ├── home page
│   └── mental distress page
├── Vector database configurations/
│   ├── init_redis.py
│   └── debug_read_redis.py
├── .gitattributes
└── .gitignore

## Backend API (`backend API`)

The `backend API` directory contains the core logic of the application, hosted on Hugging Face Spaces.

*   **`app.py`:** This Python file serves as the main application. It handles API requests, interacts with the "tiny-zero" LLM using Hugging Face Transformers, and queries the Redis database. Key endpoints include:
    *   `/api/data`:  Handles chatbot conversations, retrieves medical information, and performs vector database lookups.
    *   `/api/games/start`: Initiates the memory game.
    *   `/api/games/question`: Retrieves a question for the memory game.
    *   `/api/games/guess`: Processes user guesses in the memory game.
*   **`event_notifier.py`:** This script is responsible for sending daily SMS notifications about upcoming events using the Twilio API.
*   **`Dockerfile`:**  This file defines the Docker image used to build and deploy the backend API to Hugging Face Spaces.
*   **`requirements.txt`:** Lists all the Python dependencies required for the backend API.
*   **`runtime.txt`:** Specifies the runtime environment for the Hugging Face Space.
*   **`uwsgi.ini`:** Contains production server configurations for uWSGI, used by Hugging Face Spaces.
*   **`.env` (Not in repo):**  This file (not included in the repository for security reasons) stores environment variables, such as API keys, database credentials, and other sensitive information.

## Data Analysis and Visualization (`data`)

The `data` directory contains scripts used for data analysis and visualization.

*   **`*.ipynb` (Jupyter Notebook):** This Jupyter Notebook contains the code used to analyze the "Healthy Alzheimer's Disease and Healthy Aging Data" dataset.  It generates visualizations that are later used in the Oracle Apex frontend.
*   **`environment.yml`:**  This file specifies the conda environment used for data analysis.

## Frontend Components (`front-end components`)

This directory contains the HTML, CSS, and JavaScript files for the custom frontend components used in Oracle Apex.

*   **`medical chatbot` (directory):** Contains the files for the medical chatbot component.
    *   `index.html`:  HTML structure for the chatbot interface.
    *   `index.js`: JavaScript logic for the chatbot, including communication with the backend API.
    *   `style.css`: CSS styles for the chatbot component.
*   **`memory game` (directory):** Contains the files for the memory game component.
    *   `index.html`:  HTML structure for the memory game interface.
    *   `index.js`: JavaScript logic for the memory game.
    *   `style.css`: CSS styles for the memory game component.
*   **`changing colors header` (directory):** Contains the files for the changing colors header component.
    *   `index.html`: HTML structure for the header.
    *   `style.css`: CSS styles for the header.

## SQL Data Visualizations (`SQL`)

This directory contains the SQL queries used to generate data visualizations within Oracle Apex. Each file represents a different page or visualization. Each of the "page" files contains four SQL queries, broken down by Age, Location, Gender, and Ethnicity.

*   **`dental information page`:** Contains SQL queries to visualize dental health data.
*   **`disability information page`:** Contains SQL queries to visualize disability-related data.
*   **`home page`:** Contains SQL queries for the main dashboard visualizations.
*   **`mental distress page`:** Contains SQL queries to visualize mental health data.

## Vector Database Configuration (`Vector database configurations`)

This directory contains Python scripts for interacting with the Redis vector database.

*   **`init_redis.py`:** This script connects to the Redis database, creates the necessary vector index, and populates the database with initial data.
*   **`debug_read_redis.py`:** This script performs read operations on the Redis database to verify that data has been written correctly.

## Installation

*(Detailed instructions on setting up the project locally. This should include:)*

*   *Installing Python dependencies (`pip install -r requirements.txt`)*
*   *Setting up the Redis database*
*   *Configuring Oracle Apex (connecting to the database, importing SQL scripts, creating frontend components)*
*   *Setting up environment variables (creating the `.env` file)*
*   *Building and deploying the backend API to Hugging Face Spaces (using Docker)*

## Usage

*(Detailed instructions on how to use the application.  This should include:)*

*   *Accessing the Oracle Apex frontend*
*   *Interacting with the chatbot (asking questions, retrieving information)*
*   *Playing the memory game*
*   *Interpreting the data visualizations on the different pages*