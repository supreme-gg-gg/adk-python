#!/usr/bin/env python3
"""
Demo script showing the difference between agents with and without
comprehensive skills system prompts.
"""

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent_with_system_prompt import app_with_full_prompt, app_with_minimal_prompt


async def test_agent(app, test_query: str, app_description: str):
    """Test an agent with a specific query."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {app_description}")
    print(f"Query: {test_query}")
    print(f"{'=' * 60}")

    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        user_id="demo_user", app_name=app.name
    )

    print("\nAgent Response:")
    print("-" * 40)

    response_text = ""
    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=test_query)]
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="")
                    response_text += part.text

    print("\n" + "-" * 40)
    await runner.close()

    return response_text


async def main():
    """Run comparison demo."""

    print("Skills System Prompt Demonstration")
    print("==================================")
    print(
        "This demo shows how different system prompts affect agent behavior with skills."
    )

    test_queries = [
        "What can you help me with?",
        "I need to extract text from a PDF file. Can you help?",
        "I have a dataset I want to analyze. What should I do?",
        "Can you show me what skills you have available?",
    ]

    for query in test_queries:
        # Test agent with comprehensive skills prompt
        await test_agent(
            app_with_full_prompt, query, "Agent with Comprehensive Skills System Prompt"
        )

        # Test agent with minimal prompt (plugin adds skills guidance)
        await test_agent(
            app_with_minimal_prompt,
            query,
            "Agent with Minimal Prompt + Plugin Enhancement",
        )

        print("\n" + "=" * 60)
        print("COMPARISON COMPLETE")
        print("=" * 60)

        input("\nPress Enter to continue to next query...")


if __name__ == "__main__":
    asyncio.run(main())
