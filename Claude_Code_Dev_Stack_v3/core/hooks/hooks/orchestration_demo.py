#!/usr/bin/env python3
"""
Orchestration Demo Slash Command Handler
Demonstrates full agent hierarchy with audio feedback
"""

import json
import sys

def handle_orchestration_demo():
    """
    /orchestrate-demo command
    Triggers a cascading demonstration of the entire agent system
    """
    
    demo_sequence = {
        "command": "/orchestrate-demo",
        "description": "Full Agent Orchestration Demonstration",
        "sequence": [
            {
                "phase": "1. PROMPT ENHANCEMENT",
                "agent": "@prompt-engineer",
                "prompt": "Enhance this: Build a full-stack web application with user authentication, real-time features, and deployment pipeline",
                "audio": "prompt_engineering.wav"
            },
            {
                "phase": "2. MASTER ORCHESTRATION",
                "agent": "@master-orchestrator",
                "prompt": "Coordinate the full project lifecycle using all available agent types",
                "audio": "master_orchestrator.wav"
            },
            {
                "phase": "3. BUSINESS & STRATEGY GROUP",
                "agents": [
                    "@ceo-strategy - Define product vision and market positioning",
                    "@business-analyst - Analyze market opportunity and ROI",
                    "@financial-analyst - Create financial projections and unit economics",
                    "@business-tech-alignment - Align technology with business goals"
                ],
                "audio": "business_analysis.wav"
            },
            {
                "phase": "4. TECHNICAL LEADERSHIP GROUP",
                "agents": [
                    "@technical-cto - Evaluate technical feasibility and architecture",
                    "@project-manager - Create project timeline and milestones",
                    "@technical-specifications - Define detailed technical requirements",
                    "@security-architecture - Design security framework"
                ],
                "audio": "technical_planning.wav"
            },
            {
                "phase": "5. FRONTEND DEVELOPMENT GROUP",
                "agents": [
                    "@ui-ux-design - Create design system and wireframes",
                    "@frontend-architecture - Design component hierarchy and state management",
                    "@frontend-mockup - Build HTML/CSS prototypes",
                    "@production-frontend - Implement production React/Vue/Angular app"
                ],
                "audio": "frontend_development.wav"
            },
            {
                "phase": "6. BACKEND DEVELOPMENT GROUP",
                "agents": [
                    "@backend-services - Build API endpoints and business logic",
                    "@database-architecture - Design database schema and queries",
                    "@middleware-specialist - Implement message queues and caching",
                    "@api-integration-specialist - Connect third-party services"
                ],
                "audio": "backend_development.wav"
            },
            {
                "phase": "7. MOBILE & CROSS-PLATFORM GROUP",
                "agents": [
                    "@mobile-developer - Create React Native/Flutter apps",
                    "@integration-setup - Configure cross-platform dependencies"
                ],
                "audio": "mobile_development.wav"
            },
            {
                "phase": "8. QUALITY & OPTIMIZATION GROUP",
                "agents": [
                    "@testing-automation - Generate comprehensive test suites",
                    "@quality-assurance-lead - Define quality gates and metrics",
                    "@performance-optimization - Optimize application performance"
                ],
                "audio": "quality_assurance.wav"
            },
            {
                "phase": "9. DEPLOYMENT & OPERATIONS GROUP",
                "agents": [
                    "@devops-engineer - Setup CI/CD pipelines and infrastructure",
                    "@script-automation - Create deployment and maintenance scripts",
                    "@technical-documentation - Generate comprehensive documentation"
                ],
                "audio": "deployment_operations.wav"
            },
            {
                "phase": "10. INTELLIGENT AUTOMATION GROUP",
                "agents": [
                    "@development-prompt - Generate phased development prompts",
                    "@usage-guide-agent - Configure optimal workflow patterns"
                ],
                "audio": "automation_complete.wav"
            }
        ],
        "execution_pattern": {
            "type": "hierarchical_cascade",
            "flow": [
                "prompt-engineer -> master-orchestrator",
                "master-orchestrator -> business group (parallel)",
                "business group -> technical leadership (sequential)",
                "technical leadership -> development groups (parallel)",
                "development groups -> quality group (convergent)",
                "quality group -> deployment group (sequential)",
                "all groups -> documentation (final)"
            ]
        }
    }
    
    # Output the orchestration plan
    return {
        "type": "orchestration_demo",
        "trigger_sequence": demo_sequence,
        "prompt_enhancement": f"""
/orchestrate-demo

I want to see the full agent orchestration system in action. Please:

1. Start with @prompt-engineer to enhance this request
2. Pass to @master-orchestrator for coordination
3. Demonstrate each agent group in logical sequence:
   - Business & Strategy agents for requirements
   - Technical Leadership for architecture
   - Frontend Development for UI/UX
   - Backend Development for services
   - Mobile Development for apps
   - Quality & Optimization for testing
   - Deployment & Operations for infrastructure
   - Intelligent Automation for workflow

Show me how each agent type contributes to building a complete full-stack application with:
- User authentication system
- Real-time chat features
- Payment processing
- Admin dashboard
- Mobile apps
- Deployment pipeline
- Monitoring and analytics

Each agent should produce specific outputs demonstrating their expertise.
Make the audio hooks fire for each agent activation!
"""
    }

def main():
    """Main entry point for slash command"""
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    # Check if this is the orchestrate-demo command
    prompt = input_data.get("prompt", "").lower()
    
    if "/orchestrate-demo" in prompt:
        result = handle_orchestration_demo()
        # Output the enhanced prompt for Claude to execute
        print(result["prompt_enhancement"])
    else:
        # Not our command, pass through
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()