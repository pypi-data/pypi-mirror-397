"""HTTP client for the experiment tracking API."""

import logging
from typing import Any, cast

import httpx

from .types import Rollout, Scalar

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when an API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class Client:
    """HTTP client for the experiment tracking API."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key

        self._client = httpx.Client(headers=headers, timeout=timeout)

    def create_experiment(
        self, name: str | None = None, config: dict[str, Any] | None = None
    ) -> str:
        """
        Create a new experiment.

        Args:
            name: Experiment name. If not provided, a random name is generated on the server.
            config: Initial experiment configuration.

        Returns the experiment ID.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if config is not None:
            payload["config"] = config

        response = self._request("POST", "/api/experiments", json=payload)
        return cast(str, response["experimentId"])

    def log_scalars(self, experiment_id: str, scalars: list[Scalar]) -> dict[str, Any]:
        """Log scalar metrics for an experiment (non-blocking)."""
        payload = {
            "scalars": [
                {
                    "step": s.step,
                    "mode": s.mode,
                    "type": s.type,
                    "value": s.value,
                }
                for s in scalars
            ]
        }
        return self._request(
            "POST",
            f"/api/experiments/{experiment_id}/scalars",
            json=payload,
            fire_and_forget=True,
        )

    def log_rollouts(self, experiment_id: str, rollouts: list[Rollout]) -> dict[str, Any]:
        """Log rollouts for an experiment (non-blocking)."""
        payload = {
            "rollouts": [
                {
                    "step": r.step,
                    "mode": r.mode,
                    "promptText": r.prompt_text,
                    "messages": [{"role": m.role, "content": m.content} for m in r.messages],
                    "rewards": [{"name": rw.name, "value": rw.value} for rw in r.rewards],
                }
                for r in rollouts
            ]
        }
        logger.debug(f"[rollouts] Sending payload: {payload}")
        return self._request(
            "POST",
            f"/api/experiments/{experiment_id}/rollouts",
            json=payload,
            fire_and_forget=True,
        )

    def update_experiment(
        self,
        experiment_id: str,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        Update an experiment's name, config, and/or status.

        Args:
            experiment_id: The experiment ID.
            name: New experiment name (optional).
            config: New experiment configuration (optional).
            status: New experiment status (optional).

        Returns:
            Response with success status.
        """
        if name is None and config is None and status is None:
            raise ValueError("At least one of name, config, or status must be provided")

        payload: dict[str, Any] = {"id": experiment_id}
        if name is not None:
            payload["name"] = name
        if config is not None:
            payload["config"] = config
        if status is not None:
            payload["status"] = status

        return self._request("PUT", "/api/experiments", json=payload)

    def log_config(self, experiment_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """Log configuration for an experiment."""
        return self.update_experiment(experiment_id, config=config)

    def end_experiment(self, experiment_id: str) -> dict[str, Any]:
        """Mark an experiment as finished."""
        return self.update_experiment(experiment_id, status="complete")

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        fire_and_forget: bool = False,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            json: JSON payload
            fire_and_forget: If True, send request without waiting for response.
                           Used for logging operations to avoid blocking.
        """
        url = f"{self.base_url}{path}"

        try:
            if fire_and_forget:
                # Fire and forget - don't wait for response
                # This makes logging operations non-blocking
                response = self._client.post(url, json=json)
                # Log errors but don't raise them
                if not response.is_success:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", response.text)
                    except ValueError:
                        error_msg = response.text
                    logger.error(
                        f"[rollouts] Error: {error_msg}"
                    )
                return {}

            response = self._client.request(
                method=method,
                url=url,
                json=json,
            )
        except httpx.RequestError as e:
            if fire_and_forget:
                # Silently fail for fire-and-forget requests
                logger.warning(f"Fire-and-forget request exception: {method} {path} - {e}")
                return {}
            raise APIError(f"Request failed: {e}") from e

        if not response.is_success:
            try:
                error_data = response.json()
                message = error_data.get("error", response.text)
            except ValueError:
                message = response.text
            raise APIError(message, status_code=response.status_code)

        # Handle empty responses
        if not response.text:
            return {}

        return cast(dict[str, Any], response.json())

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
