#!/usr/bin/env python3
"""
Main CLI entry point for AI Sidekick for Splunk.
Provides a unified command interface with subcommands.
"""

import argparse
import sys


def main():
    """Main CLI function with subcommands."""
    parser = argparse.ArgumentParser(
        prog="ai-sidekick",
        description="AI Sidekick for Splunk - Multi-agent workflow orchestration system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-sidekick --start                    # Start the AI Sidekick system
  ai-sidekick --stop                     # Stop the AI Sidekick system
  ai-sidekick --create-flow-agent dev123 # Create a new FlowPilot workflow agent
  ai-sidekick --help                     # Show this help message

For more information, visit: https://github.com/deslicer/ai-sidekick-for-splunk
        """
    )
    
    # Create mutually exclusive group for main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    
    action_group.add_argument(
        "--start",
        action="store_true",
        help="Start the AI Sidekick system"
    )
    
    action_group.add_argument(
        "--stop", 
        action="store_true",
        help="Stop the AI Sidekick system"
    )
    
    action_group.add_argument(
        "--create-flow-agent",
        metavar="NAME",
        help="Create a new FlowPilot workflow agent with the specified name"
    )
    
    # Optional arguments for create-flow-agent
    parser.add_argument(
        "--output-dir",
        help="Output directory for created workflow (default: contrib/flows/NAME)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.start:
            from ai_sidekick_for_splunk.cli.start_lab import main as start_main
            start_main()
            
        elif args.stop:
            from ai_sidekick_for_splunk.cli.stop_lab import main as stop_main
            stop_main()
            
        elif args.create_flow_agent:
            # Import and call create_flow_agent with the name
            from ai_sidekick_for_splunk.cli.create_flow_agent import main as create_main
            
            # Modify sys.argv to pass the name to the create_flow_agent script
            original_argv = sys.argv.copy()
            sys.argv = ["create_flow_agent", args.create_flow_agent]
            
            # Add output-dir if specified
            if args.output_dir:
                sys.argv.extend(["--output-dir", args.output_dir])
            
            try:
                create_main()
            finally:
                # Restore original argv
                sys.argv = original_argv
                
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()