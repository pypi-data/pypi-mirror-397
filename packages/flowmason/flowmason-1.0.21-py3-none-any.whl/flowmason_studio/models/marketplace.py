"""
Pipeline Marketplace Models.

Models for the pipeline marketplace - sharing and discovering pipelines.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ListingStatus(str, Enum):
    """Status of a marketplace listing."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ListingCategory(str, Enum):
    """Categories for marketplace listings."""

    AI_GENERATION = "ai_generation"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    CONTENT = "content"
    DEVOPS = "devops"
    OTHER = "other"


class PricingModel(str, Enum):
    """Pricing models for listings."""

    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"


class Publisher(BaseModel):
    """Publisher information."""

    id: str
    name: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    verified: bool = False
    member_since: str
    total_listings: int = 0
    total_downloads: int = 0
    average_rating: float = Field(default=0.0, ge=0, le=5)


class ListingPricing(BaseModel):
    """Pricing details for a listing."""

    model: PricingModel
    price: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD")
    trial_days: int = Field(default=0, ge=0)
    features: List[str] = Field(default_factory=list)


class ListingStats(BaseModel):
    """Statistics for a listing."""

    views: int = 0
    downloads: int = 0
    favorites: int = 0
    reviews: int = 0
    average_rating: float = Field(default=0.0, ge=0, le=5)
    weekly_downloads: int = 0
    monthly_downloads: int = 0


class ListingVersion(BaseModel):
    """A version of a listing."""

    version: str
    released_at: str
    changelog: str
    downloads: int = 0
    min_flowmason_version: Optional[str] = None
    deprecated: bool = False


class ComponentRequirement(BaseModel):
    """A required component for a listing."""

    component_type: str
    name: str
    optional: bool = False
    reason: Optional[str] = None


class IntegrationRequirement(BaseModel):
    """A required integration/API for a listing."""

    name: str
    type: str = Field(description="api, database, service, etc.")
    required: bool = True
    setup_url: Optional[str] = None


class ListingReview(BaseModel):
    """A review for a listing."""

    id: str
    listing_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    title: str
    content: str
    helpful_count: int = 0
    created_at: str
    updated_at: Optional[str] = None
    verified_purchase: bool = False
    publisher_response: Optional[str] = None
    publisher_response_at: Optional[str] = None


class ListingScreenshot(BaseModel):
    """A screenshot for a listing."""

    id: str
    url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    order: int = 0


class MarketplaceListing(BaseModel):
    """A pipeline listing in the marketplace."""

    # Identity
    id: str
    slug: str = Field(description="URL-friendly identifier")
    name: str
    tagline: str = Field(max_length=100)
    description: str

    # Classification
    category: ListingCategory
    tags: List[str] = Field(default_factory=list)
    status: ListingStatus

    # Publisher
    publisher: Publisher

    # Content
    pipeline_template: Dict[str, Any] = Field(
        description="The pipeline template/configuration"
    )
    readme: Optional[str] = Field(
        default=None,
        description="Detailed documentation in markdown"
    )
    screenshots: List[ListingScreenshot] = Field(default_factory=list)
    demo_video_url: Optional[str] = None

    # Requirements
    components: List[ComponentRequirement] = Field(default_factory=list)
    integrations: List[IntegrationRequirement] = Field(default_factory=list)
    min_flowmason_version: Optional[str] = None

    # Versioning
    current_version: str
    versions: List[ListingVersion] = Field(default_factory=list)

    # Pricing
    pricing: ListingPricing

    # Stats
    stats: ListingStats = Field(default_factory=ListingStats)

    # Metadata
    created_at: str
    updated_at: str
    published_at: Optional[str] = None
    featured: bool = False
    featured_until: Optional[str] = None

    # Support
    support_email: Optional[str] = None
    documentation_url: Optional[str] = None
    source_url: Optional[str] = None


class Collection(BaseModel):
    """A curated collection of listings."""

    id: str
    name: str
    description: str
    slug: str
    cover_image_url: Optional[str] = None
    listings: List[str] = Field(
        default_factory=list,
        description="Listing IDs"
    )
    curated_by: str
    created_at: str
    updated_at: str
    featured: bool = False


class UserLibrary(BaseModel):
    """A user's library of acquired listings."""

    user_id: str
    purchased: List[str] = Field(default_factory=list)
    favorites: List[str] = Field(default_factory=list)
    installed: List[str] = Field(default_factory=list)
    recently_viewed: List[str] = Field(default_factory=list)


class InstallationRecord(BaseModel):
    """Record of an installation."""

    id: str
    listing_id: str
    user_id: str
    version: str
    installed_at: str
    pipeline_id: Optional[str] = Field(
        default=None,
        description="ID of created pipeline"
    )
    customizations: Dict[str, Any] = Field(default_factory=dict)


# API Request/Response Models

class CreateListingRequest(BaseModel):
    """Request to create a listing."""

    name: str = Field(..., min_length=3, max_length=100)
    tagline: str = Field(..., max_length=100)
    description: str = Field(..., min_length=50)
    category: ListingCategory
    tags: List[str] = Field(default_factory=list, max_length=10)
    pipeline_template: Dict[str, Any]
    pricing: ListingPricing = Field(
        default_factory=lambda: ListingPricing(model=PricingModel.FREE)
    )
    readme: Optional[str] = None


class UpdateListingRequest(BaseModel):
    """Request to update a listing."""

    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ListingCategory] = None
    tags: Optional[List[str]] = None
    readme: Optional[str] = None
    pricing: Optional[ListingPricing] = None
    support_email: Optional[str] = None
    documentation_url: Optional[str] = None


class PublishVersionRequest(BaseModel):
    """Request to publish a new version."""

    version: str
    changelog: str = Field(..., min_length=10)
    pipeline_template: Dict[str, Any]
    min_flowmason_version: Optional[str] = None


class SubmitReviewRequest(BaseModel):
    """Request to submit a review."""

    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=20)


class InstallListingRequest(BaseModel):
    """Request to install a listing."""

    version: Optional[str] = Field(
        default=None,
        description="Version to install (latest if not specified)"
    )
    customizations: Dict[str, Any] = Field(default_factory=dict)
    create_pipeline: bool = Field(
        default=True,
        description="Whether to create a pipeline from the template"
    )
    pipeline_name: Optional[str] = None


class SearchListingsRequest(BaseModel):
    """Request to search listings."""

    query: Optional[str] = None
    category: Optional[ListingCategory] = None
    tags: Optional[List[str]] = None
    pricing: Optional[PricingModel] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    verified_only: bool = False
    sort_by: str = Field(
        default="relevance",
        description="relevance, downloads, rating, newest"
    )
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SearchListingsResponse(BaseModel):
    """Response with search results."""

    listings: List[MarketplaceListing]
    total: int
    page: int
    per_page: int
    total_pages: int


class CreateCollectionRequest(BaseModel):
    """Request to create a collection."""

    name: str = Field(..., min_length=3, max_length=100)
    description: str
    listing_ids: List[str] = Field(default_factory=list)


class MarketplaceStats(BaseModel):
    """Overall marketplace statistics."""

    total_listings: int
    total_publishers: int
    total_downloads: int
    total_reviews: int
    categories: Dict[str, int] = Field(
        description="Count per category"
    )
    trending: List[str] = Field(
        description="Trending listing IDs"
    )
    new_this_week: int
