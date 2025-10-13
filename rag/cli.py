#!/usr/bin/env python3
"""Simple CLI for querying Fallout 76 build data"""

import os
from pathlib import Path
from query_engine import FalloutRAG

def ensure_api_key():
    """Check for API key and prompt user if missing"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("No ANTHROPIC_API_KEY found in environment.")
        print("Get your API key from: https://console.anthropic.com/settings/keys\n")
        api_key = input("Enter your Anthropic API key: ").strip()

        if not api_key:
            print("API key is required to use this tool.")
            exit(1)

        # Find .env file (should be in project root, one level up from rag/)
        env_path = Path(__file__).parent.parent / '.env'

        # Check if .env exists and update it, or create new
        if env_path.exists():
            # Read existing content
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Check if ANTHROPIC_API_KEY already exists
            key_exists = False
            for i, line in enumerate(lines):
                if line.startswith('ANTHROPIC_API_KEY='):
                    lines[i] = f'ANTHROPIC_API_KEY={api_key}\n'
                    key_exists = True
                    break

            # Add if it doesn't exist
            if not key_exists:
                lines.append(f'\nANTHROPIC_API_KEY={api_key}\n')

            # Write back
            with open(env_path, 'w') as f:
                f.writelines(lines)
        else:
            # Create new .env file
            with open(env_path, 'w') as f:
                f.write(f'ANTHROPIC_API_KEY={api_key}\n')

        print(f"\nAPI key saved to {env_path}")
        print("Restart the CLI to use the saved key.\n")

        # Set for current session
        os.environ['ANTHROPIC_API_KEY'] = api_key

def main():
    print("=== Fallout 76 Build Assistant ===")
    print("Ask questions about weapons, perks, and armor!")
    print("Type 'exit' to quit\n")

    ensure_api_key()
    rag = FalloutRAG()

    while True:
        question = input("You: ").strip()

        if question.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        if not question:
            continue

        print("\nAssistant: ", end="")
        answer = rag.ask(question)
        print(answer)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
