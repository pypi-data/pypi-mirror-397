"""
Main CLI Interface
"""

import sys
import os
from typing import Optional
from .config import ConfigManager
from .terminal_ui import TerminalUI
from .agent import BugPilotAgent
from .prompts import get_welcome_message


class BugPilotCLI:
    """Main CLI application"""
    
    def __init__(self):
        # Capture current working directory
        self.working_dir = os.getcwd()
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Set working directory in config
        self.config.working_directory = self.working_dir
        
        self.ui = TerminalUI(theme=self.config.terminal_theme)
        self.agent = BugPilotAgent(self.config, self.ui)
        self.running = False
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands, return True if it was a command"""
        
        if not user_input.startswith('/'):
            return False
        
        parts = user_input[1:].split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in ['exit', 'quit', 'q']:
            self.ui.print_info("Exiting BugPilot CLI...")
            self.running = False
            return True
        
        elif command == 'help':
            self.ui.show_help(self.config.mode)
            return True
        
        elif command == 'settings':
            self.ui.show_settings_menu(self.config)
            return True
        
        elif command == 'configure':
            self.configure_settings()
            return True
        
        elif command == 'mode':
            if args:
                mode = args[0].lower()
                if mode in ['normal', 'hacker']:
                    self.config.mode = mode
                    self.config_manager.save_config()
                    self.agent.update_mode(mode)
                    self.ui.show_banner(mode)
                else:
                    self.ui.print_error("Invalid mode. Use 'normal' or 'hacker'")
            else:
                self.ui.print_info(f"Current mode: {self.config.mode}")
            return True
        
        elif command == 'clear':
            self.agent.clear_context()
            return True
        
        elif command == 'models':
            self.ui.show_model_options()
            return True
        
        elif command == 'tools':
            self.show_tools_menu(args)
            return True
        
        elif command == 'portfolio':
            import webbrowser
            portfolio_url = "https://letchupkt.vgrow.tech"
            self.ui.print_panel(
                f"Developer: LAKSHMIKANTHAN K (letchupkt)\nPortfolio: {portfolio_url}",
                title="[*] Developer Portfolio",
                style="primary"
            )
            try:
                webbrowser.open(portfolio_url)
                self.ui.print_success(f"Opening {portfolio_url} in your browser...")
            except Exception as e:
                self.ui.print_warning(f"Could not open browser automatically. Please visit: {portfolio_url}")
            return True
        
        elif command == 'update':
            self.check_and_update()
            return True
        
        else:
            self.ui.print_error(f"Unknown command: /{command}")
            self.ui.print_info("Type /help for available commands")
            return True
    
    def configure_settings(self):
        """Interactive settings configuration"""
        self.ui.print_panel("[*] Configuration Menu", style="primary")
        self.ui.print_info(f"Current Working Directory: {self.working_dir}")
        self.ui.print_info("")
        
        # Configure AI Provider
        self.ui.show_model_options()
        provider = self.ui.prompt(
            "Select AI provider (gemini/openai/groq/ollama/anthropic)",
            default=self.config.model.provider
        )
        
        # Model-specific configuration
        if provider == "gemini":
            model_name = self.ui.prompt("Model name", default="gemini-2.0-flash-exp")
            api_key = self.ui.prompt("Gemini API Key (press Enter to use environment variable)", default="")
        elif provider == "openai":
            model_name = self.ui.prompt("Model name", default="gpt-4o")
            api_key = self.ui.prompt("OpenAI API Key (press Enter to use environment variable)", default="")
        elif provider == "groq":
            model_name = self.ui.prompt("Model name", default="llama-3.3-70b-versatile")
            api_key = self.ui.prompt("Groq API Key (press Enter to use environment variable)", default="")
        elif provider == "ollama":
            model_name = self.ui.prompt("Model name", default="llama3.2")
            base_url = self.ui.prompt("Ollama base URL", default="http://localhost:11434")
            api_key = None
            self.config.model.base_url = base_url
        elif provider == "anthropic":
            model_name = self.ui.prompt("Model name", default="claude-3-5-sonnet-20241022")
            api_key = self.ui.prompt("Anthropic API Key (press Enter to use environment variable)", default="")
        else:
            self.ui.print_error("Invalid provider selected")
            return
        
        # Update configuration
        if api_key:
            self.config_manager.update_model(provider, model_name, api_key)
        else:
            self.config_manager.update_model(provider, model_name)
        
        # Other settings
        mode = self.ui.prompt("Operating mode (normal/hacker)", default=self.config.mode)
        if mode in ["normal", "hacker"]:
            self.config.mode = mode
        
        theme = self.ui.prompt("Terminal theme (ocean/sunset/neon/forest/midnight)", default=self.config.terminal_theme)
        if theme in ["ocean", "sunset", "neon", "forest", "midnight"]:
            self.config.terminal_theme = theme
        
        # Auto-update setting
        self.ui.print_info("Check for updates on startup?")
        auto_update = self.ui.confirm("Enable auto-update check")
        self.config.auto_update_check = auto_update
        
        # Save configuration
        self.config_manager.save_config()
        
        self.ui.print_success("Configuration saved!")
        self.ui.print_info("Reinitializing agent...")
        
        # Reinitialize with new config
        self.config = self.config_manager.config
        self.config.working_directory = self.working_dir
        self.ui = TerminalUI(theme=self.config.terminal_theme)
        self.agent = BugPilotAgent(self.config, self.ui)
    
    def show_tools_menu(self, args):
        """Show tools menu with installation options"""
        tool_status = self.agent.tool_manager.get_tool_status()
        
        self.ui.print_panel("[*] Pentesting Tools Status", style="primary")
        
        for category, tools in tool_status.items():
            category_name = category.replace('_', ' ').title()
            self.ui.print_message(f"\n[+] {category_name}:", style="secondary")
            
            for tool in tools:
                status = "[OK]" if tool['installed'] else "[--]"
                status_style = "success" if tool['installed'] else "dim"
                
                tool_line = f"    {status} {tool['name']:<15} - {tool['description']}"
                self.ui.print_message(tool_line, style=status_style)
        
        # Show summary
        installed = self.agent.tool_manager.get_installed_tools()
        total = len(self.agent.tool_manager.TOOLS)
        
        self.ui.print_message(f"\n[*] Installed: {len(installed)}/{total} tools", style="info")
        
        # Offer installation for missing tools
        missing = self.agent.tool_manager.get_missing_tools()
        if missing and self.config.mode == "hacker":
            self.ui.print_warning(f"\n{len(missing)} tools not installed.")
            if self.ui.confirm("Install all missing tools?"):
                self.ui.print_info("Installing tools... This may take several minutes.")
                for tool in missing:
                    self.ui.print_info(f"Installing {tool}...")
                    success, message = self.agent.tool_manager.install_tool(tool)
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
    
    def check_and_update(self):
        """Check for updates and install if available"""
        from .updater import AutoUpdater
        from . import __version__
        
        updater = AutoUpdater()  # Gets version automatically
        
        self.ui.print_info("Checking for updates...")
        has_update, latest = updater.check_for_updates()
        
        if has_update:
            self.ui.print_panel(
                updater.get_update_info(),
                title="[!] Update Available",
                style="warning"
            )
            
            if self.ui.confirm("Install update now?"):
                self.ui.print_info("Updating BugPilot CLI... This may take a minute.")
                success, message = updater.perform_update()
                
                if success:
                    self.ui.print_success(message)
                    self.ui.print_warning("Please restart BugPilot CLI to use the new version.")
                    self.ui.print_info("Run: bugpilot")
                else:
                    self.ui.print_error(message)
        else:
            self.ui.print_panel(
                updater.get_update_info(),
                title="[+] Up to Date",
                style="success"
            )
    
    def _display_response_with_typing(self, response: str, chars_per_second: int = 150):
        """Display AI response with smooth typing effect"""
        import time
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text
        
        current_text = ""
        
        with Live(console=self.ui.console, refresh_per_second=30) as live:
            for char in response:
                current_text += char
                
                display_text = Text(current_text, style=self.ui.theme['text'])
                panel = Panel(
                    display_text,
                    title=f"[{self.ui.theme['success']}][AI] BugPilot[/{self.ui.theme['success']}]",
                    border_style=self.ui.theme['accent'],
                    padding=(1, 2)
                )
                
                live.update(panel)
                
                if char in '.!?\n':
                    time.sleep(0.015)
                else:
                    time.sleep(1.0 / chars_per_second)
    
    def run(self):
        """Main CLI loop"""
        # Clear terminal for clean start
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show banner
        self.ui.show_banner(self.config.mode)
        
        # Show welcome message
        self.ui.print_message(get_welcome_message(self.config.mode))
        
        # Check for updates if enabled
        if self.config.auto_update_check:
            try:
                from .updater import check_update_on_startup
                from . import __version__
                
                update_msg = check_update_on_startup(__version__, True)
                if update_msg:
                    self.ui.print_warning(update_msg)
            except:
                pass  # Silently fail if update check fails
        
        # Check if model is configured
        if not self.agent.model:
            self.ui.print_warning(" AI model not configured!")
            self.ui.print_info("Run /configure to set up your AI provider")
            
            if self.ui.confirm("Configure now?"):
                self.configure_settings()
        
        self.running = True
        
        # Main loop
        while self.running:
            try:
                # Get user input with autocomplete
                from .autocomplete import get_command_input
                
                # Use autocomplete for user input
                user_input = get_command_input(
                    "\n[!] You: " if self.config.mode == "hacker" else "\n[+] You: "
                ).strip()
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    continue
                
                # Show thinking indicator (will auto-clear)
                from rich.live import Live
                from rich.text import Text
                from rich.console import Console
                
                # Create a temporary console for the thinking message
                thinking_text = Text(" Thinking...", style="cyan")
                
                with Live(thinking_text, console=self.ui.console, refresh_per_second=4, transient=True) as live:
                    # Get AI response
                    response = self.agent.chat(user_input)
                    # Live context automatically clears on exit due to transient=True
                
                # In HACKER MODE, auto-execute commands and continue autonomously
                if self.config.mode == "hacker":
                    max_iterations = 10  # Allow more iterations for complex pentests
                    iteration = 0
                    last_output = ""
                    
                    while iteration < max_iterations:
                        # Extract and execute commands from AI response
                        commands = self.agent.extract_commands(response)
                        
                        if commands:
                            # Execute all commands from this response
                            for cmd in commands:
                                self.ui.print_panel(
                                    cmd,
                                    title="[>>] Executing Command",
                                    style="warning"
                                )
                                
                                output, returncode = self.agent.execute_command(cmd)
                                last_output = output
                                
                                # Show result
                                status = "[+] Success" if returncode == 0 else "[-] Failed"
                                self.ui.print_panel(
                                    f"Status: {status}\\nReturn Code: {returncode}\\n\\nOutput:\\n{output[:2000]}{'...' if len(output) > 2000 else ''}",
                                    title="[*] Command Result",
                                    style="success" if returncode == 0 else "error"
                                )
                            
                            # Ask AI to analyze results and suggest next step
                            analysis_prompt = f"""Previous command: {commands[-1]}
