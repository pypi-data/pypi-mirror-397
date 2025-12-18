"""
Pipeline Marketplace API Routes.

Provides HTTP API for the pipeline marketplace.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.marketplace import (
    Collection,
    CreateCollectionRequest,
    CreateListingRequest,
    InstallationRecord,
    InstallListingRequest,
    ListingCategory,
    ListingReview,
    MarketplaceListing,
    MarketplaceStats,
    PricingModel,
    Publisher,
    PublishVersionRequest,
    SearchListingsRequest,
    SearchListingsResponse,
    SubmitReviewRequest,
    UpdateListingRequest,
    UserLibrary,
)
from flowmason_studio.services.marketplace_service import get_marketplace_service

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# =============================================================================
# Discovery
# =============================================================================


@router.get("/featured", response_model=List[MarketplaceListing])
async def get_featured_listings(
    limit: int = Query(10, ge=1, le=50),
) -> List[MarketplaceListing]:
    """
    Get featured marketplace listings.

    Featured listings are hand-picked by the FlowMason team
    for quality and usefulness.
    """
    service = get_marketplace_service()
    return service.get_featured_listings(limit)


@router.get("/trending", response_model=List[MarketplaceListing])
async def get_trending_listings(
    limit: int = Query(10, ge=1, le=50),
) -> List[MarketplaceListing]:
    """
    Get trending listings based on recent activity.
    """
    service = get_marketplace_service()
    return service.get_trending_listings(limit)


@router.get("/new", response_model=List[MarketplaceListing])
async def get_new_listings(
    limit: int = Query(10, ge=1, le=50),
) -> List[MarketplaceListing]:
    """
    Get the newest marketplace listings.
    """
    service = get_marketplace_service()
    return service.get_new_listings(limit)


@router.get("/categories/{category}", response_model=List[MarketplaceListing])
async def get_category_listings(
    category: ListingCategory,
    limit: int = Query(20, ge=1, le=100),
) -> List[MarketplaceListing]:
    """
    Get listings in a specific category.
    """
    service = get_marketplace_service()
    return service.get_listings_by_category(category, limit)


@router.post("/search", response_model=SearchListingsResponse)
async def search_listings(request: SearchListingsRequest) -> SearchListingsResponse:
    """
    Search marketplace listings.

    Supports filtering by category, tags, pricing, rating, and more.
    """
    service = get_marketplace_service()
    return service.search_listings(request)


@router.get("/search", response_model=SearchListingsResponse)
async def search_listings_get(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[ListingCategory] = None,
    pricing: Optional[PricingModel] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    verified_only: bool = False,
    sort_by: str = Query("relevance"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> SearchListingsResponse:
    """
    Search marketplace listings (GET convenience endpoint).
    """
    service = get_marketplace_service()
    request = SearchListingsRequest(
        query=query,
        category=category,
        pricing=pricing,
        min_rating=min_rating,
        verified_only=verified_only,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )
    return service.search_listings(request)


# =============================================================================
# Listings
# =============================================================================


@router.post("/listings", response_model=MarketplaceListing)
async def create_listing(request: CreateListingRequest) -> MarketplaceListing:
    """
    Create a new marketplace listing.

    The listing is created in draft status and must be submitted
    for review before it can be published.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_publisher"
    username = "Publisher"

    return service.create_listing(
        user_id=user_id,
        username=username,
        name=request.name,
        tagline=request.tagline,
        description=request.description,
        category=request.category,
        pipeline_template=request.pipeline_template,
        tags=request.tags,
        pricing=request.pricing,
        readme=request.readme,
    )


