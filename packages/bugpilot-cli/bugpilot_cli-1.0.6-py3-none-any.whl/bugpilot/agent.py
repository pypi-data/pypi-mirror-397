"""
Core Agent Logic - Handles AI interactions and command execution
Enhanced with file system access, tool management, and advanced agentic capabilities
"""

import subprocess
import re
import os
from typing import List, Dict, Optional, Tuple
from .models import ModelFactory, BaseModel
from .prompts import get_system_prompt
from .terminal_ui import TerminalUI
from .filesystem import FileSystemAccess
from .toolmanager import ToolManager


class BugPilotAgent:
    """Main agent for BugPilot CLI"""
    
    def __init__(self, config, ui: TerminalUI):
        self.config = config
        self.ui = ui
        self.model: Optional[BaseModel] = None
        self.context: List[Dict[str, str]] = []
        self.system_prompt = get_system_prompt(config.mode)
        
        # Initialize file system access
        self.filesystem = FileSystemAccess(config.working_directory)
        
        # Initialize tool manager
        self.tool_manager = ToolManager()
        
        # Track current working directory
        self.current_dir = os.getcwd()
        
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize AI model bas on configuration"""
        try:
            from .config import ConfigManager
            
            # Get API key from config manager (checks api_keys dict, then env vars)
            config_manager = ConfigManager()
            api_key = config_manager.get_api_key(self.config.model.provider)
            
            self.model = ModelFactory.create_model(
                provider=self.config.model.provider,
                api_key=api_key,
                model_name=self.config.model.model_name,
                temperature=self.config.model.temperature,
                max_tokens=self.config.model.max_tokens,
                base_url=self.config.model.base_url
            )
            
            self.ui.print_success(
                f"Initialized {self.config.model.provider} ({self.config.model.model_name})"
            )
        except Exception as e:
            self.ui.print_error(f"Failed to initialize model: {str(e)}")
            self.model = None
    
    def add_to_context(self, role: str, content: str):
        """Add message to conversation context"""
        self.context.append({"role": role, "content": content})
        
        # Keep only recent context based on config
        if len(self.context) > self.config.context_history_size * 2:
            self.context = self.context[-self.config.context_history_size * 2:]
    
    def clear_context(self):
        """Clear conversation context"""
        self.context = []
        self.ui.print_success("Context cleared")
    
    def execute_command(self, command: str) -> Tuple[str, int]:
        """Execute shell command and return output with auto tool installation"""
        try:
            # Extract tool name from command
            tool_name = command.split()[0] if command.strip() else ""
            
            # Check if tool exists, if not try to install in hacker mode
            if tool_name in self.tool_manager.TOOLS:
                if not self.tool_manager.installed_tools.get(tool_name, False):
                    if self.config.mode == "hacker":
                        self.ui.print_warning(f"Tool '{tool_name}' not found. Auto-installing...")
                        success, message = self.tool_manager.install_tool(tool_name)
                        if success:
                            self.ui.print_success(message)
                        else:
                            self.ui.print_error(message)
                            return message, -1
            
            # Determine shell based on OS
            if os.name == 'nt':  # Windows
                shell_cmd = ['powershell', '-Command', command]
            else:  # Linux/Termux
                shell_cmd = ['bash', '-c', command]
            
            result = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for long scans
            )
            
            output = result.stdout if result.stdout else result.stderr
            return output, result.returncode
        except subprocess.TimeoutExpired:
            return "Command timed out after 5 minutes (increase timeout if needed)", -1
        except Exception as e:
            return f"Error executing command: {str(e)}", -1
    
    def extract_commands(self, text: str) -> List[str]:
        """Extract shell commands from AI response"""
        # Look for commands in code blocks
        code_block_pattern = r'```(?:bash|shell|sh)?\n(.*?)```'
        commands = re.findall(code_block_pattern, text, re.DOTALL)
        
        # Also look for inline commands starting with $
        inline_pattern = r'\$\s+(.+?)(?:\n|$)'
        inline_commands = re.findall(inline_pattern, text)
        
        all_commands = commands + [cmd.strip() for cmd in inline_commands]
        return [cmd.strip() for cmd in all_commands if cmd.strip()]
    
    def process_file_operations(self, user_input: str) -> Optional[str]:
        """Process file-related operations"""
        # Detect file read requests
        if any(keyword in user_input.lower() for keyword in ['read file', 'show file', 'open file', 'cat ', 'view file']):
            # Extract filename
            import re
            file_match = re.search(r'[\'"]([^\'"]+ [^\'"]+ \.|[\w/.-]+\.[\w]+)[\'"]', user_input)
            if file_match:
                filename = file_match.group(1)
                success, content = self.filesystem.read_file(filename)
                if success:
                    return f"File contents of '{filename}':\n\n```\n{content}\n```"
                else:
                    return f"Error: {content}"
        
        # Detect list files requests
        if any(keyword in user_input.lower() for keyword in ['list files', 'show files', 'ls', 'dir']):
            files = self.filesystem.list_files()
            if files:
                files_str = "\n".join([f"  • {f['name']} ({self.filesystem._human_readable_size(f['size'])})" for f in files[:20]])
                return f"Files in current directory:\n{files_str}"
            else:
                return "No files found in current directory."
        
        # Detect project analysis requests
        if any(keyword in user_input.lower() for keyword in ['analyze project', 'project structure', 'show structure']):
            analysis = self.filesystem.analyze_project()
            return f"""Project Analysis:
  • Total Files: {analysis['total_files']}
  • Total Size: {self.filesystem._human_readable_size(analysis['total_size'])}
  • Languages: {', '.join(analysis['languages'].keys())}
  • File Types: {len(analysis['file_types'])} different types
