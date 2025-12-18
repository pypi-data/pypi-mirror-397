"""Type definitions for the Nellie API SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

# Type aliases for literals to improve readability and autocomplete
BookStyle = Literal[
    "automatic",
    "action",
    "horror",
    "history",
    "sci_fi",
    "superhero",
    "mystery",
    "drama",
    "romance",
    "fantasy",
    "adventure",
    "crime",
    "western",
    "comedy",
    "epic",
    "thriller",
    "mythology",
    "folklore",
    "fable",
    "fairy_tale",
    "legend",
    "psychological",
    "suspense",
    "noir",
    "paranormal",
    "dystopian",
    "post_apocalyptic",
    "cyberpunk",
    "alternate_history",
    "gothic",
    "tragedy",
    "surrealism",
]

BookType = Literal[
    "automatic",
    "novel",
    "comic",
    "non_fiction",
    "manga",
    "textbook",
    "childrens",
    "self_help",
    "short_story",
]

ModelVersion = Literal["2.0", "3.0"]

OutputFormat = Literal["txt", "pdf", "epub", "md", "html", "json"]

# Status values returned by the API
BookStatus = Literal["queued", "processing", "completed", "failed", "unknown"]


@dataclass
class CreateBookParams:
    """Parameters for creating a new book."""

    prompt: str = ""
    style: BookStyle = "automatic"
    type: BookType = "automatic"
    images: bool = False
    author: str = "Nellie"
    custom_tone: str = ""
    model: ModelVersion = "2.0"
    output_format: OutputFormat = "pdf"
    webhook_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to a dictionary for API request."""
        return {
            "prompt": self.prompt,
            "style": self.style,
            "type": self.type,
            "images": self.images,
            "author": self.author,
            "custom_tone": self.custom_tone,
            "model": self.model,
            "output_format": self.output_format,
            "webhook_url": self.webhook_url,
        }


@dataclass
class Book:
    """Represents a book generation job."""

    request_id: str
    status: str
    message: Optional[str] = None
    status_url: Optional[str] = None

    # Additional fields populated for status/results
    progress: int = 0
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    credits_used: int = 0
    result_url: Optional[str] = None
    messages: List[str] = field(default_factory=list)
    error: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> Book:
        """Creates a Book instance from API response data.

        Args:
            data: Dictionary containing API response fields.

        Returns:
            Book: A new Book instance populated with the response data.
        """
        # Handle both 'error' and 'errorMessage' fields for compatibility
        error = data.get("error")
        error_message = data.get("errorMessage")
        # Use errorMessage as fallback for error if not present
        if not error and error_message:
            error = error_message

        return cls(
            request_id=data.get("requestId", ""),
            status=data.get("status", "unknown"),
            message=data.get("message"),
            status_url=data.get("statusUrl"),
            progress=data.get("progress", 0),
            created_at=data.get("createdAt"),
            completed_at=data.get("completedAt"),
            credits_used=data.get("creditsUsed", 0),
            result_url=data.get("resultUrl"),
            messages=data.get("messages", []),
            error=error,
            error_message=error_message,
        )

    def is_complete(self) -> bool:
        """Check if the book generation has finished (completed or failed)."""
        return self.status in ("completed", "failed")

    def is_successful(self) -> bool:
        """Check if the book generation completed successfully."""
        return self.status == "completed"


@dataclass
class Model:
    """Represents an available generation model."""

    id: str
    name: str
    description: str
    cost_per_book: int

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Model":
        """Creates a Model instance from API response data."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            cost_per_book=data.get("cost_per_book", 0),
        )


@dataclass
class Configuration:
    """Represents the available configuration options."""

    styles: List[str]
    types: List[str]
    formats: List[str]

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Configuration":
        """Creates a Configuration instance from API response data."""
        return cls(
            styles=data.get("styles", []),
            types=data.get("types", []),
            formats=data.get("formats", []),
        )


@dataclass
class UsageRequest:
    """Represents a single API request in usage history."""

    request_id: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    credits_used: int = 0

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "UsageRequest":
        """Creates a UsageRequest instance from API response data."""
        return cls(
            request_id=data.get("requestId", ""),
            status=data.get("status", "unknown"),
            created_at=data.get("createdAt"),
            completed_at=data.get("completedAt"),
            credits_used=data.get("creditsUsed", 0),
        )


@dataclass
class Usage:
    """Represents usage statistics for the authenticated user."""

    total_requests: int
    total_credits_used: int
    recent_requests: List[UsageRequest] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Usage":
        """Creates a Usage instance from API response data."""
        recent = [
            UsageRequest.from_api_response(r)
            for r in data.get("recentRequests", [])
        ]
        return cls(
            total_requests=data.get("totalRequests", 0),
            total_credits_used=data.get("totalCreditsUsed", 0),
            recent_requests=recent,
        )
