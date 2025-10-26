#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interactive runner for the ADK Skills demo agent."""

import asyncio
import mimetypes
import pathlib

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import app


async def main():
    """Run an interactive chat session with the skills agent."""
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        user_id="demo_user", app_name=app.name
    )

    print("==================================")
    print("   ADK Agent Skills Demo          ")
    print("==================================")
    print("This agent can use a sandboxed shell to interact with skills.")
    print("You can attach a local file to your message when prompted.")
    print("Try asking about:")
    print("- PDF processing")
    print("- Data analysis (e.g., 'analyze this file' and attach a CSV)")
    print("- What skills do you have? / List your skills.")
    print("Type 'quit' or 'exit' to end the session.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                break

            file_path_str = input(
                "📎 Attach file (optional path, press Enter to skip): "
            ).strip()

            message_parts = [types.Part.from_text(text=user_input)]

            if file_path_str:
                file_path = pathlib.Path(file_path_str)
                if not file_path.exists():
                    print(f"\nFile not found: {file_path}\n")
                    continue

                print(f"\n📎 Attaching {file_path}...")
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = "application/octet-stream"

                # Read the file content as bytes and create the Part.
                file_bytes = file_path.read_bytes()
                file_part = types.Part.from_bytes(
                    data=file_bytes, mime_type=mime_type
                )
                message_parts.append(file_part)

            print("Agent:")
            print("------")

            async for event in runner.run_async(
                user_id="demo_user",
                session_id=session.id,
                new_message=types.Content(role="user", parts=message_parts),
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
                        if part.function_call:
                            print(
                                f"\n\n⚙️ Calling: {part.function_call.name}("
                                f"{part.function_call.args})"
                            )

            print("\n------\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    print("\nSession ended. Goodbye!")
    await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
