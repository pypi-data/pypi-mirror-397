from __future__ import annotations
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime

class ChatHistory:
    def __init__(self) -> None:
        self._messages: Dict[str, Dict[str, Any]] = {}

    # ---- add ----
    def add_message(self, message: Dict[str, Any]) -> None:
        self._messages[message["id"]] = message

    def add_messages(self, message_list: List[Dict[str, Any]]) -> None:
        for m in message_list:
            self.add_message(m)

    # ---- read ----
    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._messages.values())

    def get_count(self) -> int:
        return len(self._messages)

    # ---- filtered / slices ----
    def get_filtered(self, filter_fn: Callable[[Dict[str, Any]], bool], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        filtered = [m for m in self._messages.values() if filter_fn(m)]
        return filtered[:limit] if limit else filtered

    def get_last_n(self, n: int) -> List[Dict[str, Any]]:
        # last N by insertion order 
        all_msgs = list(self._messages.values())
        return all_msgs[-n:]

    def get_by_type(self, msg_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.get_filtered(lambda m: m.get("type") == msg_type, limit=limit)

    def get_by_date_range(
        self,
        start: datetime,
        end: datetime,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        def _parse(dt: str) -> Optional[datetime]:
            if not dt:
                return None
            # handle ISO strings like "2025-10-29T09:01:57.32772+00:00"
            try:
                return datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except Exception:
                return None

        return self.get_filtered(
            lambda m: (
                (d := _parse(m.get("created_at"))) is not None and start <= d <= end
            ),
            limit=limit,
        )
    
    # 🔹 NEW: only user messages
    def get_user_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return only messages where type == 'user'.
        """
        return self.get_by_type("user", limit=limit)

    # 🔹 NEW: only model messages
    def get_model_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return only messages where type == 'model'.
        """
        return self.get_by_type("model", limit=limit)
    
    def to_openai_messages(
        self,
        limit: Optional[int] = None,
        include_images: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Convert stored messages to OpenAI chat history .
        - user  -> role: "user"
        - model -> role: "assistant"
        If include_images is True and a message has file_url, the final message
        uses the multimodal array format; otherwise it's plain text.
        """
        msgs = self.get_last_n(limit) if limit else self.get_all()

        out: List[Dict[str, Any]] = []
        for m in msgs:
            m_type = m.get("type")
            text = (m.get("text") or "").strip()
            file_url = (m.get("file_url") or "").strip()

            # map roles
            if m_type == "user":
                role = "user"
            elif m_type == "model":
                role = "assistant"
            else:
                # skip unknown roles
                continue

            # build content
            if include_images and file_url:
                content = []
                if text:
                    content.append({"type": "text", "text": text})
                content.append({"type": "image_url", "image_url": {"url": file_url}})
            else:
                # fall back to plain text (empty string if none)
                content = text

            out.append({"role": role, "content": content})

        return out