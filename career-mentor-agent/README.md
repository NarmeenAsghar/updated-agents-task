# 🚀 Career Mentor Agent

A professional career guidance system built with **OpenAI Agent SDK** that provides comprehensive career exploration, skill development, and job market insights using advanced AI agents, tools, and handoffs.

## ✨ Features

### 🤖 **Multi-Agent System**
- **CareerMentorAgent** - Main coordinator agent
- **SoftwareEngineeringAdvisor** - Specialized software engineering expert
- **FinanceAdvisor** - Specialized finance and investment expert  
- **MedicalAdvisor** - Specialized healthcare and medical expert

### 🛠️ **Dynamic Tools System**
- **Field Information Tool** - Comprehensive career field data
- **Skill Details Tool** - Detailed learning paths and resources
- **Job Market Data Tool** - Real-time market trends and salaries
- **Learning Path Tool** - Personalized education roadmaps

### 🔄 **Intelligent Handoffs**
- Automatic routing to specialized advisors
- Context-aware conversation flow
- Seamless agent transitions
- Professional career guidance

### 💼 **Career Fields Supported**
- 💻 **Software Engineering** - Programming, development, tech careers
- 💰 **Finance** - Investment, banking, financial analysis
- 🏥 **Medical** - Healthcare, clinical practice, medical research

## 🏗️ Architecture

### **OpenAI Agent SDK Implementation**
- ✅ **Agents** - Multiple specialized agents
- ✅ **Tools** - Dynamic data fetching
- ✅ **Handoffs** - Automatic advisor routing  
- ✅ **Runner** - Professional execution flow
- ✅ **AI-Based** - Tool-driven responses

### **Project Structure**
```
career-mentor-agent/
├── main.py                 # Chainlit entry point
├── career_agent.py         # Complete agent system
├── agents/                 # Core Agent SDK framework
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd career-mentor-agent
```

### 2. **Set Up Environment**
Create a `.env` file with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run the Application**
```bash
chainlit run main.py
```

### 5. **Access the Application**
Open your browser and go to: `http://localhost:8000`

## 🎯 How It Works

### **Career Exploration Flow**
1. **Welcome** - Agent greets and shows available career fields
2. **Field Selection** - User chooses a career field of interest
3. **Handoff** - Automatic routing to specialized advisor
4. **Expert Guidance** - Field-specific career advice and tools
5. **Dynamic Data** - Real-time market and skill information

### **Professional Features**
- **Intelligent Routing** - Automatic handoffs to field experts
- **Dynamic Tools** - Real-time data fetching for skills, market trends, and learning paths
- **Context Awareness** - Maintains conversation context across agents
- **Professional Responses** - Expert-level career guidance with emojis and formatting

## 📊 Features Breakdown

| Feature | Implementation | Status |
|---------|---------------|--------|
| **Agents** | Multiple specialized agents | ✅ Complete |
| **Tools** | Dynamic data fetching | ✅ Complete |
| **Handoffs** | Automatic advisor routing | ✅ Complete |
| **AI-Based** | Tool-driven responses | ✅ Complete |
| **Professional** | Career guidance system | ✅ Complete |

## 🔧 Dependencies

- **chainlit** - Web interface
- **python-dotenv** - Environment management
- **openai** - OpenAI API integration
- **openai-agent-sdk** - Agent SDK framework
- **requests** - HTTP requests for tools

## 🎉 Key Benefits

1. **Professional Guidance** - Expert-level career advice
2. **Dynamic Data** - Real-time market and skill information
3. **Specialized Expertise** - Field-specific advisors
4. **Intelligent Routing** - Automatic handoffs to experts
5. **Comprehensive Coverage** - Multiple career fields supported

## 🤝 Contributing

This project demonstrates a complete implementation of OpenAI Agent SDK with:
- Multi-agent architecture
- Tool-based data fetching
- Intelligent handoffs
- Professional career guidance

Feel free to extend the system with additional career fields, tools, or specialized advisors!

## 📝 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using OpenAI Agent SDK for professional career guidance** 