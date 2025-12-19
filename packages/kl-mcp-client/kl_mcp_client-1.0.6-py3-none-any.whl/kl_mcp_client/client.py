# mcp_client.py
import time
import uuid
from typing import Any, Dict, List, Optional

import requests

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


class MCPError(Exception):
    pass


class MCPClient:
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retries: int = 1,
    ):
        """
        base_url: full MCP HTTP endpoint e.g. http://localhost:3000/mcp
        headers: extra headers (e.g. {"Authorization": "Bearer ..."})
        timeout: request timeout seconds
        retries: number of attempts for network errors
        """
        self.base_url = base_url.rstrip("/")
        self.headers = DEFAULT_HEADERS.copy()
        if headers:
            self.headers.update(headers)
        self.timeout = timeout
        self.retries = max(1, int(retries))
        # local cache of sessions -> can be used to reuse session ids
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def _rpc(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        last_exc = None
        for attempt in range(self.retries):
            try:
                r = requests.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                r.raise_for_status()
            except requests.RequestException as e:
                last_exc = e
                time.sleep(0.2 * (attempt + 1))
                continue

            try:
                data = r.json()
            except ValueError:
                raise MCPError(
                    f"Invalid JSON response (status {r.status_code}): {r.text}"
                )

            if "error" in data and data["error"] is not None:
                err = data["error"]
                raise MCPError(
                    {
                        "code": err.get("code"),
                        "message": err.get("message"),
                        "data": err.get("data"),
                    }
                )
            return data.get("result", {})

        # all retries failed
        raise MCPError(f"Request failed after {self.retries} attempts: {last_exc}")

    # ----- Generic callTool wrapper -----
    def call_tool_structured(
        self, tool: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        args = {"tool": tool, "arguments": arguments or {}}
        res = self._rpc("callTool", args)
        # return structuredContent when possible
        if isinstance(res, dict) and "structuredContent" in res:
            return res["structuredContent"]
        # fallback: maybe top-level result
        return res

    # ----- Generic callTool wrapper -----
    def call_tool(
        self, tool: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        args = {"tool": tool, "arguments": arguments or {}}
        res = self._rpc("callTool", args)
        # # return structuredContent when possible
        # if isinstance(res, dict) and "structuredContent" in res:
        #     return res["structuredContent"]
        # # fallback: maybe top-level result
        return res

    # ----- Session helpers -----
    def create_session(self, cdpUrl: str) -> str:
        result = self.call_tool_structured("createSession", {"cdpUrl": cdpUrl})
        # Many MCP servers put sessionId in structuredContent.sessionId or result.sessionId
        session_id = None
        if isinstance(result, dict):
            session_id = (
                result.get("sessionId") or result.get("session_id") or result.get("id")
            )
        if not session_id:
            # fallback: try raw result text or content
            raise MCPError("createSession did not return sessionId")
        # store meta
        self._sessions[session_id] = {"created_at": time.time()}
        return session_id

    def close_session(self, session_id: str) -> bool:
        try:
            self.call_tool_structured("closeSession", {"sessionId": session_id})
            if session_id in self._sessions:
                del self._sessions[session_id]
            return True
        except MCPError:
            # still remove local record if present
            self._sessions.pop(session_id, None)
            raise

    def list_local_sessions(self) -> List[str]:
        return list(self._sessions.keys())
