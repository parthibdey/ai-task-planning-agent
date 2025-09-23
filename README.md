AI Task Planning Agent
An intelligent agent that helps with task planning by breaking down natural language goals into actionable steps, enriching them with external information, and providing a clear day-by-day plan.

Architecture Overview
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │ ── │ Flask Application│ ── │ Task Planning   │
│   (HTML/JS)     │    │                  │    │ Agent (Core)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                        ┌────────────────────────────────┼─────────────────┐
                        │                                │                 │
                ┌───────▼────────┐              ┌───────▼───────┐  ┌──────▼──────┐
                │ Web Search API │              │ Weather API   │  │ SQLite DB   │
                │  (SerpAPI)     │              │(OpenWeatherMap│  │ (Plans      │
                └────────────────┘              └───────────────┘  │ Storage)    │
                                                                   └─────────────┘

How It Works

Goal Input: User enters a natural language goal
Initial Planning: LLM (GPT-3.5) breaks down the goal into structured steps
Web Enrichment: Each step is enriched with relevant web search results
Weather Integration: Location-based goals get weather forecasts
Plan Generation: Complete plan is assembled with all information
Database Storage: Plan is saved to SQLite database for future reference
Web Display: Plan is presented in a user-friendly web interface

Setup Instructions
Prerequisites

Python 3.8 or higher
API Keys for:

OpenAI API
SerpAPI (for web search)
OpenWeatherMap API



Installation

1) Clone the repository:

git clone <your-repo-url>
cd task-planning-agent

2) Create virtual environment:

python -m venv venv
venv\Scripts\activate

3) Install dependencies:

pip install -r requirements.txt

4) Create a .env file:

OPENAI_API_KEY=your-openai-key-here
SERPAPI_KEY=your-serpapi-key-here
WEATHER_API_KEY=your-openweather-key-here

5) Run the application:

python app.py

6) Access the web interface: Open your browser and go to 
http://localhost:5000


📋 Example Goals and Generated Plans
Example 1: "Plan a 2-day vegetarian food tour in Hyderabad"
Generated Plan:
🎯 Goal: Plan a 2-day vegetarian food tour in Hyderabad
📅 Total Duration: 2 days
🌤️ Weather: 28°C, partly cloudy

Day 1:
1. Morning Food Market Visit (2 hours)
   - Visit Begum Bazaar for traditional ingredients
   - External Info: Famous for spices, dry fruits, and local produce
   
2. Traditional South Indian Breakfast (1.5 hours)
   - Try dosa, idli, and vada at Chutneys Restaurant
   - External Info: Award-winning restaurant known for authentic flavors

3. Afternoon Heritage Food Walk (3 hours)
   - Explore Old City food lanes
   - External Info: Historic area with 400-year-old food traditions

4. Dinner at Vegetarian Fine Dining (2 hours)
   - Experience modern take on traditional cuisine
   - External Info: Innovative restaurants like Ohri's offer fusion vegetarian

Day 2:
5. Street Food Tour - Charminar Area (2.5 hours)
   - Sample local street snacks and sweets
   - External Info: Famous for haleem, biryani alternatives, and sweets

6. Cooking Class Experience (3 hours)
   - Learn to prepare Hyderabadi vegetarian dishes
   - External Info: Several institutes offer hands-on cooking experiences
Example 2: "Organize a 5-step daily study routine for learning Python"
Generated Plan:
🎯 Goal: Organize a 5-step daily study routine for learning Python
📅 Total Duration: Ongoing (daily routine)

Daily Routine:
1. Morning Theory Study (45 minutes)
   - Read Python concepts and documentation
   - External Info: Python.org official tutorial recommended for beginners
   
2. Interactive Coding Practice (60 minutes)
   - Work on coding exercises and challenges
   - External Info: Platforms like HackerRank and LeetCode offer Python problems

3. Project-Based Learning (90 minutes)