@router.get("/listings/{listing_id}", response_model=MarketplaceListing)
async def get_listing(listing_id: str) -> MarketplaceListing:
    """
    Get a listing by ID.
    """
    service = get_marketplace_service()
    listing = service.get_listing(listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Record view
    service.record_view(listing_id)

    return listing


@router.get("/listings/by-slug/{slug}", response_model=MarketplaceListing)
async def get_listing_by_slug(slug: str) -> MarketplaceListing:
    """
    Get a listing by its URL slug.
    """
    service = get_marketplace_service()
    listing = service.get_listing_by_slug(slug)

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    service.record_view(listing.id)
    return listing


@router.patch("/listings/{listing_id}", response_model=MarketplaceListing)
async def update_listing(
    listing_id: str,
    request: UpdateListingRequest,
) -> MarketplaceListing:
    """
    Update a listing.

    Only the listing owner can update their listing.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_publisher"

    listing = service.update_listing(
        listing_id=listing_id,
        user_id=user_id,
        **request.model_dump(exclude_none=True),
    )

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Listing not found or you don't have permission"
        )

    return listing


@router.post("/listings/{listing_id}/submit")
async def submit_for_review(listing_id: str) -> dict:
    """
    Submit a listing for review.

    The listing will be reviewed by the FlowMason team
    before it can be published.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_publisher"

    success = service.submit_for_review(listing_id, user_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot submit listing for review"
        )

    return {"success": True, "message": "Listing submitted for review"}


@router.post("/listings/{listing_id}/archive")
async def archive_listing(listing_id: str) -> dict:
    """
    Archive a listing.

    Archived listings are no longer visible in the marketplace.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_publisher"

    success = service.archive_listing(listing_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")

    return {"success": True}


@router.post("/listings/{listing_id}/versions", response_model=dict)
async def publish_version(
    listing_id: str,
    request: PublishVersionRequest,
) -> dict:
    """
    Publish a new version of a listing.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_publisher"

    version = service.publish_version(
        listing_id=listing_id,
        user_id=user_id,
        version=request.version,
        changelog=request.changelog,
        pipeline_template=request.pipeline_template,
        min_flowmason_version=request.min_flowmason_version,
    )

    if not version:
        raise HTTPException(status_code=404, detail="Listing not found")

    return {"success": True, "version": version.model_dump()}


# =============================================================================
# Reviews
# =============================================================================


@router.post("/listings/{listing_id}/reviews", response_model=ListingReview)
async def submit_review(
    listing_id: str,
    request: SubmitReviewRequest,
) -> ListingReview:
    """
    Submit a review for a listing.

    Users can only submit one review per listing.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_reviewer"
    username = "Reviewer"

    review = service.submit_review(
        listing_id=listing_id,
        user_id=user_id,
        username=username,
        rating=request.rating,
        title=request.title,
        content=request.content,
    )

    if not review:
        raise HTTPException(
            status_code=400,
            detail="Cannot submit review (already reviewed or listing not found)"
        )

    return review


@router.get("/listings/{listing_id}/reviews", response_model=List[ListingReview])
async def get_reviews(
    listing_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ListingReview]:
    """
    Get reviews for a listing.
    """
    service = get_marketplace_service()
    return service.get_reviews(listing_id, limit, offset)


@router.post("/listings/{listing_id}/reviews/{review_id}/helpful")
async def mark_review_helpful(listing_id: str, review_id: str) -> dict:
    """
    Mark a review as helpful.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.mark_review_helpful(listing_id, review_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")

    return {"success": True}


# =============================================================================
# Installation
# =============================================================================


@router.post("/listings/{listing_id}/install", response_model=InstallationRecord)
async def install_listing(
    listing_id: str,
    request: InstallListingRequest,
) -> InstallationRecord:
    """
    Install a listing.

    This downloads the pipeline template and optionally creates
    a new pipeline from it.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    record = service.install_listing(
        listing_id=listing_id,
        user_id=user_id,
        version=request.version,
        customizations=request.customizations,
    )

    if not record:
        raise HTTPException(status_code=404, detail="Listing not found")

    return record


@router.get("/installations", response_model=List[InstallationRecord])
async def get_my_installations() -> List[InstallationRecord]:
    """
    Get all installations for the current user.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    return service.get_user_installations(user_id)


# =============================================================================
# User Library
# =============================================================================


@router.get("/library", response_model=UserLibrary)
async def get_my_library() -> UserLibrary:
    """
    Get the current user's library.

    Includes favorites, purchased, and installed listings.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    return service.get_user_library(user_id)


@router.post("/library/favorites/{listing_id}")
async def add_to_favorites(listing_id: str) -> dict:
    """
    Add a listing to favorites.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.add_to_favorites(user_id, listing_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")

    return {"success": True}


@router.delete("/library/favorites/{listing_id}")
async def remove_from_favorites(listing_id: str) -> dict:
    """
    Remove a listing from favorites.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    service.remove_from_favorites(user_id, listing_id)
    return {"success": True}


# =============================================================================
# Collections
# =============================================================================


@router.get("/collections", response_model=List[Collection])
async def list_collections(
    limit: int = Query(20, ge=1, le=100),
) -> List[Collection]:
    """
    Get curated collections.
    """
    service = get_marketplace_service()
    return service.get_collections(limit)


@router.post("/collections", response_model=Collection)
async def create_collection(request: CreateCollectionRequest) -> Collection:
    """
    Create a new collection.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_curator"

    return service.create_collection(
        user_id=user_id,
        name=request.name,
        description=request.description,
        listing_ids=request.listing_ids,
    )


@router.get("/collections/{collection_id}", response_model=Collection)
async def get_collection(collection_id: str) -> Collection:
    """
    Get a collection by ID.
    """
    service = get_marketplace_service()
    collection = service.get_collection(collection_id)

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return collection


@router.post("/collections/{collection_id}/listings/{listing_id}")
async def add_to_collection(collection_id: str, listing_id: str) -> dict:
    """
    Add a listing to a collection.
    """
    service = get_marketplace_service()

    # TODO: Get actual user from auth context
    user_id = "user_curator"

    success = service.add_to_collection(collection_id, listing_id, user_id)
    if not success:
        raise HTTPException(
            status_code=403,
            detail="Cannot add to collection"
        )

    return {"success": True}


# =============================================================================
# Publishers
# =============================================================================


@router.get("/publishers/{publisher_id}", response_model=Publisher)
async def get_publisher(publisher_id: str) -> Publisher:
    """
    Get a publisher's profile.
    """
    service = get_marketplace_service()
    publisher = service.get_publisher(publisher_id)

    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")

    return publisher


@router.get("/publishers/{publisher_id}/listings", response_model=List[MarketplaceListing])
async def get_publisher_listings(
    publisher_id: str,
    include_drafts: bool = Query(False),
) -> List[MarketplaceListing]:
    """
    Get all listings by a publisher.
    """
    service = get_marketplace_service()

    # TODO: Only show drafts to the publisher themselves
    return service.get_publisher_listings(publisher_id, include_drafts=False)


# =============================================================================
# Stats
# =============================================================================


@router.get("/stats", response_model=MarketplaceStats)
async def get_marketplace_stats() -> MarketplaceStats:
    """
    Get overall marketplace statistics.
    """
    service = get_marketplace_service()
    return service.get_marketplace_stats()


# =============================================================================
# Categories
# =============================================================================


class CategoryInfo(BaseModel):
    """Information about a category."""

    id: str
    name: str
    description: str
    icon: str
    listing_count: int


CATEGORY_INFO = {
    ListingCategory.AI_GENERATION: {
        "name": "AI Generation",
        "description": "Pipelines for AI-powered content generation",
        "icon": "sparkles",
    },
    ListingCategory.DATA_PROCESSING: {
        "name": "Data Processing",
        "description": "Transform, validate, and clean data",
        "icon": "database",
    },
    ListingCategory.INTEGRATION: {
        "name": "Integration",
        "description": "Connect to external APIs and services",
        "icon": "plug",
    },
    ListingCategory.AUTOMATION: {
        "name": "Automation",
        "description": "Automate repetitive tasks and workflows",
        "icon": "cog",
    },
    ListingCategory.ANALYTICS: {
        "name": "Analytics",
        "description": "Analyze data and generate insights",
        "icon": "chart-bar",
    },
    ListingCategory.CONTENT: {
        "name": "Content",
        "description": "Content moderation and management",
        "icon": "document-text",
    },
    ListingCategory.DEVOPS: {
        "name": "DevOps",
        "description": "CI/CD, deployment, and infrastructure",
        "icon": "server",
    },
    ListingCategory.OTHER: {
        "name": "Other",
        "description": "Miscellaneous pipelines",
        "icon": "cube",
    },
}


@router.get("/categories", response_model=List[CategoryInfo])
async def list_categories() -> List[CategoryInfo]:
    """
    List all marketplace categories.
    """
    service = get_marketplace_service()
    stats = service.get_marketplace_stats()

    categories = []
    for cat, info in CATEGORY_INFO.items():
        categories.append(
            CategoryInfo(
                id=cat.value,
                name=info["name"],
                description=info["description"],
                icon=info["icon"],
                listing_count=stats.categories.get(cat.value, 0),
            )
        )

    return categories
