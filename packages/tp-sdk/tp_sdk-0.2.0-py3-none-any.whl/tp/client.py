import logging
import os
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

import httpx

from .errors import AuthError, NotFoundError, ServerError, TPError
from .models import SearchResult, Snippet, SnippetInput, UserInfo, Visibility

logger = logging.getLogger("tp-sdk")

class TeaserPaste:
    """
    TeaserPaste Client - The "One Word" Edition.
    Less typing, more pasting.
    """

    DEFAULT_BASE_URL = "https://paste-api.teaserverse.online"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10, base_url: Optional[str] = None):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url or os.getenv("TP_BASE_URL") or self.DEFAULT_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "TeaserPaste-SDK/0.1.0 (Python)"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _req(self, method: str, path: str, json: Optional[Dict] = None) -> Any:
        # url = f"{self.BASE_URL}{path}" # handled by base_url in client
        logger.debug(f"{method} {path}")

        try:
            # reuse self.client
            resp = self.client.request(method, path, json=json)

            if resp.status_code in (401, 403):
                raise AuthError(f"Nope ({resp.status_code}): {resp.text}")
            if resp.status_code == 404:
                raise NotFoundError(f"Gone ({resp.status_code}): {resp.text}")
            if resp.status_code >= 500:
                raise ServerError(f"Ouch ({resp.status_code}): {resp.text}")

            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            raise TPError(f"Network bad: {e}")

    # --- The "One Word" Public API ---

    def get(self, id: str, pwd: Optional[str] = None) -> Snippet:
        """Get a snippet."""
        payload = {"snippetId": id}
        if pwd: payload["password"] = pwd
        return Snippet(**self._req("POST", "/getSnippet", json=payload))

    def paste(self, data: SnippetInput) -> Snippet:
        """Create (Paste) a new snippet."""
        return Snippet(**self._req("POST", "/createSnippet", json=data.model_dump(by_alias=True)))

    def edit(self, id: str,
             title: Optional[str] = None,
             content: Optional[str] = None,
             language: Optional[str] = None,
             visibility: Optional[Visibility] = None,
             tags: Optional[List[str]] = None,
             password: Optional[str] = None,
             expires: Optional[str] = None,
             **kwargs) -> Snippet:
        """Update a snippet. Pass fields as arguments."""
        updates = {k: v for k, v in locals().items() if v is not None and k not in ('self', 'id', 'kwargs')}
        updates.update(kwargs)
        return Snippet(**self._req("PATCH", "/updateSnippet", json={"snippetId": id, "updates": updates}))

    def kill(self, id: str) -> bool:
        """Soft delete a snippet."""
        self._req("DELETE", "/deleteSnippet", json={"snippetId": id})
        return True

    def live(self, id: str) -> bool:
        """Restore (Resurrect) a deleted snippet."""
        self._req("POST", "/restoreSnippet", json={"snippetId": id})
        return True

    def star(self, id: str, on: bool = True) -> Dict[str, Any]:
        """Star (on=True) or Unstar (on=False)."""
        return self._req("POST", "/starSnippet", json={"snippetId": id, "star": on})

    def fork(self, id: str) -> Dict[str, str]:
        """Copy (Fork) a snippet to your account."""
        return self._req("POST", "/copySnippet", json={"snippetId": id})

    def ls(self, limit: int = 20, mode: Optional[Visibility] = None, skip: int = 0) -> List[Snippet]:
        """List MY snippets (ls)."""
        payload = {"limit": limit, "skip": skip}
        if mode: payload["visibility"] = mode
        return [Snippet(**i) for i in self._req("POST", "/listSnippets", json=payload)]

    def ls_iter(self, limit: int = 20, mode: Optional[Visibility] = None) -> Iterator[Snippet]:
        """Iterator for listing snippets (lazy loading)."""
        offset = 0
        while True:
            snippets = self.ls(limit=limit, mode=mode, skip=offset)
            if not snippets:
                break
            for snippet in snippets:
                yield snippet
            offset += len(snippets)
            if len(snippets) < limit:
                break

    def user(self, uid: str) -> List[Snippet]:
        """Get PUBLIC snippets of another USER."""
        return [Snippet(**i) for i in self._req("POST", "/getUserPublicSnippets", json={"userId": uid})]

    def find(self, q: str, size: int = 20, skip: int = 0) -> SearchResult:
        """Search (Find) snippets."""
        data = self._req("POST", "/searchSnippets", json={"term": q, "size": size, "from": skip})
        return SearchResult(hits=[Snippet(**h) for h in data.get("hits", [])], total=data.get("total", 0))

    def find_iter(self, q: str, size: int = 20) -> Iterator[Snippet]:
        """Iterator for finding snippets."""
        offset = 0
        while True:
            result = self.find(q=q, size=size, skip=offset)
            if not result.hits:
                break
            for snippet in result.hits:
                yield snippet
            offset += len(result.hits)
            if offset >= result.total:
                break

    def me(self) -> UserInfo:
        """Get MY info."""
        return UserInfo(**self._req("GET", "/getUserInfo"))


