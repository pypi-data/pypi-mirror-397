#!/usr/bin/env python3
"""
RTLViz Setup - Auto-configure MCP servers for AI IDEs.

Usage:
    rtlviz-setup              # Auto-detect and configure
    rtlviz-setup --claude     # Configure Claude Desktop only
    rtlviz-setup --vscode     # Configure VS Code only
"""

import os
import sys
import json
import shutil
from pathlib import Path

# MCP server configuration
MCP_CONFIG = {
    "command": "rtlviz-server"
}


def get_claude_config_path() -> Path:
    """Get Claude Desktop config path based on OS."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def get_vscode_config_path() -> Path:
    """Get VS Code MCP config path (workspace-level)."""
    return Path.cwd() / ".vscode" / "mcp.json"


def configure_claude():
    """Add rtlviz to Claude Desktop configuration."""
    config_path = get_claude_config_path()
    
    print(f"📍 Claude config: {config_path}")
    
    # Load existing config or create new
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}
        config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if already configured
    if "rtlviz" in config["mcpServers"]:
        print("✅ RTLViz already configured for Claude Desktop")
        return True
    
    # Add rtlviz
    config["mcpServers"]["rtlviz"] = MCP_CONFIG
    
    # Backup existing file
    if config_path.exists():
        backup_path = config_path.with_suffix(".json.backup")
        shutil.copy(config_path, backup_path)
        print(f"📦 Backed up existing config to: {backup_path}")
    
    # Write new config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print("✅ RTLViz configured for Claude Desktop")
    print("   Restart Claude Desktop to activate")
    return True


def configure_vscode():
    """Add rtlviz to VS Code MCP configuration."""
    config_path = get_vscode_config_path()
    
    print(f"📍 VS Code config: {config_path}")
    
    # Load existing config or create new
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}
        config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure servers exists
    if "servers" not in config:
        config["servers"] = {}
    
    # Check if already configured
    if "rtlviz" in config["servers"]:
        print("✅ RTLViz already configured for VS Code")
        return True
    
    # Add rtlviz
    config["servers"]["rtlviz"] = MCP_CONFIG
    
    # Write new config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print("✅ RTLViz configured for VS Code (current workspace)")
    print("   Reload VS Code window to activate")
    return True


def main():
    """Main entry point."""
    print("🔧 RTLViz Setup")
    print("=" * 40)
    
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    
    success = True
    
    if "--claude" in args:
        success = configure_claude()
    elif "--vscode" in args:
        success = configure_vscode()
    else:
        # Auto-detect: try both
        print("Auto-detecting IDEs...\n")
        
        claude_path = get_claude_config_path()
        vscode_path = get_vscode_config_path()
        
        found_any = False
        
        # Check for Claude Desktop
        if claude_path.parent.exists() or sys.platform in ("win32", "darwin"):
            print("🔍 Found Claude Desktop")
            configure_claude()
            found_any = True
            print()
        
        # Check for VS Code workspace
        if (Path.cwd() / ".vscode").exists() or (Path.cwd() / ".git").exists():
            print("🔍 Found VS Code workspace")
            configure_vscode()
            found_any = True
            print()
        
        if not found_any:
            print("⚠️  No supported IDE detected.")
            print("   Run with --claude or --vscode to force configuration.")
            success = False
    
    print("=" * 40)
    if success:
        print("🚀 Setup complete! You can now use RTLViz.")
        print("   Just ask your AI: 'Generate an RTL diagram for CPU.v'")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
