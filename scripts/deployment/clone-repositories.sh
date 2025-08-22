#!/bin/bash
# Claude Code Dev Stack v3.0 - Repository Cloning Script
# This script clones all third-party repositories with attribution

echo "🚀 Claude Code Dev Stack v3.0 - Repository Integration"
echo "======================================================"
echo ""
echo "Cloning 7 open-source projects with attribution..."
echo ""

cd ../integrations

# Clone repositories with shallow depth to save space
repos=(
    "zainhoda/claude-code-browser:browser/zainhoda-claude-code-browser"
    "9cat/claude-code-app:mobile/9cat-claude-code-app"
    "qdhenry/Claude-Code-MCP-Manager:mcp-manager/qdhenry-mcp-manager"
    "cnoe-io/openapi-mcp-codegen:generators/cnoe-openapi-mcp-codegen"
    "harsha-iiiv/openapi-mcp-generator:generators/harsha-openapi-mcp-generator"
    "Owloops/claude-powerline:statusline/owloops-claude-powerline"
    "chongdashu/cc-statusline:statusline/chongdashu-cc-statusline"
)

for repo_info in "${repos[@]}"; do
    IFS=':' read -r repo_path local_path <<< "$repo_info"
    
    echo "📦 Cloning $repo_path..."
    
    if [ -d "$local_path" ]; then
        echo "  ✓ Already exists, skipping..."
    else
        git clone --depth=1 "https://github.com/$repo_path.git" "$local_path"
        
        if [ $? -eq 0 ]; then
            echo "  ✓ Successfully cloned to $local_path"
            
            # Preserve license
            if [ -f "$local_path/LICENSE" ]; then
                license_name=$(echo "$local_path" | sed 's/.*\///')
                cp "$local_path/LICENSE" "../LICENSE-THIRD-PARTY/LICENSE-$license_name"
                echo "  ✓ License preserved"
            fi
        else
            echo "  ✗ Failed to clone $repo_path"
        fi
    fi
    echo ""
done

echo "✅ Repository integration complete!"
echo ""
echo "📜 All licenses preserved in LICENSE-THIRD-PARTY/"
echo "📖 See CREDITS.md for full attribution"