# AI Task Planning Agent

**Description:**  
An intelligent agent that helps with **task planning** by breaking down natural language goals into actionable steps, enriching them with external information, and providing a clear day-by-day plan.

---

## Architecture Overview
Web Interface (HTML/JS) → Flask App → AI Task Planning Agent → Task Planner → APIs & SQLite DB → Web Plans Storage

## How It Works

1. **Goal Input:**  
   User enters a natural language goal.

2. **Initial Planning:**  
   LLM (GPT-3.5) breaks down the goal into structured steps.

3. **Web Enrichment:**  
   Each step is enriched with relevant web search results.

4. **Weather Integration:**  
   Location-based goals receive weather forecasts.

5. **Plan Generation:**  
   Complete plan is assembled with all information.

6. **Database Storage:**  
   Plan is saved to SQLite database for future reference.

7. **Web Display:**  
   Plan is presented in a user-friendly web interface.

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher  
- API Keys for:  
  - OpenAI API  
  - SerpAPI (for web search)  
  - OpenWeatherMap API  

### Installation

1. **Clone the repository**  
  ```bash
git clone https://github.com/parthibdey/ai-task-planning-agent.git
cd task-planning-agent
```
2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  #on windows
```
3. **Install dependencies:**
```bash
pip install -r requirements.txt
```
4. **create a .env file:**
```bash
OPENAI_API_KEY=openai-key-here
SERPAPI_KEY=serpapi-key-here
WEATHER_API_KEY=yopenweather-key-here
```
5. **Run the application:**
```bash
python app.py
```
6. **Access the web interface: Open your browser and go to**
http://localhost:5000

## Features

- Converts natural language goals into structured actionable plans.  
- Enriches each step with web search results and external information.  
- Integrates weather data for location-specific goals.  
- Stores generated plans in a SQLite database.  
- Presents plans in a clean and user-friendly web interface.  

---

## Technologies Used

- Python 3.8+  
- Flask  
- OpenAI GPT-3.5  
- SerpAPI  
- OpenWeatherMap API  
- SQLite  
- HTML/CSS/JavaScript  



## Example Goals and Generated Plans

**Example 1: "Plan a 2-day vegetarian food tour in Hyderabad"**

*Goal: Plan a 2-day vegetarian food tour in Hyderabad*

*Generated Plan:*


<img width="1345" height="883" alt="image" src="https://github.com/user-attachments/assets/63e8d2d1-eb5d-4bd6-ba50-1a8f70ed5160" />

<img width="1342" height="896" alt="image" src="https://github.com/user-attachments/assets/04bf0263-2e81-4009-a668-4432ce263942" />

<img width="1339" height="865" alt="image" src="https://github.com/user-attachments/assets/dec1ac8a-411d-405c-8ec1-4af326695f34" />

<img width="1492" height="947" alt="image" src="https://github.com/user-attachments/assets/1c05ca0b-98ca-4f7d-ae41-9999e85ba114" />



**Example 2: "Organize a 5-step daily study routine for learning Python"**

*Generated Plan:*

*Goal: Organize a 5-step daily study routine for learning Python*


<img width="1499" height="938" alt="image" src="https://github.com/user-attachments/assets/ac78488e-f5b2-4953-94bf-a30948cef67b" />

<img width="1576" height="954" alt="image" src="https://github.com/user-attachments/assets/1f83b631-8949-47d3-afb5-dacd1967fef9" />

<img width="1562" height="935" alt="image" src="https://github.com/user-attachments/assets/075bee51-bd2e-4fb5-b65f-f9e1649145f5" />



