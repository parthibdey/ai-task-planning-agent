# AI Task Planning Agent
# Complete implementation with web interface, database storage, and external APIs

import os
from dotenv import load_dotenv
import sqlite3
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from flask import Flask, render_template, request, jsonify
import openai
from serpapi import GoogleSearch

# Configuration


load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    DATABASE_PATH = 'plans.db'

@dataclass
class PlanStep:
    step_number: int
    title: str
    description: str
    estimated_time: str
    external_info: Optional[Dict] = None

@dataclass
class Plan:
    id: Optional[int]
    goal: str
    steps: List[PlanStep]
    weather_info: Optional[Dict]
    created_at: str
    total_duration: str

class WebSearchTool:
    """Tool for web search using SerpAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web for information"""
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.api_key,
                "num": num_results
            })
            results = search.get_dict()
            
            if "organic_results" in results:
                return [
                    {
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", "")
                    }
                    for result in results["organic_results"]
                ]
            return []
        except Exception as e:
            print(f"Web search error: {e}")
            return []

class WeatherTool:
    """Tool for weather information using OpenWeatherMap API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str, days: int = 3) -> Dict:
        """Get weather forecast for a city"""
        try:
            # Current weather
            current_url = f"{self.base_url}/weather"
            current_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            current_response = requests.get(current_url, params=current_params)
            current_data = current_response.json()
            
            # Forecast
            forecast_url = f"{self.base_url}/forecast"
            forecast_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (every 3 hours)
            }
            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_data = forecast_response.json()
            
            return {
                "current": {
                    "temperature": current_data["main"]["temp"],
                    "description": current_data["weather"][0]["description"],
                    "humidity": current_data["main"]["humidity"]
                },
                "forecast": self._process_forecast(forecast_data, days)
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {"error": str(e)}
    
    def _process_forecast(self, forecast_data: Dict, days: int) -> List[Dict]:
        """Process forecast data into daily summaries"""
        if "list" not in forecast_data:
            return []
        
        daily_forecasts = []
        current_date = None
        daily_temps = []
        daily_conditions = []
        
        for item in forecast_data["list"][:days * 8]:
            date = datetime.fromtimestamp(item["dt"]).date()
            
            if current_date != date:
                if current_date is not None and daily_temps:
                    daily_forecasts.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "min_temp": min(daily_temps),
                        "max_temp": max(daily_temps),
                        "description": max(set(daily_conditions), key=daily_conditions.count)
                    })
                
                current_date = date
                daily_temps = []
                daily_conditions = []
            
            daily_temps.append(item["main"]["temp"])
            daily_conditions.append(item["weather"][0]["description"])
        
        # Add the last day
        if daily_temps:
            daily_forecasts.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "min_temp": min(daily_temps),
                "max_temp": max(daily_temps),
                "description": max(set(daily_conditions), key=daily_conditions.count)
            })
        
        return daily_forecasts

class DatabaseManager:
    """Database manager for storing and retrieving plans"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    weather_info TEXT,
                    created_at TEXT NOT NULL,
                    total_duration TEXT
                )
            ''')
            conn.commit()
    
    def save_plan(self, plan: Plan) -> int:
        """Save a plan to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO plans (goal, steps, weather_info, created_at, total_duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                plan.goal,
                json.dumps([asdict(step) for step in plan.steps]),
                json.dumps(plan.weather_info) if plan.weather_info else None,
                plan.created_at,
                plan.total_duration
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_plan(self, plan_id: int) -> Optional[Plan]:
        """Retrieve a specific plan by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM plans WHERE id = ?', (plan_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_plan(row)
            return None
    
    def get_all_plans(self) -> List[Plan]:
        """Retrieve all plans"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM plans ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            return [self._row_to_plan(row) for row in rows]
    
    def _row_to_plan(self, row) -> Plan:
        """Convert database row to Plan object"""
        id, goal, steps_json, weather_info_json, created_at, total_duration = row
        
        steps_data = json.loads(steps_json)
        steps = [PlanStep(**step_data) for step_data in steps_data]
        
        weather_info = json.loads(weather_info_json) if weather_info_json else None
        
        return Plan(
            id=id,
            goal=goal,
            steps=steps,
            weather_info=weather_info,
            created_at=created_at,
            total_duration=total_duration
        )

class TaskPlanningAgent:
    """Main AI agent for task planning"""
    
    def __init__(self, config: Config):
        self.config = config
        self.web_search = WebSearchTool(config.SERPAPI_KEY)
        self.weather = WeatherTool(config.WEATHER_API_KEY)
        self.db = DatabaseManager(config.DATABASE_PATH)
        
        # Initialize OpenAI client
        openai.api_key = config.OPENAI_API_KEY
    
    def create_plan(self, goal: str) -> Plan:
        """Create a comprehensive plan for the given goal"""
        print(f"Creating plan for goal: {goal}")
        
        # Step 1: Generate initial plan structure
        initial_plan = self._generate_initial_plan(goal)
        
        # Step 2: Enrich with web search
        enriched_steps = self._enrich_with_web_search(initial_plan["steps"], goal)
        
        # Step 3: Get weather information if location-based
        weather_info = self._get_weather_info(goal)
        
        # Step 4: Create final plan object
        plan = Plan(
            id=None,
            goal=goal,
            steps=enriched_steps,
            weather_info=weather_info,
            created_at=datetime.now().isoformat(),
            total_duration=initial_plan.get("total_duration", "Variable")
        )
        
        # Step 5: Save to database
        plan.id = self.db.save_plan(plan)
        
        return plan
    
    def _generate_initial_plan(self, goal: str) -> Dict:
        """Generate initial plan structure using LLM"""
        prompt = f"""
        Create a detailed step-by-step plan for the following goal: "{goal}"
        
        Please provide:
        1. A list of specific, actionable steps
        2. Estimated time for each step
        3. Brief description of what each step involves
        4. Total estimated duration
        
        Format your response as JSON with this structure:
        {{
            "steps": [
                {{
                    "step_number": 1,
                    "title": "Step title",
                    "description": "Detailed description",
                    "estimated_time": "X hours/minutes"
                }}
            ],
            "total_duration": "X days/hours"
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful planning assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM error: {e}")
            # Fallback plan
            return {
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Plan and Research",
                        "description": f"Research and plan for: {goal}",
                        "estimated_time": "2 hours"
                    }
                ],
                "total_duration": "1 day"
            }
    
    def _enrich_with_web_search(self, steps_data: List[Dict], goal: str) -> List[PlanStep]:
        """Enrich plan steps with web search information"""
        enriched_steps = []
        
        # General search for the goal
        search_results = self.web_search.search(goal)
        
        for step_data in steps_data:
            step = PlanStep(
                step_number=step_data["step_number"],
                title=step_data["title"],
                description=step_data["description"],
                estimated_time=step_data["estimated_time"]
            )
            
            # Search for specific information related to this step
            step_query = f"{goal} {step.title}"
            step_results = self.web_search.search(step_query, num_results=3)
            
            if step_results:
                step.external_info = {
                    "search_results": step_results[:2],  # Keep top 2 results
                    "relevant_info": [result["snippet"] for result in step_results[:2]]
                }
            
            enriched_steps.append(step)
        
        return enriched_steps
    
    def _get_weather_info(self, goal: str) -> Optional[Dict]:
        """Extract location from goal and get weather information"""
        # Simple location extraction (can be improved with NER)
        common_cities = [
            "jaipur", "hyderabad", "vizag", "visakhapatnam", "mumbai", "delhi",
            "bangalore", "chennai", "kolkata", "pune", "goa", "udaipur",
            "kerala", "rajasthan", "goa"
        ]
        
        goal_lower = goal.lower()
        for city in common_cities:
            if city in goal_lower:
                weather_data = self.weather.get_weather(city)
                if "error" not in weather_data:
                    return weather_data
                break
        
        return None
    
    def get_plan_history(self) -> List[Plan]:
        """Get all saved plans"""
        return self.db.get_all_plans()
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """Get a specific plan by ID"""
        return self.db.get_plan(plan_id)

# Flask Web Application
app = Flask(__name__)
agent = TaskPlanningAgent(Config())

@app.route('/')
def index():
    """Main page with form and plan history"""
    plans = agent.get_plan_history()
    return render_template('index.html', plans=plans)

@app.route('/create_plan', methods=['POST'])
def create_plan():
    """Create a new plan"""
    goal = request.form.get('goal')
    if not goal:
        return jsonify({"error": "Goal is required"}), 400
    
    try:
        plan = agent.create_plan(goal)
        return jsonify({
            "success": True,
            "plan_id": plan.id,
            "message": "Plan created successfully!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/plan/<int:plan_id>')
def view_plan(plan_id):
    """View a specific plan"""
    plan = agent.get_plan_by_id(plan_id)
    if not plan:
        return "Plan not found", 404
    
    return render_template('plan_detail.html', plan=plan)

@app.route('/api/plans')
def api_plans():
    """API endpoint to get all plans"""
    plans = agent.get_plan_history()
    return jsonify([asdict(plan) for plan in plans])

@app.route('/api/plan/<int:plan_id>')
def api_plan_detail(plan_id):
    """API endpoint to get a specific plan"""
    plan = agent.get_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    
    return jsonify(asdict(plan))

if __name__ == '__main__':
    
    
    print("Starting AI Task Planning Agent...")
    print("\n Server starting at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)