from __future__ import annotations

import re

_GREETING_PATTERNS = (
    r"^\s*xin\s+chào\s*$",
    r"^\s*chào\s*$",
    r"^\s*hello\s*$",
    r"^\s*hi\s*$",
    r"^\s*good\s+morning\s*$",
    r"^\s*good\s+afternoon\s*$",
    r"^\s*good\s+evening\s*$",
    r"^\s*cảm\s+ơn\s*$",
    r"^\s*thanks?\s*$",
    r"^\s*ok(?:ay)?\s*$",
)

_LEGAL_KEYWORDS = (
    "luật",
    "pháp luật",
    "điều ",
    "bộ luật",
    "nghị định",
    "thông tư",
    "tội ",
    "hình phạt",
    "xử phạt",
    "bị cấm",
    "nghiêm cấm",
    "tàng trữ",
    "mua bán",
    "vận chuyển",
    "sử dụng trái phép",
    "ma túy",
    "ma tuý",
    "cai nghiện",
    "chất ma túy",
    "chất ma tuý",
    "tiền chất",
)

_NEWS_KEYWORDS = (
    "tin tức",
    "báo",
    "vụ án",
    "nghệ sĩ",
    "ca sĩ",
    "diễn viên",
    "mới nhất",
    "gần đây",
)


def normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def is_greeting(text: str) -> bool:
    query = normalize_query(text)
    return any(re.match(pattern, query, flags=re.IGNORECASE) for pattern in _GREETING_PATTERNS)


def is_legal_query(text: str) -> bool:
    query = normalize_query(text)
    return any(keyword in query for keyword in _LEGAL_KEYWORDS)


def is_news_query(text: str) -> bool:
    query = normalize_query(text)
    return any(keyword in query for keyword in _NEWS_KEYWORDS)


def classify_query(text: str) -> str:
    if is_greeting(text):
        return "greeting"
    if is_legal_query(text):
        return "legal"
    if is_news_query(text):
        return "news"
    return "other"