Output: {last_output[:1000]}

Based on this result, what should be the next step for pentesting {user_input}?
If the pentest is complete or you have enough information, provide a summary.
Otherwise, suggest the next command to run."""
                            
                            thinking_text = Text(" Analyzing results...", style="cyan")
                            with Live(thinking_text, console=self.ui.console, refresh_per_second=4, transient=True) as live:
                                response = self.agent.chat(analysis_prompt)
                            
                            # Check if AI wants to stop
                            response_lower = response.lower()
                            if any(phrase in response_lower for phrase in [
                                'pentest complete', 'testing complete', 'scan complete',
                                'assessment complete', 'analysis complete', 'finished',
                                'no further steps', 'that concludes', 'summary:'
                            ]):
                                # Show final summary
                                self._display_response_with_typing(response)
                                break
                        else:
                            # No commands in response - just show it and break
                            self._display_response_with_typing(response)
                            break
                        
                        iteration += 1
                    
                    # If max iterations reached
                    if iteration >= max_iterations:
                        self.ui.print_warning("\\nReached maximum iteration limit. Pentest session ended.")
                else:
                    # NORMAL MODE - just display response
                    self._display_response_with_typing(response)
                
            except KeyboardInterrupt:
                self.ui.print_warning("\nInterrupted by user")
                if self.ui.confirm("Exit BugPilot?"):
                    self.running = False
            except Exception as e:
                self.ui.print_error(f"Unexpected error: {str(e)}")


def main():
    """Entry point for CLI"""
    try:
        cli = BugPilotCLI()
        cli.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
