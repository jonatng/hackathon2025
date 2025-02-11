# Caregiver: AI-Powered Assistance for Assisted Living Facilities

Caregiver is an innovative AI-driven application designed to optimize the management of **assisted living facilities**. By integrating **conversational AI**, **vector search technology**, **data visualization**, and **real-time event notifications**, Caregiver empowers facility administrators with **intelligent insights** and **enhanced operational efficiency**. The application is designed to provide **accurate medical guidance, streamlined event tracking, and engaging cognitive exercises** for residents.

This README provides an in-depth guide to the **architecture, features, and setup** of the Caregiver system.

---

## **Table of Contents**

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Backend API (`backend-api`)](#backend-api)
- [Data Analysis and Visualization (`data`)](#data-analysis-and-visualization)
- [Frontend Components (`frontend-components`)](#frontend-components)
- [SQL Data Visualizations (`SQL`)](#sql-data-visualizations)
- [Vector Database Configuration (`vector-database-configurations`)](#vector-database-configuration)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## **Project Overview**

Caregiver is built to address the **complex needs** of **assisted living facilities** by offering a combination of **AI-powered assistance**, **event tracking**, and **data visualization**. The application features a conversational **chatbot** powered by **Hugging Face Transformers**, which allows administrators to retrieve **medical information, resident statistics, and facility updates** through natural language queries.

Additionally, the system integrates **Redis** as a **vector database** and a **conversation history store**, ensuring that AI responses remain **contextually relevant**.

Key **functional components** include:

- **Conversational AI assistant** for medical and facility-related queries
- **Real-time event notifications** sent via **Twilio SMS**
- **Dynamic SQL-based data visualizations** in **Oracle APEX**
- **An interactive memory game** designed to engage residents cognitively

The Caregiver **frontend** is built using **Oracle APEX**, which provides **SQL-driven dashboards** for administrators to monitor resident health trends and facility operations.

---

## **Key Features**

- **AI-Powered Assistance:** Uses **TinyZero (a Hugging Face model)** to provide medical insights and facility-related information.
- **Vector Database (Redis):** Stores event data and health statistics for efficient AI retrieval.
- **Conversation History:** Enables contextual, personalized AI interactions.
- **Data Visualization:** SQL-based dashboards in **Oracle APEX** present key health metrics.
- **SMS Notifications:** Daily event reminders sent via **Twilio API**.
- **Interactive Memory Game:** AI-powered historical guessing game to engage residents.

---

## **Technology Stack**

- **LLM:** Hugging Face Transformers (**TinyZero model**, distilled from DeepSeek R1 Zero)
- **Database:** Redis (Vector database + Key-Value store for chatbot memory)
- **Frontend:** Oracle APEX
- **Data Visualization:** SQL queries (Oracle APEX dashboards)
- **Event Notifications:** Twilio API (SMS reminders)
- **Programming Languages:** Python, JavaScript, HTML, CSS
- **Deployment:** Docker, Hugging Face Spaces

---

## **Directory Structure**

```
Caregiver/
├── backend-api/
│   ├── app.py
│   ├── event_notifier.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── uwsgi.ini
│   └── .env (Not in repo)
├── data/
│   ├── Healthy_Aging.ipynb (Jupyter Notebook for analysis)
│   ├── environment.yml
├── frontend-components/
│   ├── changing-colors-header/
│   ├── medical-chatbot/
│   ├── memory-game/
├── SQL/
│   ├── dental_information_page.sql
│   ├── disability_information_page.sql
│   ├── home_page.sql
│   ├── mental_distress_page.sql
├── vector-database-configurations/
│   ├── init_redis.py
│   ├── debug_read_redis.py
└── .gitignore
```

---

## **Backend API (`backend-api`)**

The **backend API** is hosted on **Hugging Face Spaces** and serves as the **core logic layer**. It interacts with the **AI model, Redis database, and Twilio API** to provide real-time responses and event notifications.

### **Key Components:**

- **`app.py`**
  - Handles API requests
  - Integrates with the **LLM (TinyZero or Minstrel)** for medical chatbot functionality
  - Queries the Redis vector database for event lookups
  - Key API endpoints:
    - `/api/data`: AI-powered medical & facility chatbot
    - `/api/games/start`: Starts the **Memory Game**
    - `/api/games/question`: Fetches historical clues from the AI
    - `/api/games/guess`: Processes user guesses

- **`event_notifier.py`**
  - Queries the Redis vector database for upcoming events
  - Sends **daily SMS reminders** to administrators using **Twilio API**

---

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/caregiver.git
   cd caregiver
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Redis database and initialize vectors:
   ```bash
   python vector-database-configurations/init_redis.py
   ```
4. Configure Oracle APEX frontend & import SQL scripts.

---

## **Usage**

- Access the **Oracle APEX frontend**.
- Use the **AI chatbot** for facility & medical queries.
- View **real-time data visualizations**.
- Receive **SMS notifications** for upcoming events.
- Engage residents with the **Memory Game**.

---

## **Conclusion**

Caregiver provides an **AI-powered, data-driven** solution for assisted living facilities. The integration of **LLMs, vector search, SQL dashboards, and real-time notifications** makes it a **powerful tool** for facility management.

🚀 *For future production deployment, we would optimize by integrating TinyZero to minimize compute costs.*