class AsyncTeaserPaste:
    """
    Async TeaserPaste Client.
    """

    DEFAULT_BASE_URL = "https://paste-api.teaserverse.online"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10, base_url: Optional[str] = None):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url or os.getenv("TP_BASE_URL") or self.DEFAULT_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "TeaserPaste-SDK/0.1.0 (Python)"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _req(self, method: str, path: str, json: Optional[Dict] = None) -> Any:
        logger.debug(f"{method} {path}")

        try:
            resp = await self.client.request(method, path, json=json)

            if resp.status_code in (401, 403):
                raise AuthError(f"Nope ({resp.status_code}): {resp.text}")
            if resp.status_code == 404:
                raise NotFoundError(f"Gone ({resp.status_code}): {resp.text}")
            if resp.status_code >= 500:
                raise ServerError(f"Ouch ({resp.status_code}): {resp.text}")

            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            raise TPError(f"Network bad: {e}")

    async def get(self, id: str, pwd: Optional[str] = None) -> Snippet:
        """Get a snippet."""
        payload = {"snippetId": id}
        if pwd: payload["password"] = pwd
        return Snippet(**await self._req("POST", "/getSnippet", json=payload))

    async def paste(self, data: SnippetInput) -> Snippet:
        """Create (Paste) a new snippet."""
        return Snippet(**await self._req("POST", "/createSnippet", json=data.model_dump(by_alias=True)))

    async def edit(self, id: str,
             title: Optional[str] = None,
             content: Optional[str] = None,
             language: Optional[str] = None,
             visibility: Optional[Visibility] = None,
             tags: Optional[List[str]] = None,
             password: Optional[str] = None,
             expires: Optional[str] = None,
             **kwargs) -> Snippet:
        """Update a snippet. Pass fields as arguments."""
        updates = {k: v for k, v in locals().items() if v is not None and k not in ('self', 'id', 'kwargs')}
        updates.update(kwargs)
        return Snippet(**await self._req("PATCH", "/updateSnippet", json={"snippetId": id, "updates": updates}))

    async def kill(self, id: str) -> bool:
        """Soft delete a snippet."""
        await self._req("DELETE", "/deleteSnippet", json={"snippetId": id})
        return True

    async def live(self, id: str) -> bool:
        """Restore (Resurrect) a deleted snippet."""
        await self._req("POST", "/restoreSnippet", json={"snippetId": id})
        return True

    async def star(self, id: str, on: bool = True) -> Dict[str, Any]:
        """Star (on=True) or Unstar (on=False)."""
        return await self._req("POST", "/starSnippet", json={"snippetId": id, "star": on})

    async def fork(self, id: str) -> Dict[str, str]:
        """Copy (Fork) a snippet to your account."""
        return await self._req("POST", "/copySnippet", json={"snippetId": id})

    async def ls(self, limit: int = 20, mode: Optional[Visibility] = None, skip: int = 0) -> List[Snippet]:
        """List MY snippets (ls)."""
        payload = {"limit": limit, "skip": skip}
        if mode: payload["visibility"] = mode
        return [Snippet(**i) for i in await self._req("POST", "/listSnippets", json=payload)]

    async def ls_iter(self, limit: int = 20, mode: Optional[Visibility] = None) -> AsyncIterator[Snippet]:
        """Async iterator for listing snippets (lazy loading)."""
        offset = 0
        while True:
            snippets = await self.ls(limit=limit, mode=mode, skip=offset)
            if not snippets:
                break
            for snippet in snippets:
                yield snippet
            offset += len(snippets)
            if len(snippets) < limit:
                break

    async def user(self, uid: str) -> List[Snippet]:
        """Get PUBLIC snippets of another USER."""
        return [Snippet(**i) for i in await self._req("POST", "/getUserPublicSnippets", json={"userId": uid})]

    async def find(self, q: str, size: int = 20, skip: int = 0) -> SearchResult:
        """Search (Find) snippets."""
        data = await self._req("POST", "/searchSnippets", json={"term": q, "size": size, "from": skip})
        return SearchResult(hits=[Snippet(**h) for h in data.get("hits", [])], total=data.get("total", 0))

    async def find_iter(self, q: str, size: int = 20) -> AsyncIterator[Snippet]:
        """Async iterator for finding snippets."""
        offset = 0
        while True:
            result = await self.find(q=q, size=size, skip=offset)
            if not result.hits:
                break
            for snippet in result.hits:
                yield snippet
            offset += len(result.hits)
            if offset >= result.total:
                break

    async def me(self) -> UserInfo:
        """Get MY info."""
        return UserInfo(**await self._req("GET", "/getUserInfo"))
