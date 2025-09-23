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
import re

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
    day: int
    external_info: Optional[Dict] = None

@dataclass
class Plan:
    id: Optional[int]
    goal: str
    steps: List[PlanStep]
    weather_info: Optional[Dict]
    created_at: str
    total_duration: str
    days_count: int

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
                    total_duration TEXT,
                    days_count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
    
    def save_plan(self, plan: Plan) -> int:
        """Save a plan to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO plans (goal, steps, weather_info, created_at, total_duration, days_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                plan.goal,
                json.dumps([asdict(step) for step in plan.steps]),
                json.dumps(plan.weather_info) if plan.weather_info else None,
                plan.created_at,
                plan.total_duration,
                plan.days_count
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
        id, goal, steps_json, weather_info_json, created_at, total_duration, days_count = row
        
        steps_data = json.loads(steps_json)
        steps = [PlanStep(**step_data) for step_data in steps_data]
        
        weather_info = json.loads(weather_info_json) if weather_info_json else None
        
        return Plan(
            id=id,
            goal=goal,
            steps=steps,
            weather_info=weather_info,
            created_at=created_at,
            total_duration=total_duration,
            days_count=days_count or 1
        )

class TaskPlanningAgent:
    """Main AI agent for task planning"""
    
    def __init__(self, config: Config):
        self.config = config
        self.web_search = WebSearchTool(config.SERPAPI_KEY) if config.SERPAPI_KEY else None
        self.weather = WeatherTool(config.WEATHER_API_KEY) if config.WEATHER_API_KEY else None
        self.db = DatabaseManager(config.DATABASE_PATH)
        
        # Initialize OpenAI client
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
    
    def create_plan(self, goal: str) -> Plan:
        """Create a comprehensive plan for the given goal"""
        print(f"Creating plan for goal: {goal}")
        
        # Step 1: Generate initial plan structure
        initial_plan = self._generate_initial_plan(goal)
        
        # Step 2: Enrich with web search
        enriched_steps = self._enrich_with_web_search(initial_plan["steps"], goal)
        
        # Step 3: Get weather information if location-based
        weather_info = self._get_weather_info(goal, initial_plan.get("days_count", 1))
        
        # Step 4: Create final plan object
        plan = Plan(
            id=None,
            goal=goal,
            steps=enriched_steps,
            weather_info=weather_info,
            created_at=datetime.now().isoformat(),
            total_duration=initial_plan.get("total_duration", "Variable"),
            days_count=initial_plan.get("days_count", 1)
        )
        
        # Step 5: Save to database
        plan.id = self.db.save_plan(plan)
        
        return plan
    
    def _estimate_days_from_goal(self, goal: str) -> int:
        """Estimate number of days based on goal keywords"""
        goal_lower = goal.lower()
        
        # Look for explicit day mentions
        day_patterns = [
            r'(\d+)\s*day', r'(\d+)-day', r'day\s*(\d+)',
            r'(\d+)\s*week', r'week\s*(\d+)'
        ]
        
        for pattern in day_patterns:
            match = re.search(pattern, goal_lower)
            if match:
                days = int(match.group(1))
                if 'week' in pattern:
                    days *= 7
                return min(days, 7)  # Cap at 7 days
        
        # Estimate based on activity type
        if any(word in goal_lower for word in ['tour', 'trip', 'visit', 'explore', 'vacation', 'holiday']):
            return 3
        elif any(word in goal_lower for word in ['weekend', 'quick', 'short']):
            return 2
        elif any(word in goal_lower for word in ['learn', 'course', 'training', 'workshop']):
            return 5
        else:
            return 1
    
    def _generate_initial_plan(self, goal: str) -> Dict:
        """Generate initial plan structure using LLM"""
        days_count = self._estimate_days_from_goal(goal)
        
        prompt = f"""
        Create a detailed step-by-step plan for the following goal: "{goal}"
        
        The plan should be organized across {days_count} day(s). Each step should be practical and actionable.
        
        Please provide:
        1. A list of specific, actionable steps distributed across days
        2. Estimated time for each step
        3. Brief description of what each step involves
        4. Which day each step belongs to
        5. Total estimated duration
        
        Format your response as JSON with this structure:
        {{
            "days_count": {days_count},
            "steps": [
                {{
                    "step_number": 1,
                    "title": "Step title",
                    "description": "Detailed description with specific recommendations",
                    "estimated_time": "2 hours",
                    "day": 1
                }}
            ],
            "total_duration": "{days_count} days"
        }}
        
        Make sure steps are distributed evenly across the {days_count} day(s) and include specific places, activities, or recommendations where relevant.
        """
        
        try:
            if self.config.OPENAI_API_KEY:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful planning assistant who creates detailed, day-by-day itineraries. Always respond with valid JSON and include specific recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                return json.loads(content)
            else:
                # Fallback without OpenAI API
                return self._generate_fallback_plan(goal, days_count)
                
        except Exception as e:
            print(f"LLM error: {e}")
            return self._generate_fallback_plan(goal, days_count)
    
    def _generate_fallback_plan(self, goal: str, days_count: int) -> Dict:
        """Generate a fallback plan when LLM is not available"""
        steps = []
        step_num = 1
        
        for day in range(1, days_count + 1):
            if day == 1:
                steps.extend([
                    {
                        "step_number": step_num,
                        "title": "Research and Planning",
                        "description": f"Research best options and create detailed plan for: {goal}",
                        "estimated_time": "2 hours",
                        "day": day
                    },
                    {
                        "step_number": step_num + 1,
                        "title": "Initial Setup/Preparation",
                        "description": f"Prepare necessary materials and setup for: {goal}",
                        "estimated_time": "1.5 hours",
                        "day": day
                    }
                ])
                step_num += 2
            else:
                steps.append({
                    "step_number": step_num,
                    "title": f"Day {day} Activities",
                    "description": f"Continue with planned activities for: {goal}",
                    "estimated_time": "4 hours",
                    "day": day
                })
                step_num += 1
        
        return {
            "days_count": days_count,
            "steps": steps,
            "total_duration": f"{days_count} days"
        }
    
    def _enrich_with_web_search(self, steps_data: List[Dict], goal: str) -> List[PlanStep]:
        """Enrich plan steps with web search information"""
        enriched_steps = []
        
        if not self.web_search:
            # Return steps without web search enrichment
            for step_data in steps_data:
                step = PlanStep(
                    step_number=step_data["step_number"],
                    title=step_data["title"],
                    description=step_data["description"],
                    estimated_time=step_data["estimated_time"],
                    day=step_data.get("day", 1)
                )
                enriched_steps.append(step)
            return enriched_steps
        
        # General search for the goal
        search_results = self.web_search.search(goal)
        
        for step_data in steps_data:
            step = PlanStep(
                step_number=step_data["step_number"],
                title=step_data["title"],
                description=step_data["description"],
                estimated_time=step_data["estimated_time"],
                day=step_data.get("day", 1)
            )
            
            # Search for specific information related to this step
            step_query = f"{goal} {step.title}"
            step_results = self.web_search.search(step_query, num_results=3)
            
            if step_results:
                # Extract useful information from search results
                relevant_info = []
                for result in step_results[:2]:
                    snippet = result.get("snippet", "")
                    if snippet:
                        # Clean and format the snippet
                        clean_snippet = snippet.replace("\n", " ").strip()
                        if len(clean_snippet) > 100:
                            clean_snippet = clean_snippet[:100] + "..."
                        relevant_info.append(clean_snippet)
                
                step.external_info = {
                    "search_results": step_results[:2],
                    "relevant_info": relevant_info
                }
            
            enriched_steps.append(step)
        
        return enriched_steps
    
    def _get_weather_info(self, goal: str, days_count: int) -> Optional[Dict]:
        """Extract location from goal and get weather information"""
        if not self.weather:
            return None
            
        # Enhanced location extraction
        indian_cities = [
            "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", 
            "kolkata", "pune", "ahmedabad", "jaipur", "surat", "lucknow",
            "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam",
            "vizag", "pimpri", "patna", "vadodara", "ghaziabad", "ludhiana",
            "agra", "nashik", "faridabad", "meerut", "rajkot", "kalyan",
            "vasai", "varanasi", "srinagar", "aurangabad", "dhanbad",
            "amritsar", "navi mumbai", "allahabad", "prayagraj", "ranchi",
            "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada",
            "jodhpur", "madurai", "raipur", "kota", "guwahati", "chandigarh",
            "solapur", "hubli", "dharwad", "bareilly", "moradabad", "mysore",
            "mysuru", "gurgaon", "gurugram", "aligarh", "jalandhar", "tiruchirappalli",
            "bhubaneswar", "salem", "warangal", "mira", "bhayandar", "thiruvananthapuram",
            "bhiwandi", "saharanpur", "gorakhpur", "guntur", "bikaner", "amravati",
            "noida", "jamshedpur", "bhilai", "cuttack", "firozabad", "kochi",
            "nellore", "bhavnagar", "dehradun", "durgapur", "asansol", "rourkela",
            "nanded", "kolhapur", "ajmer", "akola", "gulbarga", "jamnagar",
            "ujjain", "loni", "siliguri", "jhansi", "ulhasnagar", "jammu",
            "sangli", "miraj", "kupwad", "belgaum", "mangalore", "ambattur",
            "tirunelveli", "malegaon", "gaya", "jalgaon", "udaipur", "maheshtala",
            "goa", "panaji", "margao", "kerala", "kottayam", "thrissur",
            "rajasthan", "udaipur", "mount abu", "pushkar", "rishikesh",
            "haridwar", "shimla", "manali", "dharamshala", "mcleodganj",
            "kasauli", "mussoorie", "nainital", "jim corbett", "corbett",
            "darjeeling", "gangtok", "shillong", "ooty", "kodaikanal",
            "munnar", "alleppey", "kumarakom", "hampi", "gokarna", "pondicherry",
            "puducherry", "mahabalipuram", "kanyakumari", "rameswaram",
            "agartala", "imphal", "aizawl", "kohima", "itanagar"
        ]
        
        goal_lower = goal.lower()
        detected_city = None
        
        for city in indian_cities:
            if city in goal_lower:
                detected_city = city
                break
        
        if detected_city:
            weather_data = self.weather.get_weather(detected_city, days=days_count)
            if "error" not in weather_data:
                return {**weather_data, "location": detected_city.title()}
        
        return None
    
    def get_plan_history(self) -> List[Plan]:
        """Get all saved plans"""
        return self.db.get_all_plans()
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """Get a specific plan by ID"""
        return self.db.get_plan(plan_id)
    
    def format_plan_display(self, plan: Plan) -> str:
        """Format plan for display with day-by-day structure"""
        output = []
        
        # Group steps by day
        steps_by_day = {}
        for step in plan.steps:
            day = step.day
            if day not in steps_by_day:
                steps_by_day[day] = []
            steps_by_day[day].append(step)
        
        # Format each day
        for day in sorted(steps_by_day.keys()):
            output.append(f"Day {day}:")
            
            for step in steps_by_day[day]:
                output.append(f"{step.step_number}. {step.title} ({step.estimated_time})")
                output.append(f"   - {step.description}")
                
                if step.external_info and step.external_info.get('relevant_info'):
                    for info in step.external_info['relevant_info']:
                        output.append(f"   - External Info: {info}")
                
                output.append("")  # Add blank line
        
        return "\n".join(output)

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
            "message": "Plan created successfully!",
            "formatted_plan": agent.format_plan_display(plan)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/plan/<int:plan_id>')
def view_plan(plan_id):
    """View a specific plan"""
    plan = agent.get_plan_by_id(plan_id)
    if not plan:
        return "Plan not found", 404
    
    formatted_plan = agent.format_plan_display(plan)
    return render_template('plan_detail.html', plan=plan, formatted_plan=formatted_plan)

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
    
    return jsonify({
        **asdict(plan),
        "formatted_display": agent.format_plan_display(plan)
    })

if __name__ == '__main__':
    print("Starting AI Task Planning Agent...")
    print("\n Server starting at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)