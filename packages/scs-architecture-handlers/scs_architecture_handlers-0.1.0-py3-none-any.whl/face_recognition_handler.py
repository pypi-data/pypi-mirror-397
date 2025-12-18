"""FaceRecognitionHandler that calls our external FastAPI server.

Run this file directly to see the handler process a dummy frame. If no API
configuration is provided, it runs in dry-run mode and returns a stub result.
"""
from __future__ import annotations

import io
import os
import time
from typing import Any, Dict, Callable, Optional

import numpy as np
import requests
from PIL import Image

from base_handler import ArchitectureHandler


class FaceRecognitionHandler(ArchitectureHandler):
    """Handler that posts frames to a remote /detect endpoint.

    Parameters (in addition to base ArchitectureHandler):
    - api_key: Optional[str]     API key for the x-api-key header
    - process_stream: str        Value for the process-stream header (defaults to "default_stream")
    - dry_run: bool              If True, skip network call and return a stub result
    """

    REQUIRED_KEYS = {"frame", "timestamp"}

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        process_stream: str = "default_stream",
        dry_run: bool = False,
        # Base parameters
        host: Optional[str] = None,
        port: Optional[int] = None,
        auth: Any = None,
        run_as_thread: bool = True,
        disable_thread: bool = False,
        max_queue_size: int = 128,
        result_queue_size: Optional[int] = None,
        verbose: bool = False,
        expected_type: Optional[type] = None,
        network_timeout: Optional[float] = 10.0,
        client_id_prefix: str = "client",
        generate_results_callback: Optional[Callable[[Any, Dict[str, Any]], Any]] = None,  # type: ignore[name-defined]
    ):
        super().__init__(
            host=host,
            port=port,
            auth=auth,
            run_as_thread=run_as_thread,
            disable_thread=disable_thread,
            max_queue_size=max_queue_size,
            result_queue_size=result_queue_size,
            verbose=verbose,
            expected_type=expected_type,
            network_timeout=network_timeout,
            client_id_prefix=client_id_prefix,
            generate_results_callback=generate_results_callback,
        )
        # API config
        self.api_key: Optional[str] = api_key
        self.process_stream: str = process_stream
        self.dry_run: bool = bool(dry_run)
        # Default timeout for requests
        self._timeout: float = float(self.network_timeout or 10.0)

    # --- Validation / Preprocess ---
    def validate_item(self, item: Dict[str, Any], extra: Dict[str, Any]) -> bool:  # type: ignore[override]
        if not isinstance(item, dict):
            return False
        if not self.REQUIRED_KEYS.issubset(item.keys()):
            return False
        frame = item.get("frame")
        if not isinstance(frame, np.ndarray) or frame.ndim != 3:
            return False
        return True

    def preprocess_item(self, item: Dict[str, Any], extra: Dict[str, Any]):  # type: ignore[override]
        # Ensure the frame is uint8 for JPEG encoding
        frame = item["frame"]
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        return {**item, "frame": frame}, extra

    # --- Core generation ---
    def generate_results(self, item: Dict[str, Any], extra: Dict[str, Any]) -> Any:  # type: ignore[override]
        # Build payload for network request (image bytes + headers)
        payload = self._prepare_request_payload(item, extra)
        response = self.perform_request(payload)
        return response

    def postprocess_result(self, item: Dict[str, Any], extra: Dict[str, Any], result: Any) -> Any:  # type: ignore[override]
        # Attach original timestamp for downstream consumers
        if isinstance(result, dict):
            result = {**result, "ts": item["timestamp"]}
        return result

    # --- Networking helpers ---
    def _prepare_request_payload(self, item: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[override]
        frame: np.ndarray = item["frame"]
        # Convert numpy array (H, W, C) to JPEG bytes via PIL
        image = Image.fromarray(frame)
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=90)
        img_bytes = buf.getvalue()
        buf.close()

        return {
            "client_id": self.client_id,
            "image_bytes": img_bytes,
            "filename": f"frame_{int(time.time()*1000)}.jpg",
            "content_type": "image/jpeg",
            "headers": {
                # FastAPI converts underscores to hyphens for headers
                "x-api-key": self.api_key or "",
                "process-stream": self.process_stream,
            },
            "url": self._detect_url(),
            "timeout": self._timeout,
        }

    def _perform_request(self, payload: Dict[str, Any]):  # type: ignore[override]
        # In dry-run, return a stubbed result without network I/O
        if self.dry_run or not payload.get("url") or not self.api_key:
            # Minimal plausible structure to aid local testing
            return {
                "detectedPersons": [],
                "numPersons": 0,
                "fps": 0.0,
            }

        url = payload["url"]
        headers = payload.get("headers", {})
        files = {
            "file": (payload.get("filename", "frame.jpg"), payload["image_bytes"], payload.get("content_type", "application/octet-stream")),
        }
        timeout = payload.get("timeout", self._timeout)

        # Perform the HTTP POST
        resp = requests.post(url, headers=headers, files=files, timeout=timeout)
        resp.raise_for_status()
        # Expect JSON with keys: detectedPersons, numPersons, fps
        return resp.json()

    # --- URL helpers ---
    def _detect_url(self) -> Optional[str]:
        if not (self.host and self.port):
            return None
        base = f"http://{self.host}:{self.port}"
        return f"{base}/detect"


def _demo():
    # Read environment for convenience
    api_key = os.getenv("FR_API_KEY")
    process_stream = os.getenv("FR_PROCESS_STREAM", "default_stream")

    # Enable dry_run
    dry_run = True

    handler = FaceRecognitionHandler(
        host="localhost",
        port=443,
        api_key=api_key,
        process_stream=process_stream,
        dry_run=dry_run,
        run_as_thread=True,
        verbose=True,
        network_timeout=10.0,
    )

    # Create a dummy frame
    frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    handler.feed({"frame": frame, "timestamp": time.time()})
    result = handler.get_result(timeout=5.0)
    print("Result:", result)
    print("Stats:", handler.stats())
    handler.cleanup()


if __name__ == "__main__":
    _demo()
