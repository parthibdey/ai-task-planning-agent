AI Task Planning Agent

description: >
    An intelligent agent that helps with task planning by breaking down natural language goals
    into actionable steps, enriching them with external information, and providing a clear
    day-by-day plan.

architecture:
  overview: "Web Interface (HTML/JS) → Flask App → AI Task Planning Agent → Task Planner → APIs & SQLite DB → Web Plans Storage"

how_it_works:
  - goal_input: "User enters a natural language goal."
  - initial_planning: "LLM (GPT-3.5) breaks down the goal into structured steps."
  - web_enrichment: "Each step is enriched with relevant web search results."
  - weather_integration: "Location-based goals receive weather forecasts."
  - plan_generation: "Complete plan is assembled with all information."
  - database_storage: "Plan is saved to SQLite database for future reference."
  - web_display: "Plan is presented in a user-friendly web interface."

setup_instructions:
  prerequisites:
    - "Python 3.8 or higher"
    - "API Keys for OpenAI API, SerpAPI, and OpenWeatherMap API"
  installation:
    steps:
      - "Clone the repository: git clone <repository-url> && cd task-planning-agent"
      - "Create a virtual environment: python -m venv venv"
      - "Activate the virtual environment:"
        windows: "venv\\Scripts\\activate"
        mac_linux: "source venv/bin/activate"
      - "Install dependencies: pip install -r requirements.txt"
      - "Create a .env file with your API keys:"
        content: |
          OPENAI_API_KEY=your-openai-key
          SERPAPI_KEY=your-serpapi-key
          WEATHER_API_KEY=your-openweather-key
      - "Run the application: python app.py"
      - "Access the web interface: http://localhost:5000"

features:
  - "Converts natural language goals into structured actionable plans."
  - "Enriches each step with web search results and external information."
  - "Integrates weather data for location-specific goals."
  - "Stores generated plans in a SQLite database."
  - "Presents plans in a clean and user-friendly web interface."

technologies:
  - "Python 3.8+"
  - "Flask"
  - "OpenAI GPT-3.5"
  - "SerpAPI"
  - "OpenWeatherMap API"
  - "SQLite"
  - "HTML/CSS/JavaScript"

license: "MIT"

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
