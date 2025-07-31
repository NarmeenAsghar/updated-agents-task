import os
from dotenv import load_dotenv
from typing import cast, List, Dict, Any
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import json
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Career Fields and Data
FIELDS = [
    "software engineering",
    "finance", 
    "medical"
]

FIELD_DESCRIPTIONS = {
    "software engineering": "💻 Software Engineering is a dynamic field focused on designing, developing, and maintaining software applications. It combines technical expertise with problem-solving skills to create innovative solutions that power our digital world.",
    "finance": "💰 Finance is a broad field encompassing investment, banking, and financial planning. It's crucial for business operations and personal wealth management in our global economy.",
    "medical": "🏥 Medical field is dedicated to healthcare, patient care, and medical research. It's essential for improving human health and saving lives through various medical practices and innovations."
}

FIELD_SKILLS = {
    "software engineering": ["Programming", "Data Structures", "Algorithms", "Version Control", "Databases", "System Design"],
    "finance": ["Financial Analysis", "Excel", "Accounting", "Investment", "Risk Management"],
    "medical": ["Anatomy & Physiology", "Medical Procedures", "Patient Care", "Medical Ethics", "Clinical Skills", "Medical Technology"]
}

FIELD_JOB_ROLES = {
    "software engineering": ["Backend Developer", "Frontend Developer", "DevOps Engineer", "Mobile App Developer"],
    "finance": ["Financial Analyst", "Investment Banker", "Accountant", "Auditor"],
    "medical": ["Doctor", "Nurse", "Medical Researcher", "Healthcare Administrator"]
}

