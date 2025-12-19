"""Type definitions for Artanis SDK."""

from typing import Any, Callable, Dict, Optional, Union
from typing_extensions import TypedDict


class ArtanisConfig(TypedDict, total=False):
    """Configuration options for Artanis client."""

    api_key: str
    base_url: str
    enabled: bool
    debug: bool
    on_error: Optional[Callable[[Exception], None]]


class TraceData(TypedDict, total=False):
    """Internal trace data structure."""

    trace_id: str
    name: str
    metadata: Optional[Dict[str, Any]]
    inputs: Dict[str, Any]
    output: Optional[Any]
    state: Dict[str, Any]
    timestamp: str
    duration_ms: Optional[int]
    error: Optional[str]


class FeedbackData(TypedDict, total=False):
    """Feedback data structure."""

    trace_id: str
    rating: Union[str, float]
    comment: Optional[str]
    correction: Optional[Dict[str, Any]]
    timestamp: str


# Type aliases
Rating = Union[str, float]
Metadata = Dict[str, Any]
