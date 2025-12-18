"""
Pipeline Marketplace Service.

Manages the pipeline marketplace for sharing and discovering pipelines.
"""

import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.marketplace import (
    Collection,
    ComponentRequirement,
    InstallationRecord,
    ListingCategory,
    ListingPricing,
    ListingReview,
    ListingScreenshot,
    ListingStats,
    ListingStatus,
    ListingVersion,
    MarketplaceListing,
    MarketplaceStats,
    PricingModel,
    Publisher,
    SearchListingsRequest,
    SearchListingsResponse,
    UserLibrary,
)


class MarketplaceService:
    """Service for managing the pipeline marketplace."""

    def __init__(self):
        """Initialize the marketplace service."""
        self._listings: Dict[str, MarketplaceListing] = {}
        self._publishers: Dict[str, Publisher] = {}
        self._reviews: Dict[str, List[ListingReview]] = {}  # listing_id -> reviews
        self._collections: Dict[str, Collection] = {}
        self._user_libraries: Dict[str, UserLibrary] = {}
        self._installations: Dict[str, List[InstallationRecord]] = {}  # user_id -> records
        self._slug_to_id: Dict[str, str] = {}

        # Initialize with sample data
        self._init_sample_data()

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return secrets.token_urlsafe(16)

    def _now(self) -> str:
        """Get current ISO timestamp."""
        return datetime.utcnow().isoformat() + "Z"

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')

    def _init_sample_data(self):
        """Initialize with sample marketplace data."""
        # Create a sample publisher
        publisher = Publisher(
            id="pub_flowmason",
            name="FlowMason Team",
            username="flowmason",
            verified=True,
            member_since="2024-01-01T00:00:00Z",
            total_listings=5,
            total_downloads=1000,
            average_rating=4.8,
        )
        self._publishers[publisher.id] = publisher

        # Sample listings
        sample_listings = [
            {
                "name": "Content Summarizer",
                "tagline": "Summarize long articles into concise key points",
                "description": "A complete pipeline for summarizing long-form content using AI. Supports multiple languages and output formats.",
                "category": ListingCategory.AI_GENERATION,
                "tags": ["summarization", "ai", "content", "nlp"],
                "pipeline_template": {
                    "name": "content-summarizer",
                    "stages": [
                        {"id": "input", "component_type": "variable_set"},
                        {"id": "summarize", "component_type": "generator", "depends_on": ["input"]},
                    ]
                },
            },
            {
                "name": "API Data Aggregator",
                "tagline": "Collect and combine data from multiple APIs",
                "description": "A flexible pipeline for fetching data from multiple REST APIs, transforming, and combining the results.",
                "category": ListingCategory.INTEGRATION,
                "tags": ["api", "integration", "data", "aggregation"],
                "pipeline_template": {
                    "name": "api-aggregator",
                    "stages": [
                        {"id": "fetch1", "component_type": "http_request"},
                        {"id": "fetch2", "component_type": "http_request"},
                        {"id": "combine", "component_type": "json_transform", "depends_on": ["fetch1", "fetch2"]},
                    ]
                },
            },
            {
                "name": "Content Moderation Pipeline",
                "tagline": "AI-powered content moderation for user submissions",
                "description": "Automatically moderate user-generated content for toxicity, spam, and policy violations.",
                "category": ListingCategory.CONTENT,
                "tags": ["moderation", "ai", "safety", "content"],
                "pipeline_template": {
                    "name": "content-moderation",
                    "stages": [
                        {"id": "analyze", "component_type": "generator"},
                        {"id": "classify", "component_type": "filter", "depends_on": ["analyze"]},
                    ]
                },
            },
            {
                "name": "Data Validation Pipeline",
                "tagline": "Validate and clean data before processing",
                "description": "A robust pipeline for validating data against schemas, cleaning, and transforming for downstream use.",
                "category": ListingCategory.DATA_PROCESSING,
                "tags": ["validation", "data", "schema", "cleaning"],
                "pipeline_template": {
                    "name": "data-validator",
                    "stages": [
                        {"id": "validate", "component_type": "schema_validate"},
                        {"id": "transform", "component_type": "json_transform", "depends_on": ["validate"]},
                    ]
                },
            },
            {
                "name": "Report Generator",
                "tagline": "Generate formatted reports from data",
                "description": "Transform raw data into professionally formatted reports with AI-generated insights.",
                "category": ListingCategory.ANALYTICS,
                "tags": ["reports", "analytics", "ai", "formatting"],
                "pipeline_template": {
                    "name": "report-generator",
                    "stages": [
                        {"id": "analyze", "component_type": "generator"},
                        {"id": "format", "component_type": "json_transform", "depends_on": ["analyze"]},
                    ]
                },
            },
        ]

        for i, data in enumerate(sample_listings):
            listing_id = f"listing_{i+1}"
            slug = self._slugify(data["name"])
            now = self._now()

            listing = MarketplaceListing(
                id=listing_id,
                slug=slug,
                name=data["name"],
                tagline=data["tagline"],
                description=data["description"],
                category=data["category"],
                tags=data["tags"],
                status=ListingStatus.PUBLISHED,
                publisher=publisher,
                pipeline_template=data["pipeline_template"],
                current_version="1.0.0",
                versions=[
                    ListingVersion(
                        version="1.0.0",
                        released_at=now,
                        changelog="Initial release",
                        downloads=100 + i * 50,
                    )
                ],
                pricing=ListingPricing(model=PricingModel.FREE),
                stats=ListingStats(
                    views=500 + i * 100,
                    downloads=100 + i * 50,
                    favorites=20 + i * 5,
                    reviews=5 + i,
                    average_rating=4.0 + (i * 0.2),
                ),
                created_at=now,
                updated_at=now,
                published_at=now,
                featured=i == 0,
            )

            self._listings[listing_id] = listing
            self._slug_to_id[slug] = listing_id
            self._reviews[listing_id] = []

    # =========================================================================
    # Listings
    # =========================================================================

    def create_listing(
        self,
        user_id: str,
        username: str,
        name: str,
        tagline: str,
        description: str,
        category: ListingCategory,
        pipeline_template: Dict[str, Any],
        tags: Optional[List[str]] = None,
        pricing: Optional[ListingPricing] = None,
        readme: Optional[str] = None,
    ) -> MarketplaceListing:
        """Create a new marketplace listing."""
        listing_id = self._generate_id()
        slug = self._slugify(name)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while slug in self._slug_to_id:
            slug = f"{base_slug}-{counter}"
            counter += 1

        now = self._now()

        # Get or create publisher
        publisher = self._publishers.get(user_id)
        if not publisher:
            publisher = Publisher(
                id=user_id,
                name=username,
                username=username.lower().replace(" ", "-"),
                member_since=now,
            )
            self._publishers[user_id] = publisher

        listing = MarketplaceListing(
            id=listing_id,
            slug=slug,
            name=name,
            tagline=tagline,
            description=description,
            category=category,
            tags=tags or [],
            status=ListingStatus.DRAFT,
            publisher=publisher,
            pipeline_template=pipeline_template,
            readme=readme,
            current_version="1.0.0",
            versions=[
                ListingVersion(
                    version="1.0.0",
                    released_at=now,
                    changelog="Initial version",
                )
            ],
            pricing=pricing or ListingPricing(model=PricingModel.FREE),
            created_at=now,
            updated_at=now,
        )

        self._listings[listing_id] = listing
        self._slug_to_id[slug] = listing_id
        self._reviews[listing_id] = []

        # Update publisher stats
        publisher.total_listings += 1

        return listing

    def get_listing(self, listing_id: str) -> Optional[MarketplaceListing]:
        """Get a listing by ID."""
        return self._listings.get(listing_id)

    def get_listing_by_slug(self, slug: str) -> Optional[MarketplaceListing]:
        """Get a listing by slug."""
        listing_id = self._slug_to_id.get(slug)
        if listing_id:
            return self._listings.get(listing_id)
        return None

    def update_listing(
        self,
        listing_id: str,
        user_id: str,
        **updates,
    ) -> Optional[MarketplaceListing]:
        """Update a listing."""
        listing = self._listings.get(listing_id)
        if not listing or listing.publisher.id != user_id:
            return None

        for key, value in updates.items():
            if value is not None and hasattr(listing, key):
                setattr(listing, key, value)

        listing.updated_at = self._now()
        return listing

    def submit_for_review(self, listing_id: str, user_id: str) -> bool:
        """Submit a listing for review."""
        listing = self._listings.get(listing_id)
        if not listing or listing.publisher.id != user_id:
            return False

        if listing.status != ListingStatus.DRAFT:
            return False

        listing.status = ListingStatus.PENDING_REVIEW
        listing.updated_at = self._now()
        return True

    def publish_listing(self, listing_id: str) -> bool:
        """Publish a listing (admin action)."""
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        listing.status = ListingStatus.PUBLISHED
        listing.published_at = self._now()
        listing.updated_at = self._now()
        return True

    def archive_listing(self, listing_id: str, user_id: str) -> bool:
        """Archive a listing."""
        listing = self._listings.get(listing_id)
        if not listing or listing.publisher.id != user_id:
            return False

        listing.status = ListingStatus.ARCHIVED
        listing.updated_at = self._now()
        return True

    def publish_version(
        self,
        listing_id: str,
        user_id: str,
        version: str,
        changelog: str,
        pipeline_template: Dict[str, Any],
        min_flowmason_version: Optional[str] = None,
    ) -> Optional[ListingVersion]:
        """Publish a new version of a listing."""
        listing = self._listings.get(listing_id)
        if not listing or listing.publisher.id != user_id:
            return None

        new_version = ListingVersion(
            version=version,
            released_at=self._now(),
            changelog=changelog,
            min_flowmason_version=min_flowmason_version,
        )

        listing.versions.append(new_version)
        listing.current_version = version
        listing.pipeline_template = pipeline_template
        listing.updated_at = self._now()

        return new_version

    def record_view(self, listing_id: str) -> None:
        """Record a view of a listing."""
        listing = self._listings.get(listing_id)
        if listing:
            listing.stats.views += 1

    # =========================================================================
    # Search
    # =========================================================================

    def search_listings(
        self,
        request: SearchListingsRequest,
    ) -> SearchListingsResponse:
        """Search marketplace listings."""
        results = []

        for listing in self._listings.values():
            # Only published listings
            if listing.status != ListingStatus.PUBLISHED:
                continue

            # Category filter
            if request.category and listing.category != request.category:
                continue

            # Pricing filter
            if request.pricing and listing.pricing.model != request.pricing:
                continue

            # Rating filter
            if request.min_rating and listing.stats.average_rating < request.min_rating:
                continue

            # Verified filter
            if request.verified_only and not listing.publisher.verified:
                continue

            # Tag filter
            if request.tags:
                if not any(tag in listing.tags for tag in request.tags):
                    continue

            # Query filter
            if request.query:
                query_lower = request.query.lower()
                if not (
                    query_lower in listing.name.lower()
                    or query_lower in listing.description.lower()
                    or query_lower in listing.tagline.lower()
                    or any(query_lower in tag for tag in listing.tags)
                ):
                    continue

            results.append(listing)

        # Sort
        if request.sort_by == "downloads":
            results.sort(key=lambda x: x.stats.downloads, reverse=True)
        elif request.sort_by == "rating":
            results.sort(key=lambda x: x.stats.average_rating, reverse=True)
        elif request.sort_by == "newest":
            results.sort(key=lambda x: x.published_at or "", reverse=True)
        else:  # relevance - use a combination
            results.sort(
                key=lambda x: (x.stats.downloads * 0.4 + x.stats.average_rating * 100 * 0.6),
                reverse=True,
            )

        # Pagination
        total = len(results)
        total_pages = (total + request.per_page - 1) // request.per_page
        start = (request.page - 1) * request.per_page
        end = start + request.per_page
        results = results[start:end]

        return SearchListingsResponse(
            listings=results,
            total=total,
            page=request.page,
            per_page=request.per_page,
            total_pages=total_pages,
        )

    def get_featured_listings(self, limit: int = 10) -> List[MarketplaceListing]:
        """Get featured listings."""
        featured = [
            listing for listing in self._listings.values()
            if listing.featured and listing.status == ListingStatus.PUBLISHED
        ]
        featured.sort(key=lambda x: x.stats.downloads, reverse=True)
        return featured[:limit]

    def get_trending_listings(self, limit: int = 10) -> List[MarketplaceListing]:
        """Get trending listings based on recent activity."""
        published = [
            listing for listing in self._listings.values()
            if listing.status == ListingStatus.PUBLISHED
        ]
        # Sort by weekly downloads (or total if weekly not available)
        published.sort(
            key=lambda x: x.stats.weekly_downloads or x.stats.downloads,
            reverse=True,
        )
        return published[:limit]

    def get_new_listings(self, limit: int = 10) -> List[MarketplaceListing]:
        """Get newest listings."""
        published = [
            listing for listing in self._listings.values()
            if listing.status == ListingStatus.PUBLISHED
        ]
        published.sort(key=lambda x: x.published_at or "", reverse=True)
        return published[:limit]

    def get_listings_by_category(
        self,
        category: ListingCategory,
        limit: int = 20,
    ) -> List[MarketplaceListing]:
        """Get listings by category."""
        listings = [
            listing for listing in self._listings.values()
            if listing.category == category and listing.status == ListingStatus.PUBLISHED
        ]
        listings.sort(key=lambda x: x.stats.downloads, reverse=True)
        return listings[:limit]

    # =========================================================================
    # Reviews
    # =========================================================================

    def submit_review(
        self,
        listing_id: str,
        user_id: str,
        username: str,
        rating: int,
        title: str,
        content: str,
    ) -> Optional[ListingReview]:
        """Submit a review for a listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return None

        # Check if user already reviewed
        existing_reviews = self._reviews.get(listing_id, [])
        if any(r.user_id == user_id for r in existing_reviews):
            return None  # Already reviewed

        review = ListingReview(
            id=self._generate_id(),
            listing_id=listing_id,
            user_id=user_id,
            username=username,
            rating=rating,
            title=title,
            content=content,
            created_at=self._now(),
        )

        self._reviews[listing_id].append(review)

        # Update listing stats
        listing.stats.reviews += 1
        total_rating = sum(r.rating for r in self._reviews[listing_id])
        listing.stats.average_rating = total_rating / listing.stats.reviews

        return review

    def get_reviews(
        self,
        listing_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ListingReview]:
        """Get reviews for a listing."""
        reviews = self._reviews.get(listing_id, [])
        reviews.sort(key=lambda x: x.created_at, reverse=True)
        return reviews[offset:offset + limit]

    def mark_review_helpful(
        self,
        listing_id: str,
        review_id: str,
        user_id: str,
    ) -> bool:
        """Mark a review as helpful."""
        reviews = self._reviews.get(listing_id, [])
        review = next((r for r in reviews if r.id == review_id), None)
        if review:
            review.helpful_count += 1
            return True
        return False

    # =========================================================================
    # Installation
    # =========================================================================

    def install_listing(
        self,
        listing_id: str,
        user_id: str,
        version: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None,
    ) -> Optional[InstallationRecord]:
        """Install a listing for a user."""
        listing = self._listings.get(listing_id)
        if not listing or listing.status != ListingStatus.PUBLISHED:
            return None

        # Use current version if not specified
        install_version = version or listing.current_version

        record = InstallationRecord(
            id=self._generate_id(),
            listing_id=listing_id,
            user_id=user_id,
            version=install_version,
            installed_at=self._now(),
            customizations=customizations or {},
        )

        if user_id not in self._installations:
            self._installations[user_id] = []
        self._installations[user_id].append(record)

        # Update stats
        listing.stats.downloads += 1
        listing.stats.weekly_downloads += 1
        listing.stats.monthly_downloads += 1

        # Update version downloads
        for v in listing.versions:
            if v.version == install_version:
                v.downloads += 1
                break

        # Update publisher stats
        listing.publisher.total_downloads += 1

        return record

    def get_user_installations(
        self,
        user_id: str,
    ) -> List[InstallationRecord]:
        """Get all installations for a user."""
        return self._installations.get(user_id, [])

    # =========================================================================
    # User Library
    # =========================================================================

    def get_user_library(self, user_id: str) -> UserLibrary:
        """Get or create a user's library."""
        if user_id not in self._user_libraries:
            self._user_libraries[user_id] = UserLibrary(user_id=user_id)
        return self._user_libraries[user_id]

    def add_to_favorites(self, user_id: str, listing_id: str) -> bool:
        """Add a listing to favorites."""
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        library = self.get_user_library(user_id)
        if listing_id not in library.favorites:
            library.favorites.append(listing_id)
            listing.stats.favorites += 1
        return True

    def remove_from_favorites(self, user_id: str, listing_id: str) -> bool:
        """Remove a listing from favorites."""
        library = self.get_user_library(user_id)
        if listing_id in library.favorites:
            library.favorites.remove(listing_id)
            listing = self._listings.get(listing_id)
            if listing:
                listing.stats.favorites = max(0, listing.stats.favorites - 1)
            return True
        return False

    def add_to_recently_viewed(self, user_id: str, listing_id: str) -> None:
        """Add a listing to recently viewed."""
        library = self.get_user_library(user_id)
        if listing_id in library.recently_viewed:
            library.recently_viewed.remove(listing_id)
        library.recently_viewed.insert(0, listing_id)
        library.recently_viewed = library.recently_viewed[:50]  # Keep last 50

    # =========================================================================
    # Collections
    # =========================================================================

    def create_collection(
        self,
        user_id: str,
        name: str,
        description: str,
        listing_ids: Optional[List[str]] = None,
    ) -> Collection:
        """Create a curated collection."""
        collection_id = self._generate_id()
        slug = self._slugify(name)
        now = self._now()

        collection = Collection(
            id=collection_id,
            name=name,
            description=description,
            slug=slug,
            listings=listing_ids or [],
            curated_by=user_id,
            created_at=now,
            updated_at=now,
        )

        self._collections[collection_id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get a collection by ID."""
        return self._collections.get(collection_id)

    def get_collections(self, limit: int = 20) -> List[Collection]:
        """Get all collections."""
        collections = list(self._collections.values())
        collections.sort(key=lambda x: x.created_at, reverse=True)
        return collections[:limit]

    def add_to_collection(
        self,
        collection_id: str,
        listing_id: str,
        user_id: str,
    ) -> bool:
        """Add a listing to a collection."""
        collection = self._collections.get(collection_id)
        if not collection or collection.curated_by != user_id:
            return False

        if listing_id not in collection.listings:
            collection.listings.append(listing_id)
            collection.updated_at = self._now()
        return True

    # =========================================================================
    # Publishers
    # =========================================================================

    def get_publisher(self, publisher_id: str) -> Optional[Publisher]:
        """Get a publisher by ID."""
        return self._publishers.get(publisher_id)

    def get_publisher_listings(
        self,
        publisher_id: str,
        include_drafts: bool = False,
    ) -> List[MarketplaceListing]:
        """Get all listings by a publisher."""
        listings = [
            listing for listing in self._listings.values()
            if listing.publisher.id == publisher_id
        ]

        if not include_drafts:
            listings = [l for l in listings if l.status == ListingStatus.PUBLISHED]

        return listings

    # =========================================================================
    # Stats
    # =========================================================================

    def get_marketplace_stats(self) -> MarketplaceStats:
        """Get overall marketplace statistics."""
        published = [
            l for l in self._listings.values()
            if l.status == ListingStatus.PUBLISHED
        ]

        # Category counts
        categories = {}
        for listing in published:
            cat = listing.category.value
            categories[cat] = categories.get(cat, 0) + 1

        # Trending (top 10 by weekly downloads)
        trending = sorted(
            published,
            key=lambda x: x.stats.weekly_downloads,
            reverse=True,
        )[:10]

        # New this week
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        new_count = sum(
            1 for l in published
            if l.published_at and l.published_at > week_ago
        )

        return MarketplaceStats(
            total_listings=len(published),
            total_publishers=len(self._publishers),
            total_downloads=sum(l.stats.downloads for l in published),
            total_reviews=sum(len(self._reviews.get(l.id, [])) for l in published),
            categories=categories,
            trending=[l.id for l in trending],
            new_this_week=new_count,
        )


# Singleton instance
_service: Optional[MarketplaceService] = None


def get_marketplace_service() -> MarketplaceService:
    """Get the singleton MarketplaceService instance."""
    global _service
    if _service is None:
        _service = MarketplaceService()
    return _service