"""
        
        return None
    
    def process_hacker_mode_response(self, response: str, user_input: str = "") -> str:
        """Process response in hacker mode - auto-execute commands"""
        # Don't execute commands for casual conversation or questions
        user_lower = user_input.lower().strip()
        
        # List of casual/question inputs that should NOT trigger command execution
        casual_patterns = [
            'hey', 'heyy', 'hello', 'hi', 'sup', 'yo', 'thanks', 'thank you', 'ok', 'okay',
            'what can you do', 'what can u do', 'help', 'who are you', 'what are you',
            'how are you', 'how do you work', 'what is this', 'explain', 'tell me about'
        ]
        
        # Check if input matches casual patterns
        for pattern in casual_patterns:
            if pattern in user_lower:
                return response
        
        # Also check if it's a question (contains '?' but no target/IP)
        if '?' in user_input and not any(indicator in user_lower for indicator in ['scan', 'test', 'check', 'exploit', 'target', '192.', '10.', 'http://', 'https://']):
            return response
        
        commands = self.extract_commands(response)
        
        if not commands:
            return response
        
        executed_results = []
        
        for cmd in commands:
            # Show command being executed
            self.ui.print_panel(
                cmd,
                title="[>>] Executing Command",
                style="warning"
            )
            
            # Execute if auto-execute is enabled or in hacker mode
            if self.config.auto_execute_commands or self.config.mode == "hacker":
                output, return_code = self.execute_command(cmd)
                
                status = "[+] Success" if return_code == 0 else "[-] Failed"
                self.ui.print_panel(
                    f"Status: {status}\nReturn Code: {return_code}\n\nOutput:\n{output}",
                    title="[*] Command Result",
                    style="success" if return_code == 0 else "error"
                )
                
                executed_results.append({
                    "command": cmd,
                    "output": output,
                    "return_code": return_code
                })
            else:
                # Ask for confirmation
                if self.ui.confirm(f"Execute command: {cmd[:100]}...?"):
                    output, return_code = self.execute_command(cmd)
                    
                    status = "[+] Success" if return_code == 0 else "[-] Failed"
                    self.ui.print_panel(
                        f"Status: {status}\nReturn Code: {return_code}\n\nOutput:\n{output}",
                        title="[*] Command Result",
                        style="success" if return_code == 0 else "error"
                    )
                    
                    executed_results.append({
                        "command": cmd,
                        "output": output,
                        "return_code": return_code
                    })
        
        # If commands were executed, add results to context for next iteration
        if executed_results:
            results_summary = "\n\n".join([
                f"Command: {r['command']}\nReturn Code: {r['return_code']}\nOutput:\n{r['output']}"
                for r in executed_results
            ])
            
            self.add_to_context("assistant", response)
            self.add_to_context("user", f"Command execution results:\n{results_summary}")
        
        return response
    
    def chat(self, user_input: str) -> str:
        """Main chat function with file system awareness"""
        if not self.model:
            return "Error: Model not initialized. Please configure API keys."
        
        # Check for file operations first
        file_response = self.process_file_operations(user_input)
        if file_response:
            return file_response
        
        # Add file system context to prompt
        file_context = f"\nCurrent Directory: {self.filesystem.get_current_directory()}"
        
        # Prepare full prompt with system context
        full_prompt = f"{self.system_prompt}{file_context}\n\nUser: {user_input}"
        
        # Add to context
        self.add_to_context("user", user_input)
        
        try:
            # Generate response
            response = self.model.generate(full_prompt, self.context)
            
            # Add response to context
            self.add_to_context("assistant", response)
            
            # Process commands in hacker mode
            if self.config.mode == "hacker":
                self.process_hacker_mode_response(response, user_input)
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def update_mode(self, mode: str):
        """Update operating mode"""
        self.config.mode = mode
        self.system_prompt = get_system_prompt(mode)
        self.clear_context()
        self.ui.print_success(f"Switched to {mode.upper()} mode")
