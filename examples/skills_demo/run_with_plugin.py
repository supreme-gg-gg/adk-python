#!/usr/bin/env python3
"""
Example script showing how to run an agent with SkillsPlugin.
"""

import asyncio
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

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
    print("This agent has skills available through shell commands.")
    print("Try asking about:")
    print("- PDF processing tasks")
    print("- Data analysis tasks")
    print("- 'What skills do you have available?'")
    print("- 'List the available skills'")
    print("- 'Show me the PDF processing skill'")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ["quit", "exit"]:
                break

            print(f"\nAgent ({user_input}):")
            print("-" * 40)

            async for event in runner.run_async(
                user_id="demo_user",
                session_id=session.id,
                new_message=types.Content(
                    role="user", parts=[types.Part.from_text(text=user_input)]
                ),
            ):
                if event.content and event.content.parts:
                    for i, part in enumerate(event.content.parts):
                        if part.text:
                            print(f"  Text: {part.text.strip()}")
                        if part.function_call:
                            print(
                                f"  🔧 Function Call: {part.function_call.name}({part.function_call.args})"
                            )
                        if part.function_response:
                            print(
                                f"  📋 Function Response: {part.function_response.name}"
                            )
                            if part.function_response.response:
                                response_text = part.function_response.response.get(
                                    "result", str(part.function_response.response)
                                )
                                # Truncate long responses for readability
                                if len(response_text) > 200:
                                    response_text = (
                                        response_text[:200] + "... [truncated]"
                                    )
                                print(f"      Result: {response_text}")

            print("-" * 40)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

    await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
