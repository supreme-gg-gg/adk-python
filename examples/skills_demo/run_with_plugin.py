#!/usr/bin/env python3
"""
Example script showing how to run an agent with SkillsPlugin.
"""

import asyncio
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

# from agent import app_with_plugin
from agent_with_system_prompt import app_with_full_prompt


async def main():
    """Run the agent with SkillsPlugin."""

    # Create runner with the app (includes SkillsPlugin)

    runner = InMemoryRunner(app=app_with_full_prompt)

    # Create a session
    session = await runner.session_service.create_session(
        user_id="demo_user", app_name=app_with_full_prompt.name
    )

    print("Skills Plugin Demo")
    print("==================")
    print("This agent has skills automatically available through the SkillsPlugin.")
    print("Try asking about:")
    print("- PDF processing tasks")
    print("- Data analysis tasks")
    print("- 'What skills do you have available?'")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ["quit", "exit"]:
                break

            print("\nAgent:", end=" ")

            async for event in runner.run_async(
                user_id="demo_user",
                session_id=session.id,
                new_message=types.Content(
                    role="user", parts=[types.Part.from_text(text=user_input)]
                ),
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="")

            print("\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

    await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
