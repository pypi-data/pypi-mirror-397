"""
Instinct8 CLI - Drop-in replacement for Codex exec

This CLI mimics Codex's `codex exec` interface, allowing users to replace
Codex with Instinct8 Agent seamlessly.

Usage:
    instinct8 "create a FastAPI endpoint"
    instinct8 exec "create a FastAPI endpoint"
    instinct8 exec --json "create a FastAPI endpoint"
"""

import argparse
import json
import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from .codex_integration import Instinct8Agent, create_instinct8_agent


class Instinct8CLI:
    """
    CLI wrapper that mimics Codex's exec interface.
    
    This allows users to replace Codex with Instinct8 by aliasing:
    alias codex=instinct8
    """
    
    def __init__(
        self,
        goal: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: str = "gpt-4o",
        compaction_threshold: int = 80000,
    ):
        """
        Initialize Instinct8 CLI.
        
        Args:
            goal: Optional default goal (can be set via config)
            constraints: Optional default constraints
            model: Model to use
            compaction_threshold: Compression threshold
        """
        self.model = model
        self.compaction_threshold = compaction_threshold
        
        # Try to load config from ~/.instinct8/config.json or .instinct8/config.json
        config = self._load_config()
        if config:
            goal = goal or config.get('goal')
            constraints = constraints or config.get('constraints', [])
            self.model = config.get('model', model)
        
        # Initialize agent if goal provided
        self.agent: Optional[Instinct8Agent] = None
        if goal:
            self.agent = create_instinct8_agent(
                goal=goal,
                constraints=constraints or [],
                model=self.model,
                compaction_threshold=self.compaction_threshold,
            )
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load config from ~/.instinct8/config.json or .instinct8/config.json"""
        config_paths = [
            Path.home() / ".instinct8" / "config.json",
            Path(".instinct8") / "config.json",
            Path("instinct8.config.json"),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        return json.load(f)
                except Exception:
                    pass
        
        return None
    
    def exec(
        self,
        prompt: str,
        json_output: bool = False,
        skip_git_check: bool = True,
        timeout: Optional[int] = None,
        allow_execution: bool = False,
    ) -> str:
        """
        Execute a prompt (mimics Codex's exec command).
        
        This now actually generates code and can execute commands!
        
        Args:
            prompt: The prompt/task to execute
            json_output: If True, return JSON output
            skip_git_check: Ignored (for compatibility)
            timeout: Optional timeout (ignored for now)
            allow_execution: If True, allows executing commands (use with caution)
        
        Returns:
            Agent's response with generated code
        """
        # Initialize agent if not already initialized
        if not self.agent:
            # Try to infer goal from prompt or use default
            goal = prompt[:100] + "..." if len(prompt) > 100 else prompt
            self.agent = create_instinct8_agent(
                goal=goal,
                constraints=[],
                model=self.model,
                compaction_threshold=self.compaction_threshold,
                allow_execution=allow_execution,
            )
        
        # Execute the task (this generates code!)
        response = self.agent.execute(prompt)
        
        if json_output:
            return json.dumps({
                "output": response,
                "context_length": self.agent.context_length,
                "salience_items": len(self.agent.salience_set),
            }, indent=2)
        
        return response


def main():
    """Main CLI entry point - mimics Codex's interface."""
    parser = argparse.ArgumentParser(
        description="Instinct8 - Coding agent with Selective Salience Compression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Persistent interactive mode (like Claude Code)
  instinct8                    # Starts persistent session
  instinct8 --goal "Build app"  # Start with goal
  
  # One-shot execution (like Codex exec)
  instinct8 "create a FastAPI endpoint"
  instinct8 exec "create a FastAPI endpoint"
  
  # With JSON output
  instinct8 exec --json "explain this code"
  
  # With goal and constraints
  instinct8 exec --goal "Build auth system" --constraints "Use JWT" "Hash passwords" "create login endpoint"
  
  # Alias to replace Codex
  alias codex=instinct8
  codex exec "fix lint errors"
        """
    )
    
    # Codex-compatible flags
    # Use nargs='*' to capture all remaining args as the prompt
    parser.add_argument(
        'prompt',
        nargs='*',
        help='Prompt/task to execute (can be multiple words). If omitted, starts persistent interactive session.'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON format'
    )
    parser.add_argument(
        '--skip-git-repo-check',
        action='store_true',
        help='Skip git repository check (for compatibility)'
    )
    
    # Instinct8-specific flags
    parser.add_argument(
        '--goal',
        type=str,
        help='Task goal (can also be set in ~/.instinct8/config.json)'
    )
    parser.add_argument(
        '--constraints',
        nargs='*',
        default=[],
        help='Task constraints'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o',
        help='Model to use (default: gpt-4o)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=80000,
        help='Compression threshold in tokens (default: 80000)'
    )
    parser.add_argument(
        '--allow-execution',
        action='store_true',
        help='Allow executing commands (use with caution!)'
    )
    
    # Handle 'exec' subcommand (for Codex compatibility)
    if len(sys.argv) > 1 and sys.argv[1] == 'exec':
        sys.argv.pop(1)  # Remove 'exec' from args
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)
    
    # Get prompt - join all words if it's a list
    prompt = ' '.join(args.prompt) if isinstance(args.prompt, list) else args.prompt
    
    # If no prompt provided, start persistent interactive session (like Claude Code)
    if not prompt:
        _start_persistent_session(
            goal=args.goal,
            constraints=args.constraints,
            model=args.model,
            compaction_threshold=args.threshold,
            allow_execution=getattr(args, 'allow_execution', False),
        )
        return
    
    # Create CLI instance for one-shot execution
    cli = Instinct8CLI(
        goal=args.goal,
        constraints=args.constraints,
        model=args.model,
        compaction_threshold=args.threshold,
    )
    
    # Execute
    try:
        output = cli.exec(
            prompt=prompt,
            json_output=args.json,
            skip_git_check=args.skip_git_repo_check,
            allow_execution=getattr(args, 'allow_execution', False),
        )
        print(output)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _start_persistent_session(
    goal: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    model: str = "gpt-4o",
    compaction_threshold: int = 80000,
    allow_execution: bool = False,
):
    """
    Start a persistent interactive session (like Claude Code).
    
    This keeps Instinct8 running and waiting for user input, maintaining
    context across multiple interactions.
    """
    import subprocess
    from pathlib import Path
    
    # Get project info
    cwd = Path.cwd()
    project_name = cwd.name
    
    # Try to get git branch
    git_branch = None
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            git_branch = result.stdout.strip()
    except Exception:
        pass
    
    # Welcome message (like Claude Code) - styled with colors
    from selective_salience import __version__
    from selective_salience.ui import print_welcome_box, print_tips_box, get_input_prompt
    
    # Suppress verbose logging during initialization
    import logging
    old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.WARNING)
    
    # Print styled welcome box
    print()
    print_welcome_box(
        version=__version__,
        project_name=project_name,
        git_branch=git_branch,
        working_dir=str(cwd),
    )
    print_tips_box()
    
    # Show file access status
    from selective_salience.ui import Colors
    print(f"{Colors.GREEN}✅{Colors.RESET} {Colors.DIM}File operations enabled (read/write){Colors.RESET}")
    if allow_execution:
        print(f"{Colors.YELLOW}⚠️{Colors.RESET} {Colors.DIM}Command execution enabled{Colors.RESET}")
    else:
        print(f"{Colors.DIM}💡 Tip: Use --allow-execution to enable command execution{Colors.RESET}")
    print()
    
    # Restore logging level after initialization
    logging.getLogger().setLevel(old_level)
    
    # Create agent
    from selective_salience.codex_integration import Instinct8Agent
    
    # Initialize with goal or default
    agent_goal = goal or f"Help with {project_name} project"
    agent_constraints = constraints or []
    
    # Suppress verbose output during agent initialization
    import sys
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    # Temporarily suppress stdout/stderr during initialization
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        agent = Instinct8Agent(
            model=model,
            compaction_threshold=compaction_threshold,
            allow_execution=allow_execution,
            working_directory=str(cwd),  # Pass working directory to agent
        )
        agent.initialize(agent_goal, agent_constraints)
    
    # Now agent is ready, show prompt
    
    # Persistent loop (like Claude Code)
    turn_count = 0
    while True:
        try:
            # Get user input with styled prompt
            prompt = input(get_input_prompt()).strip()
            
            if not prompt:
                continue
            
            # Handle slash commands (Codex-style)
            if prompt.startswith('/'):
                _handle_slash_command(prompt, agent, model, compaction_threshold, allow_execution, agent_goal, agent_constraints)
                continue
            
            # Handle special commands
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            elif prompt.lower() == 'help':
                _print_help()
                continue
            
            elif prompt.lower() == 'stats':
                print(f"\n📊 Statistics:")
                print(f"  Context length: {agent.context_length:,} tokens")
                print(f"  Salience items: {len(agent.salience_set)}")
                print(f"  Turns: {turn_count}")
                print()
                continue
            
            elif prompt.lower() == 'salience':
                salience = agent.salience_set
                if salience:
                    print("\n📌 Preserved Salience Set:")
                    for i, item in enumerate(salience, 1):
                        print(f"  {i}. {item[:100]}..." if len(item) > 100 else f"  {i}. {item}")
                else:
                    print("\n📌 No salience items yet (compression hasn't triggered)")
                print()
                continue
            
            elif prompt.lower() == 'compress':
                agent.compress()
                print("✅ Compression triggered\n")
                continue
            
            elif prompt.lower() == 'reset':
                agent.reset()
                agent.initialize(agent_goal, agent_constraints)
                turn_count = 0
                print("✅ Agent reset\n")
                continue
            
            # Execute the prompt
            turn_count += 1
            print()  # Blank line before response
            try:
                # Execute with thought process display
                response = agent.execute(prompt, show_reasoning=True)
                print(response)
                print()  # Blank line after response
            except Exception as e:
                print(f"❌ Error: {e}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def _print_help():
    """Print help message with all available commands."""
    from selective_salience.ui import Colors
    
    print(f"\n{Colors.BOLD}📖 Available Commands:{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Slash Commands (Codex-style):{Colors.RESET}")
    print(f"  {Colors.CYAN}/init{Colors.RESET}      - Create an AGENTS.md file with instructions for INSTINCT8")
    print(f"  {Colors.CYAN}/status{Colors.RESET}     - Show current session configuration")
    print(f"  {Colors.CYAN}/approvals{Colors.RESET}  - Choose what INSTINCT8 can do without approval")
    print(f"  {Colors.CYAN}/model{Colors.RESET}      - Choose what model and reasoning effort to use")
    print(f"  {Colors.CYAN}/review{Colors.RESET}     - Review any changes and find issues")
    
    print(f"\n{Colors.BOLD}Regular Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}<prompt>{Colors.RESET}        - Execute a coding task")
    print(f"  {Colors.GREEN}stats{Colors.RESET}          - Show agent statistics")
    print(f"  {Colors.GREEN}salience{Colors.RESET}       - Show preserved salience set")
    print(f"  {Colors.GREEN}compress{Colors.RESET}        - Manually trigger compression")
    print(f"  {Colors.GREEN}reset{Colors.RESET}          - Reset agent state")
    print(f"  {Colors.GREEN}help{Colors.RESET}           - Show this help message")
    print(f"  {Colors.GREEN}quit/exit/q{Colors.RESET}     - Exit Instinct8")
    print()


def _handle_slash_command(
    command: str,
    agent: Instinct8Agent,
    model: str,
    compaction_threshold: int,
    allow_execution: bool,
    agent_goal: str,
    agent_constraints: List[str],
):
    """Handle slash commands (Codex-style)."""
    from selective_salience.ui import Colors
    
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    if cmd == '/init':
        _handle_init_command(agent)
    
    elif cmd == '/status':
        _handle_status_command(agent, model, compaction_threshold, allow_execution, agent_goal, agent_constraints)
    
    elif cmd == '/approvals':
        _handle_approvals_command(agent, allow_execution)
    
    elif cmd == '/model':
        _handle_model_command(agent, model, args)
    
    elif cmd == '/review':
        _handle_review_command(agent)
    
    else:
        print(f"{Colors.YELLOW}⚠️  Unknown command: {cmd}{Colors.RESET}")
        print(f"Type {Colors.CYAN}help{Colors.RESET} or {Colors.CYAN}/help{Colors.RESET} to see available commands\n")


def _handle_init_command(agent: Instinct8Agent):
    """Handle /init command - create AGENTS.md file."""
    from selective_salience.ui import Colors
    from pathlib import Path
    
    agents_file = Path("AGENTS.md")
    
    if agents_file.exists():
        print(f"{Colors.YELLOW}⚠️  AGENTS.md already exists. Skipping /init to avoid overwriting.{Colors.RESET}\n")
        return
    
    # Create AGENTS.md with instructions
    agents_content = """# AGENTS.md - Instructions for INSTINCT8

This file contains instructions for INSTINCT8 agent working on this project.

## Project Goal
[Describe the main goal of this project]

## Constraints
- [Add any constraints or requirements]

## Guidelines
- [Add coding guidelines, style preferences, etc.]

## Notes
- [Any additional notes for the agent]

---
*This file was created by INSTINCT8's /init command.*
"""
    
    try:
        agents_file.write_text(agents_content)
        print(f"{Colors.GREEN}✅ Created AGENTS.md file{Colors.RESET}\n")
        print(f"{Colors.DIM}You can now edit AGENTS.md with instructions for INSTINCT8.{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.YELLOW}❌ Failed to create AGENTS.md: {e}{Colors.RESET}\n")


def _handle_status_command(
    agent: 'Instinct8Agent',
    model: str,
    compaction_threshold: int,
    allow_execution: bool,
    agent_goal: str,
    agent_constraints: List[str],
):
    """Handle /status command - show current session configuration."""
    from selective_salience.ui import Colors
    
    print(f"\n{Colors.BOLD}📊 Current Session Configuration:{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}Model:{Colors.RESET} {model}")
    print(f"{Colors.CYAN}Compression Threshold:{Colors.RESET} {compaction_threshold:,} tokens")
    print(f"{Colors.CYAN}Command Execution:{Colors.RESET} {'✅ Enabled' if allow_execution else '❌ Disabled'}")
    print(f"{Colors.CYAN}Current Context Length:{Colors.RESET} {agent.context_length:,} tokens")
    print(f"{Colors.CYAN}Salience Items:{Colors.RESET} {len(agent.salience_set)}")
    
    print(f"\n{Colors.BOLD}Goal:{Colors.RESET}")
    print(f"  {agent_goal}")
    
    if agent_constraints:
        print(f"\n{Colors.BOLD}Constraints:{Colors.RESET}")
        for constraint in agent_constraints:
            print(f"  • {constraint}")
    else:
        print(f"\n{Colors.DIM}No constraints set{Colors.RESET}")
    
    print()


def _handle_approvals_command(agent: Instinct8Agent, allow_execution: bool):
    """Handle /approvals command - configure what agent can do without approval."""
    from selective_salience.ui import Colors
    
    print(f"\n{Colors.BOLD}⚙️  Approval Settings:{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}Command Execution:{Colors.RESET} {'✅ Enabled' if allow_execution else '❌ Disabled'}")
    print(f"{Colors.CYAN}File Operations:{Colors.RESET} ✅ Enabled (read/write)")
    
    print(f"\n{Colors.DIM}Note: To enable command execution, restart INSTINCT8 with --allow-execution flag{Colors.RESET}\n")


def _handle_model_command(agent: Instinct8Agent, current_model: str, args: str):
    """Handle /model command - choose model and reasoning effort."""
    from selective_salience.ui import Colors
    
    if not args:
        print(f"\n{Colors.BOLD}🤖 Current Model:{Colors.RESET} {current_model}\n")
        print(f"{Colors.DIM}Usage: /model <model-name>{Colors.RESET}")
        print(f"{Colors.DIM}Example: /model gpt-4o{Colors.RESET}\n")
        return
    
    new_model = args.strip()
    # Update agent model (if agent supports it)
    if hasattr(agent, '_model'):
        agent._model = new_model
        print(f"{Colors.GREEN}✅ Model changed to: {new_model}{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Model change requires restart. New model: {new_model}{Colors.RESET}\n")


def _handle_review_command(agent: Instinct8Agent):
    """Handle /review command - review changes and find issues."""
    from selective_salience.ui import Colors
    import subprocess
    from pathlib import Path
    
    print(f"\n{Colors.BOLD}🔍 Reviewing Changes:{Colors.RESET}\n")
    
    # Check for git diff
    try:
        result = subprocess.run(
            ['git', 'diff', '--stat'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"{Colors.CYAN}Git Changes:{Colors.RESET}")
            print(result.stdout)
            print()
        else:
            print(f"{Colors.DIM}No git changes detected{Colors.RESET}\n")
    except Exception:
        print(f"{Colors.DIM}Git not available or not a git repository{Colors.RESET}\n")
    
    # Show file operations
    if hasattr(agent, '_file_operations') and agent._file_operations:
        print(f"{Colors.CYAN}File Operations:{Colors.RESET}")
        for op in agent._file_operations[-10:]:  # Show last 10
            op_type = op.get('operation', 'unknown')
            path = op.get('path', 'unknown')
            if op_type == 'write':
                print(f"  ✅ Created/Modified: {Path(path).name}")
            elif op_type == 'read':
                print(f"  📖 Read: {Path(path).name}")
        print()
    else:
        print(f"{Colors.DIM}No file operations recorded{Colors.RESET}\n")
    
    # Ask agent to review
    print(f"{Colors.DIM}Asking agent to review changes...{Colors.RESET}\n")
    try:
        review_prompt = "Review the recent changes and identify any potential issues, bugs, or improvements needed."
        response = agent.execute(review_prompt, show_reasoning=True)
        print(response)
        print()
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Review failed: {e}{Colors.RESET}\n")


if __name__ == '__main__':
    main()

