from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api.errors import RequestError, ResponseFormatError
from llm_api.transport.client import send_payload


class TransportTests(unittest.TestCase):
    def test_send_payload_returns_json_dict(self) -> None:
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"ok": True}

        with mock.patch("llm_api.transport.client.requests.post", return_value=response):
            data = send_payload(
                payload={"x": 1},
                api_key="key",
                base_url="https://example.com/v1/responses",
                timeout=(1.0, 2.0),
            )

        self.assertEqual(data, {"ok": True})

    def test_timeout_raises_request_error(self) -> None:
        with mock.patch(
            "llm_api.transport.client.requests.post",
            side_effect=requests.exceptions.Timeout(),
        ):
            with self.assertRaises(RequestError):
                send_payload(
                    payload={"x": 1},
                    api_key="key",
                    base_url="https://example.com/v1/responses",
                    timeout=(1.0, 2.0),
                )

    def test_http_error_raises_request_error(self) -> None:
        response = mock.Mock(status_code=429)
        http_error = requests.exceptions.HTTPError(response=response)

        with mock.patch("llm_api.transport.client.requests.post") as mock_post:
            mock_post.return_value.raise_for_status.side_effect = http_error
            with self.assertRaises(RequestError):
                send_payload(
                    payload={"x": 1},
                    api_key="key",
                    base_url="https://example.com/v1/responses",
                    timeout=(1.0, 2.0),
                )

    def test_non_json_response_raises_response_format_error(self) -> None:
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("bad json")

        with mock.patch("llm_api.transport.client.requests.post", return_value=response):
            with self.assertRaises(ResponseFormatError):
                send_payload(
                    payload={"x": 1},
                    api_key="key",
                    base_url="https://example.com/v1/responses",
                    timeout=(1.0, 2.0),
                )


if __name__ == "__main__":
    unittest.main()
