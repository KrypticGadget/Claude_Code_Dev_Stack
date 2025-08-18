#!/bin/bash
# Project setup helper for Claude Code Agent System

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_prompt() {
    echo -e "${YELLOW}[?]${NC} $1"
}

echo "Claude Code Agent System - Project Setup Helper"
echo "=============================================="
echo

# Get project details
print_prompt "Enter project name:"
read -r PROJECT_NAME

print_prompt "Enter project description:"
read -r PROJECT_DESC

print_prompt "Project type (web/mobile/api/fullstack):"
read -r PROJECT_TYPE

# Create project structure suggestions
echo
print_status "Suggested project structure for $PROJECT_TYPE:"
echo

case "$PROJECT_TYPE" in
    "web")
        echo "📁 $PROJECT_NAME/"
        echo "├── 📁 frontend/"
        echo "│   ├── 📁 src/"
        echo "│   ├── 📁 public/"
        echo "│   └── 📄 package.json"
        echo "├── 📁 backend/"
        echo "│   ├── 📁 src/"
        echo "│   ├── 📁 tests/"
        echo "│   └── 📄 package.json"
        echo "├── 📁 database/"
        echo "├── 📁 docs/"
        echo "└── 📄 README.md"
        
        SUGGESTED_AGENTS="master-orchestrator frontend-architecture frontend-mockup production-frontend backend-services database-architecture"
        ;;
        
    "mobile")
        echo "📁 $PROJECT_NAME/"
        echo "├── 📁 mobile/"
        echo "│   ├── 📁 src/"
        echo "│   ├── 📁 ios/"
        echo "│   ├── 📁 android/"
        echo "│   └── 📄 package.json"
        echo "├── 📁 backend/"
        echo "│   ├── 📁 api/"
        echo "│   └── 📁 services/"
        echo "├── 📁 shared/"
        echo "└── 📄 README.md"
        
        SUGGESTED_AGENTS="master-orchestrator mobile-development backend-services api-integration-specialist database-architecture"
        ;;
        
    "api")
        echo "📁 $PROJECT_NAME/"
        echo "├── 📁 src/"
        echo "│   ├── 📁 routes/"
        echo "│   ├── 📁 controllers/"
        echo "│   ├── 📁 models/"
        echo "│   └── 📁 middleware/"
        echo "├── 📁 tests/"
        echo "├── 📁 docs/"
        echo "│   └── 📁 api/"
        echo "└── 📄 README.md"
        
        SUGGESTED_AGENTS="master-orchestrator backend-services database-architecture api-integration-specialist security-architecture"
        ;;
        
    "fullstack")
        echo "📁 $PROJECT_NAME/"
        echo "├── 📁 apps/"
        echo "│   ├── 📁 web/"
        echo "│   ├── 📁 mobile/"
        echo "│   └── 📁 api/"
        echo "├── 📁 packages/"
        echo "│   ├── 📁 shared/"
        echo "│   └── 📁 ui/"
        echo "├── 📁 infrastructure/"
        echo "└── 📄 README.md"
        
        SUGGESTED_AGENTS="master-orchestrator business-analyst technical-cto project-manager frontend-architecture backend-services database-architecture devops-engineering"
        ;;
        
    *)
        echo "Using generic structure..."
        echo "📁 $PROJECT_NAME/"
        echo "├── 📁 src/"
        echo "├── 📁 tests/"
        echo "├── 📁 docs/"
        echo "└── 📄 README.md"
        
        SUGGESTED_AGENTS="master-orchestrator business-analyst technical-specifications"
        ;;
esac

echo
print_status "Recommended agent workflow:"
echo

# Display recommended workflow
echo "1. Strategic Planning Phase:"
echo "   ${GREEN}> Use the master-orchestrator agent to begin new project: \"$PROJECT_DESC\"${NC}"
echo
echo "2. Architecture Phase:"
for agent in $SUGGESTED_AGENTS; do
    if [ "$agent" != "master-orchestrator" ]; then
        echo "   ${GREEN}> Use the $agent agent to [specific task]${NC}"
    fi
done
echo

# Create initialization command
INIT_COMMAND="Use the master-orchestrator agent to begin new project: \"$PROJECT_DESC\""

print_status "Project initialization command:"
echo
echo "   ${GREEN}$INIT_COMMAND${NC}"
echo

# Optional: Save project config
print_prompt "Save project configuration? (y/n)"
read -r SAVE_CONFIG

if [ "$SAVE_CONFIG" = "y" ] || [ "$SAVE_CONFIG" = "Y" ]; then
    PROJECT_CONFIG_DIR="$HOME/.claude/projects"
    mkdir -p "$PROJECT_CONFIG_DIR"
    
    CONFIG_FILE="$PROJECT_CONFIG_DIR/${PROJECT_NAME// /-}.json"
    
    cat > "$CONFIG_FILE" << EOF
{
  "name": "$PROJECT_NAME",
  "description": "$PROJECT_DESC",
  "type": "$PROJECT_TYPE",
  "suggested_agents": "$SUGGESTED_AGENTS",
  "init_command": "$INIT_COMMAND",
  "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    
    print_success "Project configuration saved to $CONFIG_FILE"
fi

echo
print_status "Next steps:"
echo "1. Open Claude Code"
echo "2. Copy and paste the initialization command above"
echo "3. Follow the orchestrator's guidance through each phase"
echo
print_success "Project setup complete!"