# Tools for dynamic data fetching
class CareerTools:
    @staticmethod
    def get_field_info(field_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a career field"""
        field_name = field_name.lower()
        if field_name in FIELD_DESCRIPTIONS:
            return {
                "field": field_name,
                "description": FIELD_DESCRIPTIONS[field_name],
                "skills": FIELD_SKILLS.get(field_name, []),
                "job_roles": FIELD_JOB_ROLES.get(field_name, []),
                "growth_potential": "High",
                "salary_range": "$60,000 - $150,000+",
                "education_required": "Bachelor's degree or equivalent"
            }
        return {"error": "Field not found"}

    @staticmethod
    def get_skill_details(skill_name: str, field: str) -> Dict[str, Any]:
        """Get detailed information about a specific skill"""
        skill_details = {
            "programming": {
                "description": "Ability to write code in various programming languages",
                "learning_path": ["Start with Python/JavaScript", "Learn data structures", "Practice algorithms", "Build projects"],
                "resources": ["Codecademy", "freeCodeCamp", "LeetCode", "GitHub"],
                "time_to_learn": "6-12 months"
            },
            "financial analysis": {
                "description": "Analyzing financial data to make business decisions",
                "learning_path": ["Learn Excel", "Study accounting principles", "Understand financial statements", "Practice with real data"],
                "resources": ["Coursera", "edX", "CFA Institute", "Bloomberg Terminal"],
                "time_to_learn": "3-6 months"
            },
            "anatomy": {
                "description": "Understanding human body structure and function",
                "learning_path": ["Study basic biology", "Learn human anatomy", "Practice with models", "Clinical experience"],
                "resources": ["Khan Academy", "Gray's Anatomy", "Medical school courses", "Clinical rotations"],
                "time_to_learn": "2-4 years"
            }
        }
        return skill_details.get(skill_name.lower(), {"error": "Skill not found"})

    @staticmethod
    def get_job_market_data(field: str) -> Dict[str, Any]:
        """Get current job market data for a field"""
        # Simulated job market data
        market_data = {
            "software engineering": {
                "demand": "Very High",
                "growth_rate": "22%",
                "average_salary": "$110,000",
                "remote_work": "Common",
                "top_companies": ["Google", "Microsoft", "Amazon", "Apple", "Meta"]
            },
            "finance": {
                "demand": "High",
                "growth_rate": "8%",
                "average_salary": "$85,000",
                "remote_work": "Limited",
                "top_companies": ["Goldman Sachs", "JPMorgan", "Morgan Stanley", "BlackRock", "Vanguard"]
            },
            "medical": {
                "demand": "Very High",
                "growth_rate": "16%",
                "average_salary": "$120,000",
                "remote_work": "Limited",
                "top_companies": ["Mayo Clinic", "Cleveland Clinic", "Johns Hopkins", "Mass General", "Stanford Health"]
            }
        }
        return market_data.get(field.lower(), {"error": "Field not found"})

    @staticmethod
    def get_learning_path(field: str, experience_level: str = "beginner") -> Dict[str, Any]:
        """Get a personalized learning path for a field"""
        paths = {
            "software engineering": {
                "beginner": [
                    "Learn Python basics (2-3 months)",
                    "Study data structures and algorithms (3-4 months)",
                    "Build small projects (2-3 months)",
                    "Learn version control with Git (1 month)",
                    "Apply for internships or entry-level positions"
                ],
                "intermediate": [
                    "Learn a framework (React, Django, etc.) (2-3 months)",
                    "Study system design (3-4 months)",
                    "Contribute to open source (ongoing)",
                    "Build a portfolio (2-3 months)",
                    "Network and attend meetups"
                ]
            },
            "finance": {
                "beginner": [
                    "Learn Excel and financial modeling (2-3 months)",
                    "Study accounting principles (3-4 months)",
                    "Learn about financial markets (2-3 months)",
                    "Get certifications (CFA, CPA) (6-12 months)",
                    "Apply for internships"
                ],
                "intermediate": [
                    "Specialize in a finance area (2-3 months)",
                    "Build financial models (ongoing)",
                    "Network with professionals (ongoing)",
                    "Get advanced certifications (ongoing)",
                    "Apply for analyst positions"
                ]
            },
            "medical": {
                "beginner": [
                    "Complete pre-med requirements (2-4 years)",
                    "Take MCAT exam (3-6 months preparation)",
                    "Apply to medical schools (1 year)",
                    "Complete medical school (4 years)",
                    "Complete residency (3-7 years)"
                ],
                "intermediate": [
                    "Choose a medical specialty (ongoing)",
                    "Complete specialty training (2-5 years)",
                    "Get board certifications (ongoing)",
                    "Build clinical experience (ongoing)",
                    "Consider fellowship programs"
                ]
            }
        }
        return paths.get(field.lower(), {}).get(experience_level, {"error": "Path not found"})

# Specialized Career Advisors (for handoffs)
class SoftwareEngineeringAdvisor(Agent):
    def __init__(self, name: str, instructions: str, model):
        super().__init__(name=name, instructions=instructions, model=model)
        self.field = "software engineering"
        self.tools = CareerTools()

    def respond(self, history, session):
        last_message = history[-1]["content"].lower().strip()
        
        # Use tools to get dynamic data
        field_info = self.tools.get_field_info(self.field)
        market_data = self.tools.get_job_market_data(self.field)
        
        if "skill" in last_message or "learn" in last_message:
            skill_details = self.tools.get_skill_details("programming", self.field)
            return (f"💻 **Software Engineering Skills Guide**\n\n{skill_details['description']}\n\n**Learning Path:**\n" + 
                   "\n".join([f"• {step}" for step in skill_details['learning_path']]) + 
                   f"\n\n**Resources:** {', '.join(skill_details['resources'])}\n\n**Time to Learn:** {skill_details['time_to_learn']}", None)
        
        elif "job" in last_message or "career" in last_message:
            return (f"💼 **Software Engineering Career Opportunities**\n\n**Job Roles:**\n" + 
                   "\n".join([f"• {role}" for role in field_info['job_roles']]) + 
                   f"\n\n**Market Data:**\n• Demand: {market_data['demand']}\n• Growth Rate: {market_data['growth_rate']}\n• Average Salary: {market_data['average_salary']}\n• Top Companies: {', '.join(market_data['top_companies'])}", None)
        
        else:
            return (f"💻 **Software Engineering Expert Here!**\n\nI can help you with:\n• Skills and learning paths\n• Job opportunities and market data\n• Career guidance and advice\n\nWhat would you like to know about software engineering?", None)

class FinanceAdvisor(Agent):
    def __init__(self, name: str, instructions: str, model):
        super().__init__(name=name, instructions=instructions, model=model)
        self.field = "finance"
        self.tools = CareerTools()

    def respond(self, history, session):
        last_message = history[-1]["content"].lower().strip()
        
        field_info = self.tools.get_field_info(self.field)
        market_data = self.tools.get_job_market_data(self.field)
        
        if "skill" in last_message or "learn" in last_message:
            skill_details = self.tools.get_skill_details("financial analysis", self.field)
            return (f"💰 **Finance Skills Guide**\n\n{skill_details['description']}\n\n**Learning Path:**\n" + 
                   "\n".join([f"• {step}" for step in skill_details['learning_path']]) + 
                   f"\n\n**Resources:** {', '.join(skill_details['resources'])}\n\n**Time to Learn:** {skill_details['time_to_learn']}", None)
        
        elif "job" in last_message or "career" in last_message:
            return (f"💼 **Finance Career Opportunities**\n\n**Job Roles:**\n" + 
                   "\n".join([f"• {role}" for role in field_info['job_roles']]) + 
                   f"\n\n**Market Data:**\n• Demand: {market_data['demand']}\n• Growth Rate: {market_data['growth_rate']}\n• Average Salary: {market_data['average_salary']}\n• Top Companies: {', '.join(market_data['top_companies'])}", None)
        
        else:
            return (f"💰 **Finance Expert Here!**\n\nI can help you with:\n• Financial analysis skills\n• Investment and banking careers\n• Market trends and opportunities\n\nWhat would you like to know about finance?", None)

class MedicalAdvisor(Agent):
    def __init__(self, name: str, instructions: str, model):
        super().__init__(name=name, instructions=instructions, model=model)
        self.field = "medical"
        self.tools = CareerTools()

    def respond(self, history, session):
        last_message = history[-1]["content"].lower().strip()
        
        field_info = self.tools.get_field_info(self.field)
        market_data = self.tools.get_job_market_data(self.field)
        
        if "skill" in last_message or "learn" in last_message:
            skill_details = self.tools.get_skill_details("anatomy", self.field)
            return (f"🏥 **Medical Skills Guide**\n\n{skill_details['description']}\n\n**Learning Path:**\n" + 
                   "\n".join([f"• {step}" for step in skill_details['learning_path']]) + 
                   f"\n\n**Resources:** {', '.join(skill_details['resources'])}\n\n**Time to Learn:** {skill_details['time_to_learn']}", None)
        
        elif "job" in last_message or "career" in last_message:
            return (f"💼 **Medical Career Opportunities**\n\n**Job Roles:**\n" + 
                   "\n".join([f"• {role}" for role in field_info['job_roles']]) + 
                   f"\n\n**Market Data:**\n• Demand: {market_data['demand']}\n• Growth Rate: {market_data['growth_rate']}\n• Average Salary: {market_data['average_salary']}\n• Top Companies: {', '.join(market_data['top_companies'])}", None)
        
        else:
            return (f"🏥 **Medical Expert Here!**\n\nI can help you with:\n• Medical education and training\n• Healthcare career paths\n• Clinical skills and procedures\n\nWhat would you like to know about the medical field?", None)

# Main Career Mentor Agent with Tools and Handoffs
class CareerMentorAgent(Agent):
    def __init__(self, name: str, instructions: str, model):
        super().__init__(name=name, instructions=instructions, model=model)
        self.fields = FIELDS
        self.field_descriptions = FIELD_DESCRIPTIONS
        self.field_skills = FIELD_SKILLS
        self.field_job_roles = FIELD_JOB_ROLES
        self.tools = CareerTools()
        
        # Initialize specialized advisors
        self.software_advisor = SoftwareEngineeringAdvisor("Software Engineering Advisor", "Expert in software engineering careers", model)
        self.finance_advisor = FinanceAdvisor("Finance Advisor", "Expert in finance careers", model)
        self.medical_advisor = MedicalAdvisor("Medical Advisor", "Expert in medical careers", model)

    def respond(self, history, session):
        """
        Professional AI-based response system with tools and handoffs
        """
        last_message = history[-1]["content"].lower().strip()
        
        # Greetings
        if any(greeting in last_message for greeting in ["hi", "hello", "hey"]):
            return ("👋 Hello! I'm your Career Mentor Agent. 🎯 I can help you explore various career fields. Here are some popular areas:\n- " + "\n- ".join(self.fields) + "\n\n🤔 Which field interests you most?", None)
        
        # End conversation
        if any(end_word in last_message for end_word in ["thanks", "thank you", "ok", "okay", "bye", "goodbye", "end", "finish", "done"]):
            return ("😊 Thank you for using the Career Mentor Agent! Feel free to return anytime for more career guidance. 🚀 Good luck with your career journey!", None)
        
        # Field selection with handoff to specialized advisor
        for field in self.fields:
            if field in last_message:
                session.set("current_field", field)
                
                # Handoff to specialized advisor
                if field == "software engineering":
                    return (self.software_advisor.respond(history, session)[0], "software_advisor")
                elif field == "finance":
                    return (self.finance_advisor.respond(history, session)[0], "finance_advisor")
                elif field == "medical":
                    return (self.medical_advisor.respond(history, session)[0], "medical_advisor")
        
        # Tool-based responses for general queries
        if "market" in last_message or "demand" in last_message:
            current_field = session.get("current_field")
            if current_field:
                market_data = self.tools.get_job_market_data(current_field)
                return (f"📊 **Job Market Data for {current_field.title()}**\n\n" + 
                       f"• Demand: {market_data['demand']}\n" +
                       f"• Growth Rate: {market_data['growth_rate']}\n" +
                       f"• Average Salary: {market_data['average_salary']}\n" +
                       f"• Remote Work: {market_data['remote_work']}\n" +
                       f"• Top Companies: {', '.join(market_data['top_companies'])}", None)
        
        if "path" in last_message or "learn" in last_message:
            current_field = session.get("current_field")
            if current_field:
                learning_path = self.tools.get_learning_path(current_field)
                return (f"🎓 **Learning Path for {current_field.title()}**\n\n" + 
                       "\n".join([f"• {step}" for step in learning_path]), None)
        
        # Default response
        return ("I'd be happy to help you explore career opportunities! 🎯 I can help you explore various career fields. Here are some popular areas:\n- " + "\n- ".join(self.fields) + "\n\n🤔 Which field interests you most?", None)

# Initialize the professional agent with tools and handoffs
career_agent = CareerMentorAgent(
    name="Career Mentor Agent",
    instructions="You are a professional career mentor with access to tools and specialized advisors for comprehensive career guidance.",
    model=None  # Will be set in main.py
)

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("current_field", None)
    cl.user_session.set("current_advisor", None)
    
    # Initialize the agent with the model
    career_agent.model = model
    career_agent.software_advisor.model = model
    career_agent.finance_advisor.model = model
    career_agent.medical_advisor.model = model
    
    cl.user_session.set("agent", career_agent)
    cl.user_session.set("software_advisor", career_agent.software_advisor)
    cl.user_session.set("finance_advisor", career_agent.finance_advisor)
    cl.user_session.set("medical_advisor", career_agent.medical_advisor)
    
    print(f"Professional Career Mentor Agent with Tools and Handoffs loaded: {career_agent}")
    await cl.Message(content="👋 Welcome to the Career Mentor Agent! I'm here to help you explore career opportunities and guide you through different professional fields.").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()
    
    agent: CareerMentorAgent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []
    session = cl.user_session
    history.append({"role": "user", "content": message.content})
    
    try:
        print("\n[PROFESSIONAL_AGENT_WITH_TOOLS_AND_HANDOFFS]\n", history, "\n")
        response_content, handoff = agent.respond(history, session)
        
        # Handle handoffs to specialized advisors
        if handoff:
            if handoff == "software_advisor":
                advisor = cl.user_session.get("software_advisor")
                response_content, _ = advisor.respond(history, session)
            elif handoff == "finance_advisor":
                advisor = cl.user_session.get("finance_advisor")
                response_content, _ = advisor.respond(history, session)
            elif handoff == "medical_advisor":
                advisor = cl.user_session.get("medical_advisor")
                response_content, _ = advisor.respond(history, session)
        
        msg.content = response_content
        await msg.update()
        cl.user_session.set("chat_history", history + [{"role": "assistant", "content": response_content}])
        print(f"User: {message.content}")
        print(f"Professional Agent with Tools: {response_content}")
        
    except Exception as e:
        msg.content = "I apologize, but I encountered an error. Please try again or rephrase your question."
        await msg.update() 