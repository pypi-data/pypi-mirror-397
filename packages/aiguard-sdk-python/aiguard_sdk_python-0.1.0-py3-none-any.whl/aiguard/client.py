import requests
import time
from functools import wraps


class AIGuard:
    """AIGuard client for monitoring and logging AI model invocations."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:5000/api"):
        """
        Initialize the AIGuard client.

        Args:
            api_key: Your AIGuard API key
            base_url: Base URL for the AIGuard API (default: http://localhost:5000/api)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict:
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def log(self, data: dict) -> None:
        """
        Log a model call to AIGuard (fire-and-forget).

        Args:
            data: Log data containing model, input, output, latency, tokens, status, etc.
        """
        try:
            requests.post(
                f"{self.base_url}/logs",
                json=data,
                headers=self._headers(),
            )
        except Exception as e:
            print(f"AIGuard Logging Failed: {e}")

    def start_invocation(self, data: dict) -> dict:
        """
        Start an invocation (signals the beginning of an AI model call).

        Args:
            data: Invocation data containing:
                - eventId (required): Unique identifier for this invocation
                - event (required): Event type/name
                - userId (required): User identifier
                - inputMessage (optional): Input message to the model
                - model (optional): Model name/identifier
                - convoId (optional): Conversation identifier
                - properties (optional): Additional custom properties

        Returns:
            The created invocation object

        Raises:
            requests.exceptions.RequestException: If the API call fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/invocations",
                json=data,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"AIGuard Start Invocation Failed: {e}")
            raise

    def end_invocation(self, data: dict) -> dict:
        """
        End an invocation (signals the completion of an AI model call).

        Args:
            data: End invocation data containing:
                - eventId (required): The eventId of the invocation to end
                - output (optional): Output from the model call

        Returns:
            The updated invocation object

        Raises:
            requests.exceptions.RequestException: If the API call fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/invocations/end",
                json=data,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"AIGuard End Invocation Failed: {e}")
            raise

    def wrap_openai(self, client):
        """
        Wrap an OpenAI client to automatically log all chat completion calls.

        Args:
            client: An OpenAI client instance

        Returns:
            The wrapped OpenAI client with automatic logging
        """
        original_create = client.chat.completions.create

        @wraps(original_create)
        def wrapped_create(*args, **kwargs):
            start_time = time.time()
            response = None
            error = None
            status = "success"

            try:
                response = original_create(*args, **kwargs)
                return response
            except Exception as e:
                error = str(e)
                status = "error"
                raise
            finally:
                end_time = time.time()
                latency = int((end_time - start_time) * 1000)  # Convert to ms

                # Extract input
                input_messages = kwargs.get("messages", args[0] if args else None)

                # Extract output & tokens if success
                output = None
                tokens = None

                if response:
                    output = response.choices[0].message.content
                    if response.usage:
                        tokens = {
                            "prompt": response.usage.prompt_tokens,
                            "completion": response.usage.completion_tokens,
                            "total": response.usage.total_tokens,
                        }

                # Fire and forget log
                self.log({
                    "model": kwargs.get("model", "openai-unknown"),
                    "input": input_messages,
                    "output": output,
                    "latency": latency,
                    "tokens": tokens,
                    "status": status,
                    "error": error,
                    "metadata": kwargs,
                })

        client.chat.completions.create = wrapped_create
        return client
