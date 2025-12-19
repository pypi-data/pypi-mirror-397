from datetime import datetime
from functools import cached_property
from typing import Any, Literal

from langcodes import Language
from langcodes.tag_parser import LanguageTagError
from pydantic import ValidationInfo, field_validator, model_validator

from models.base import TaranisBaseModel


class NewsItem(TaranisBaseModel):
    _core_endpoint = "/assess/news-items"

    osint_source_id: str
    id: str | None = None
    hash: str | None = None
    title: str | None = None
    author: str | None = None
    review: str | None = None
    content: str | None = None
    link: str | None = None
    source: str | None = None
    published: datetime | None = None
    collected: datetime | None = None
    updated: datetime | None = None
    attributes: list[str | dict[str, Any]] | None = None
    story_id: str | None = None
    language: str | None = None
    last_change: str | None = None


class StoryTag(TaranisBaseModel):
    name: str
    size: int
    type: str | None = None


class Story(TaranisBaseModel):
    _core_endpoint = "/assess/stories"
    _model_name = "story"
    _pretty_name = "Story"
    _cache_timeout = 30

    id: str | None = None
    title: str | None = None
    description: str | None = None
    created: datetime | None = None
    updated: datetime | None = None
    last_change: str | None = None
    news_items: list[NewsItem] | None = None
    links: list[str] | None = None
    important: bool | None = None
    read: bool | None = None
    likes: int | None = None
    dislikes: int | None = None
    user_vote: Literal["like", "dislike", "", None] = None
    summary: str | None = None
    relevance: int | None = None
    comments: str | None = None
    in_reports_count: int | None = None
    tags: list[dict[str, Any]] | None = None
    attributes: list[dict[str, Any]] | None = None

    @cached_property
    def search_field(self) -> str:
        search = ""
        search += f"{self.title.lower() if self.title else ''} {self.description.lower() if self.description else ''} "
        if self.news_items:
            search += " ".join([item.title.lower() for item in self.news_items if item.title])
            search += " ".join([item.content.lower() for item in self.news_items if item.content])
            search += " ".join([item.source.lower() for item in self.news_items if item.source])
        return search


class AssessSource(TaranisBaseModel):
    id: str | None = None
    icon: str | None = None
    name: str
    type: str | None = None


class FilterLists(TaranisBaseModel):
    _core_endpoint = "/assess/filterlists"
    _model_name = "filter_lists"
    _pretty_name = "Filter Lists"

    tags: list[str] = []
    sources: list[AssessSource] = []
    groups: list[dict[str, Any]] = []


class StoryUpdatePayload(TaranisBaseModel):
    vote: Literal["like", "dislike", ""] | None = None
    important: bool | None = None
    read: bool | None = None
    title: str | None = None
    description: str | None = None
    comments: str | None = None
    summary: str | None = None
    tags: list[dict[str, Any]] | None = None
    attributes: list[dict[str, Any]] | None = None


class BulkAction(TaranisBaseModel):
    story_ids: list[str] = []
    payload: StoryUpdatePayload | None = None


class NewsItemCreate(TaranisBaseModel):
    osint_source_id: str
    title: str | None = None
    author: str | None = None
    review: str | None = None
    content: str | None = None
    link: str | None = None
    source: str | None = None
    published: datetime | None = None
    collected: datetime | None = None
    attributes: list[str | dict[str, Any]] | None = None
    language: str | None = None

    @field_validator("language", mode="before")
    def normalize_language_code(self, v: str, info: ValidationInfo) -> str:
        if v:
            try:
                return Language.get(v).language or ""
            except (LanguageTagError, ValueError, TypeError):
                return ""
        return ""

    @model_validator(mode="after")
    def check_required_fields(self) -> "NewsItemCreate":
        if not self.title and not self.content:
            raise ValueError("Either title or content must be provided for NewsItemCreate.")
        return self


class StoryCreate(TaranisBaseModel):
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    news_items: list[NewsItemCreate] = []
    tags: list[dict[str, Any]] | None = None
    attributes: list[dict[str, Any]] | None = None
    created: datetime | None = None
