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

"""Utility for creating and accessing session-specific staging areas."""

import os
import tempfile
from pathlib import Path


def get_session_staging_path(
    session_id: str, app_name: str, skills_directory: Path
) -> Path:
    """Creates (if needed) and returns the path to a session's staging directory.

    This function provides a consistent, isolated filesystem environment for each
    session. It creates a root directory for the session and populates it with
    an 'uploads' folder and a symlink to the static 'skills' directory.

    Args:
        session_id: The unique ID of the current session.
        app_name: The name of the application, used for namespacing.
        skills_directory: The path to the static skills directory.

    Returns:
        The resolved path to the session's root staging directory.
    """
    base_path = Path(tempfile.gettempdir()) / "adk_sessions" / app_name
    session_path = base_path / session_id

    # Create the session and uploads directories
    (session_path / "uploads").mkdir(parents=True, exist_ok=True)

    # Symlink the static skills directory into the session directory
    if skills_directory and skills_directory.exists():
        skills_symlink = session_path / "skills"
        if not skills_symlink.exists():
            os.symlink(
                skills_directory.resolve(),
                skills_symlink,
                target_is_directory=True,
            )

    return session_path.resolve()
