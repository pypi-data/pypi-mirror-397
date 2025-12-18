"""Local Claude CLI provider (uses logged-in account, no API key)."""

import os
import subprocess
import shutil
import logging
from typing import Optional
from .base_provider import LLMProvider

logger = logging.getLogger(__name__)


class LocalClaudeProvider(LLMProvider):
    """
    Local Claude CLI provider.

    Uses the `claude` command from Anthropic Pro/Max plans.
    No API key needed - uses logged-in account.
    """

    def __init__(self, model: str = "claude-3-5-haiku-20241022"):
        """
        Initialize local Claude provider.

        Args:
            model: Claude model to use (currently fixed by CLI)
        """
        self.model = model
        self.command = "claude"

    def validate_availability(self) -> bool:
        """
        Check if `claude` CLI is installed and available.

        Returns:
            True if claude is in PATH, False otherwise
        """
        return shutil.which(self.command) is not None

    def analyze(self, transcript: str, prompt: str, **kwargs) -> str:
        """
        Send transcript + prompt to local Claude CLI.

        Args:
            transcript: The video transcript text
            prompt: The user's question/instruction
            **kwargs: Additional options (temperature, max_tokens, etc.)

        Returns:
            Claude's response as string

        Raises:
            FileNotFoundError: If claude CLI not found
            subprocess.CalledProcessError: If claude command fails
            Exception: For other errors
        """
        if not self.validate_availability():
            raise FileNotFoundError(
                "Claude CLI not found. Please install it first:\n"
                "  https://docs.anthropic.com/en/docs/cli\n\n"
                "Or use --api flag to use API keys instead."
            )

        # Build the full prompt with transcript
        full_prompt = f"{prompt}\n\nTranscript:\n{transcript}"

        # Build command
        # Use --print/-p for non-interactive mode
        cmd = [self.command, "--print"]

        # Add model selection
        # Use model alias (haiku, sonnet, opus) or full model name
        if self.model:
            # Extract model alias from full model name
            model_alias = self._get_model_alias(self.model)
            cmd.extend(["--model", model_alias])

        # Add optional parameters if provided
        # Note: Claude CLI doesn't support temperature/max-tokens via flags
        # These would need to be in config or API mode

        try:
            # Run claude with prompt via stdin
            logger.debug(f"Running: {' '.join(cmd)}")
            logger.debug(f"Prompt length: {len(full_prompt)} chars")

            # Remove ANTHROPIC_API_KEY from environment to force local CLI mode
            # (otherwise Claude CLI defaults to API mode if key is present)
            env = os.environ.copy()
            env.pop('ANTHROPIC_API_KEY', None)

            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )

            response = result.stdout.strip()

            if not response:
                raise Exception("Claude returned empty response")

            logger.debug(f"Response length: {len(response)} chars")
            return response

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            stdout_msg = e.stdout.strip() if e.stdout else ""
            logger.error(f"Claude CLI error: {error_msg}")
            logger.error(f"Claude CLI stdout: {stdout_msg}")

            # Check for common errors
            if "not logged in" in error_msg.lower():
                raise Exception(
                    "Not logged into Claude. Please run:\n"
                    "  claude login\n\n"
                    "Or use --api flag to use API keys instead."
                )
            elif "rate limit" in error_msg.lower():
                raise Exception(
                    f"Rate limit exceeded. Error: {error_msg}\n\n"
                    "Try again in a few moments or use --api flag."
                )
            else:
                # Include both stderr and stdout in error message for debugging
                full_error = f"stderr: {error_msg}"
                if stdout_msg:
                    full_error += f"\nstdout: {stdout_msg}"
                raise Exception(f"Claude CLI failed: {full_error}")

        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            raise

    def _get_model_alias(self, model: str) -> str:
        """
        Extract model alias from full model name.

        Args:
            model: Full model name (e.g., "claude-3-5-haiku-20241022")

        Returns:
            Model alias (e.g., "haiku") or full model name if no alias found
        """
        # Map full model names to aliases
        if "haiku" in model.lower():
            return "haiku"
        elif "sonnet" in model.lower():
            return "sonnet"
        elif "opus" in model.lower():
            return "opus"
        else:
            # Return full model name if no alias found
            return model

    def get_model_name(self) -> str:
        """Return the model identifier."""
        return self.model

    def estimate_cost(self, transcript: str, prompt: str) -> Optional[float]:
        """
        Local Claude is free within plan limits.

        Returns:
            None (no per-request cost)
        """
        return None
