"""
FlowMason Marketplace Service.

Public package marketplace with ratings, reviews, and discovery features.
Extends the private registry to enable public package sharing.
"""

import hashlib
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class PackageStatus(str, Enum):
    """Package publication status."""
    DRAFT = "draft"              # Not yet published
    PENDING = "pending"          # Awaiting review
    PUBLISHED = "published"      # Live in marketplace
    SUSPENDED = "suspended"      # Temporarily removed
    DEPRECATED = "deprecated"    # No longer maintained


class TrustBadge(str, Enum):
    """Trust badges for verified packages."""
    VERIFIED = "verified"        # Code reviewed and verified
    OFFICIAL = "official"        # Official FlowMason package
    POPULAR = "popular"          # High download count
    TRENDING = "trending"        # Rapidly growing downloads
    FEATURED = "featured"        # Editor's choice


@dataclass
class Publisher:
    """Package publisher profile."""
    id: str
    name: str
    display_name: str
    email: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime] = None
    package_count: int = 0
    total_downloads: int = 0


@dataclass
class Review:
    """Package review."""
    id: str
    package_name: str
    package_version: str
    user_id: str
    user_name: str
    rating: int  # 1-5 stars
    title: Optional[str] = None
    body: Optional[str] = None
    helpful_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MarketplacePackage:
    """Package listing in the marketplace."""
    # Core info
    name: str
    version: str
    description: str
    long_description: Optional[str] = None

    # Publisher
    publisher_id: str = ""
    publisher_name: str = ""

    # Categorization
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Components
    components: List[str] = field(default_factory=list)
    component_count: int = 0

    # Status
    status: PackageStatus = PackageStatus.PUBLISHED
    badges: List[TrustBadge] = field(default_factory=list)

    # Statistics
    downloads: int = 0
    downloads_this_week: int = 0
    downloads_this_month: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    review_count: int = 0

    # Timestamps
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Metadata
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation_url: Optional[str] = None
    changelog_url: Optional[str] = None

    # Media
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)

    # Versions
    available_versions: List[str] = field(default_factory=list)
    latest_version: str = ""

    # Requirements
    min_flowmason_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class MarketplaceStats:
    """Overall marketplace statistics."""
    total_packages: int = 0
    total_downloads: int = 0
    total_publishers: int = 0
    total_reviews: int = 0
    packages_this_week: int = 0
    downloads_this_week: int = 0


class MarketplaceService:
    """
    Marketplace service for public package discovery and distribution.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self._storage_path = storage_path or Path.home() / ".flowmason" / "marketplace"
        self._packages_dir = self._storage_path / "packages"
        self._publishers_dir = self._storage_path / "publishers"
        self._reviews_dir = self._storage_path / "reviews"
        self._stats_dir = self._storage_path / "stats"

        # Ensure directories exist
        for d in [self._packages_dir, self._publishers_dir, self._reviews_dir, self._stats_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Package Operations
    # =========================================================================

    def publish_package(
        self,
        name: str,
        version: str,
        package_path: Path,
        publisher_id: str,
        metadata: Dict[str, Any],
    ) -> MarketplacePackage:
        """
        Publish a package to the marketplace.
        """
        # Load or create package listing
        listing = self._load_package(name) or MarketplacePackage(
            name=name,
            version=version,
            description=metadata.get("description", ""),
            publisher_id=publisher_id,
        )

        # Update with new version info
        listing.version = version
        listing.description = metadata.get("description", listing.description)
        listing.long_description = metadata.get("long_description", listing.long_description)
        listing.category = metadata.get("category", listing.category)
        listing.subcategory = metadata.get("subcategory", listing.subcategory)
        listing.tags = metadata.get("tags", listing.tags)
        listing.components = metadata.get("components", listing.components)
        listing.component_count = len(listing.components)
        listing.license = metadata.get("license", listing.license)
        listing.homepage = metadata.get("homepage", listing.homepage)
        listing.repository = metadata.get("repository", listing.repository)
        listing.documentation_url = metadata.get("documentation_url", listing.documentation_url)
        listing.icon_url = metadata.get("icon_url", listing.icon_url)
        listing.screenshots = metadata.get("screenshots", listing.screenshots)
        listing.min_flowmason_version = metadata.get("min_flowmason_version")
        listing.dependencies = metadata.get("dependencies", [])

        # Update version tracking
        if version not in listing.available_versions:
            listing.available_versions.append(version)
            listing.available_versions.sort(reverse=True)
        listing.latest_version = listing.available_versions[0]

        # Set timestamps
        now = datetime.utcnow()
        if not listing.published_at:
            listing.published_at = now
        listing.updated_at = now

        # Set status
        listing.status = PackageStatus.PUBLISHED

        # Get publisher info
        publisher = self.get_publisher(publisher_id)
        if publisher:
            listing.publisher_name = publisher.display_name

        # Save
        self._save_package(listing)

        # Copy package file to marketplace storage
        dest_dir = self._packages_dir / name
        dest_dir.mkdir(exist_ok=True)
        dest_path = dest_dir / f"{name}-{version}.fmpkg"
        if package_path.exists():
            import shutil
            shutil.copy2(package_path, dest_path)

        # Update publisher stats
        self._update_publisher_stats(publisher_id)

        return listing

    def get_package(self, name: str) -> Optional[MarketplacePackage]:
        """Get a package listing."""
        return self._load_package(name)

    def search_packages(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publisher_id: Optional[str] = None,
        sort_by: str = "downloads",  # downloads, rating, recent, name
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[MarketplacePackage], int]:
        """
        Search marketplace packages.

        Returns (packages, total_count).
        """
        packages = self._list_all_packages()

        # Filter by query
        if query:
            query_lower = query.lower()
            packages = [
                p for p in packages
                if query_lower in p.name.lower()
                or query_lower in p.description.lower()
                or any(query_lower in t.lower() for t in p.tags)
            ]

        # Filter by category
        if category:
            packages = [p for p in packages if p.category == category]

        # Filter by tags
        if tags:
            packages = [
                p for p in packages
                if any(t in p.tags for t in tags)
            ]

        # Filter by publisher
        if publisher_id:
            packages = [p for p in packages if p.publisher_id == publisher_id]

        # Filter to only published packages
        packages = [p for p in packages if p.status == PackageStatus.PUBLISHED]

        # Sort
        if sort_by == "downloads":
            packages.sort(key=lambda p: p.downloads, reverse=True)
        elif sort_by == "rating":
            packages.sort(key=lambda p: p.rating_average, reverse=True)
        elif sort_by == "recent":
            packages.sort(key=lambda p: p.updated_at or datetime.min, reverse=True)
        elif sort_by == "name":
            packages.sort(key=lambda p: p.name.lower())

        # Paginate
        total = len(packages)
        start = (page - 1) * page_size
        end = start + page_size
        packages = packages[start:end]

        return packages, total

    def get_featured_packages(self, limit: int = 6) -> List[MarketplacePackage]:
        """Get featured packages."""
        packages = self._list_all_packages()
        featured = [p for p in packages if TrustBadge.FEATURED in p.badges]
        return featured[:limit]

    def get_trending_packages(self, limit: int = 10) -> List[MarketplacePackage]:
        """Get trending packages (highest downloads this week)."""
        packages = self._list_all_packages()
        packages.sort(key=lambda p: p.downloads_this_week, reverse=True)
        return packages[:limit]

    def get_popular_packages(self, limit: int = 10) -> List[MarketplacePackage]:
        """Get most popular packages (highest total downloads)."""
        packages = self._list_all_packages()
        packages.sort(key=lambda p: p.downloads, reverse=True)
        return packages[:limit]

    def get_recent_packages(self, limit: int = 10) -> List[MarketplacePackage]:
        """Get recently published packages."""
        packages = self._list_all_packages()
        packages.sort(key=lambda p: p.published_at or datetime.min, reverse=True)
        return packages[:limit]

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with package counts."""
        packages = self._list_all_packages()
        categories: Dict[str, int] = {}

        for pkg in packages:
            if pkg.category:
                categories[pkg.category] = categories.get(pkg.category, 0) + 1

        return [
            {"name": name, "count": count}
            for name, count in sorted(categories.items())
        ]

    def download_package(
        self,
        name: str,
        version: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Get path to package file and record download.
        """
        listing = self._load_package(name)
        if not listing:
            return None

        version = version or listing.latest_version
        pkg_path = self._packages_dir / name / f"{name}-{version}.fmpkg"

        if not pkg_path.exists():
            return None

        # Record download
        self._record_download(name, version, user_id)

        return pkg_path

    def deprecate_package(self, name: str, reason: Optional[str] = None) -> bool:
        """Mark a package as deprecated."""
        listing = self._load_package(name)
        if not listing:
            return False

        listing.status = PackageStatus.DEPRECATED
        self._save_package(listing)
        return True

    # =========================================================================
    # Reviews
    # =========================================================================

    def add_review(
        self,
        package_name: str,
        user_id: str,
        user_name: str,
        rating: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> Review:
        """Add a review for a package."""
        listing = self._load_package(package_name)
        if not listing:
            raise ValueError(f"Package '{package_name}' not found")

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Check if user already reviewed this package
        existing = self._get_user_review(package_name, user_id)
        if existing:
            # Update existing review
            existing.rating = rating
            existing.title = title
            existing.body = body
            existing.updated_at = datetime.utcnow()
            self._save_review(existing)
            self._update_package_ratings(package_name)
            return existing

        # Create new review
        review = Review(
            id=str(uuid4()),
            package_name=package_name,
            package_version=listing.latest_version,
            user_id=user_id,
            user_name=user_name,
            rating=rating,
            title=title,
            body=body,
            created_at=datetime.utcnow(),
        )

        self._save_review(review)
        self._update_package_ratings(package_name)

        return review

    def get_reviews(
        self,
        package_name: str,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Review], int]:
        """Get reviews for a package."""
        reviews = self._load_reviews(package_name)
        reviews.sort(key=lambda r: r.created_at or datetime.min, reverse=True)

        total = len(reviews)
        start = (page - 1) * page_size
        end = start + page_size

        return reviews[start:end], total

    def mark_review_helpful(self, review_id: str, user_id: str) -> bool:
        """Mark a review as helpful."""
        # Find review
        for pkg_dir in self._reviews_dir.iterdir():
            for review_file in pkg_dir.glob("*.json"):
                review = self._load_review_file(review_file)
                if review and review.id == review_id:
                    review.helpful_count += 1
                    self._save_review(review)
                    return True
        return False

    def delete_review(self, review_id: str, user_id: str) -> bool:
        """Delete a review (only by author)."""
        for pkg_dir in self._reviews_dir.iterdir():
            for review_file in pkg_dir.glob("*.json"):
                review = self._load_review_file(review_file)
                if review and review.id == review_id:
                    if review.user_id != user_id:
                        raise PermissionError("Can only delete your own reviews")
                    review_file.unlink()
                    self._update_package_ratings(review.package_name)
                    return True
        return False

    # =========================================================================
    # Publishers
    # =========================================================================

    def create_publisher(
        self,
        user_id: str,
        name: str,
        display_name: str,
        email: Optional[str] = None,
        website: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> Publisher:
        """Create a publisher profile."""
        # Check if name is taken
        existing = self._load_publisher_by_name(name)
        if existing:
            raise ValueError(f"Publisher name '{name}' is already taken")

        publisher = Publisher(
            id=user_id,
            name=name,
            display_name=display_name,
            email=email,
            website=website,
            bio=bio,
            created_at=datetime.utcnow(),
        )

        self._save_publisher(publisher)
        return publisher

    def get_publisher(self, publisher_id: str) -> Optional[Publisher]:
        """Get a publisher by ID."""
        return self._load_publisher(publisher_id)

    def get_publisher_by_name(self, name: str) -> Optional[Publisher]:
        """Get a publisher by name."""
        return self._load_publisher_by_name(name)

    def update_publisher(
        self,
        publisher_id: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
        website: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[Publisher]:
        """Update publisher profile."""
        publisher = self._load_publisher(publisher_id)
        if not publisher:
            return None

        if display_name:
            publisher.display_name = display_name
        if email is not None:
            publisher.email = email
        if website is not None:
            publisher.website = website
        if bio is not None:
            publisher.bio = bio
        if avatar_url is not None:
            publisher.avatar_url = avatar_url

        self._save_publisher(publisher)
        return publisher

    def get_publisher_packages(
        self,
        publisher_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[MarketplacePackage], int]:
        """Get packages by a publisher."""
        return self.search_packages(publisher_id=publisher_id, page=page, page_size=page_size)

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> MarketplaceStats:
        """Get overall marketplace statistics."""
        packages = self._list_all_packages()
        publishers = list(self._publishers_dir.glob("*.json"))

        total_downloads = sum(p.downloads for p in packages)
        total_reviews = sum(p.review_count for p in packages)
        downloads_this_week = sum(p.downloads_this_week for p in packages)

        # Count packages published this week
        one_week_ago = datetime.utcnow().timestamp() - (7 * 24 * 60 * 60)
        packages_this_week = sum(
            1 for p in packages
            if p.published_at and p.published_at.timestamp() > one_week_ago
        )

        return MarketplaceStats(
            total_packages=len(packages),
            total_downloads=total_downloads,
            total_publishers=len(publishers),
            total_reviews=total_reviews,
            packages_this_week=packages_this_week,
            downloads_this_week=downloads_this_week,
        )

    # =========================================================================
    # Badge Management
    # =========================================================================

    def add_badge(self, package_name: str, badge: TrustBadge) -> bool:
        """Add a trust badge to a package."""
        listing = self._load_package(package_name)
        if not listing:
            return False

        if badge not in listing.badges:
            listing.badges.append(badge)
            self._save_package(listing)

        return True

    def remove_badge(self, package_name: str, badge: TrustBadge) -> bool:
        """Remove a trust badge from a package."""
        listing = self._load_package(package_name)
        if not listing:
            return False

        if badge in listing.badges:
            listing.badges.remove(badge)
            self._save_package(listing)

        return True

    def update_automatic_badges(self) -> None:
        """Update automatic badges based on metrics."""
        packages = self._list_all_packages()

        # Popular badge: top 10% by downloads
        by_downloads = sorted(packages, key=lambda p: p.downloads, reverse=True)
        popular_threshold = len(packages) // 10 or 1
        popular_names = {p.name for p in by_downloads[:popular_threshold]}

        # Trending badge: top 10% by weekly downloads
        by_trending = sorted(packages, key=lambda p: p.downloads_this_week, reverse=True)
        trending_threshold = len(packages) // 10 or 1
        trending_names = {p.name for p in by_trending[:trending_threshold]}

        for pkg in packages:
            # Update popular badge
            if pkg.name in popular_names:
                if TrustBadge.POPULAR not in pkg.badges:
                    pkg.badges.append(TrustBadge.POPULAR)
            else:
                if TrustBadge.POPULAR in pkg.badges:
                    pkg.badges.remove(TrustBadge.POPULAR)

            # Update trending badge
            if pkg.name in trending_names and pkg.downloads_this_week > 0:
                if TrustBadge.TRENDING not in pkg.badges:
                    pkg.badges.append(TrustBadge.TRENDING)
            else:
                if TrustBadge.TRENDING in pkg.badges:
                    pkg.badges.remove(TrustBadge.TRENDING)

            self._save_package(pkg)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _load_package(self, name: str) -> Optional[MarketplacePackage]:
        """Load package listing from storage."""
        meta_path = self._packages_dir / name / "metadata.json"
        if not meta_path.exists():
            return None

        try:
            with open(meta_path) as f:
                data = json.load(f)
            return self._dict_to_package(data)
        except Exception:
            return None

    def _save_package(self, pkg: MarketplacePackage) -> None:
        """Save package listing to storage."""
        pkg_dir = self._packages_dir / pkg.name
        pkg_dir.mkdir(exist_ok=True)
        meta_path = pkg_dir / "metadata.json"

        with open(meta_path, "w") as f:
            json.dump(self._package_to_dict(pkg), f, indent=2, default=str)

    def _list_all_packages(self) -> List[MarketplacePackage]:
        """List all packages in storage."""
        packages = []
        for pkg_dir in self._packages_dir.iterdir():
            if pkg_dir.is_dir():
                pkg = self._load_package(pkg_dir.name)
                if pkg:
                    packages.append(pkg)
        return packages

    def _record_download(
        self,
        name: str,
        version: str,
        user_id: Optional[str],
    ) -> None:
        """Record a package download."""
        listing = self._load_package(name)
        if listing:
            listing.downloads += 1
            listing.downloads_this_week += 1
            listing.downloads_this_month += 1
            self._save_package(listing)

    def _load_reviews(self, package_name: str) -> List[Review]:
        """Load all reviews for a package."""
        reviews_dir = self._reviews_dir / package_name
        if not reviews_dir.exists():
            return []

        reviews = []
        for review_file in reviews_dir.glob("*.json"):
            review = self._load_review_file(review_file)
            if review:
                reviews.append(review)

        return reviews

    def _load_review_file(self, path: Path) -> Optional[Review]:
        """Load a single review from file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return self._dict_to_review(data)
        except Exception:
            return None

    def _save_review(self, review: Review) -> None:
        """Save a review to storage."""
        reviews_dir = self._reviews_dir / review.package_name
        reviews_dir.mkdir(exist_ok=True)
        review_path = reviews_dir / f"{review.id}.json"

        with open(review_path, "w") as f:
            json.dump(self._review_to_dict(review), f, indent=2, default=str)

    def _get_user_review(self, package_name: str, user_id: str) -> Optional[Review]:
        """Get a user's review for a package."""
        reviews = self._load_reviews(package_name)
        for r in reviews:
            if r.user_id == user_id:
                return r
        return None

    def _update_package_ratings(self, package_name: str) -> None:
        """Update package rating statistics."""
        listing = self._load_package(package_name)
        if not listing:
            return

        reviews = self._load_reviews(package_name)
        if reviews:
            ratings = [r.rating for r in reviews]
            listing.rating_average = round(statistics.mean(ratings), 1)
            listing.rating_count = len(ratings)
            listing.review_count = len([r for r in reviews if r.body])
        else:
            listing.rating_average = 0.0
            listing.rating_count = 0
            listing.review_count = 0

        self._save_package(listing)

    def _load_publisher(self, publisher_id: str) -> Optional[Publisher]:
        """Load publisher by ID."""
        pub_path = self._publishers_dir / f"{publisher_id}.json"
        if not pub_path.exists():
            return None

        try:
            with open(pub_path) as f:
                data = json.load(f)
            return self._dict_to_publisher(data)
        except Exception:
            return None

    def _load_publisher_by_name(self, name: str) -> Optional[Publisher]:
        """Load publisher by name."""
        for pub_file in self._publishers_dir.glob("*.json"):
            publisher = self._load_publisher(pub_file.stem)
            if publisher and publisher.name == name:
                return publisher
        return None

    def _save_publisher(self, publisher: Publisher) -> None:
        """Save publisher to storage."""
        pub_path = self._publishers_dir / f"{publisher.id}.json"
        with open(pub_path, "w") as f:
            json.dump(self._publisher_to_dict(publisher), f, indent=2, default=str)

    def _update_publisher_stats(self, publisher_id: str) -> None:
        """Update publisher statistics."""
        publisher = self._load_publisher(publisher_id)
        if not publisher:
            return

        packages, _ = self.search_packages(publisher_id=publisher_id, page_size=1000)
        publisher.package_count = len(packages)
        publisher.total_downloads = sum(p.downloads for p in packages)
        self._save_publisher(publisher)

    # Serialization helpers
    def _package_to_dict(self, pkg: MarketplacePackage) -> Dict[str, Any]:
        return {
            "name": pkg.name,
            "version": pkg.version,
            "description": pkg.description,
            "long_description": pkg.long_description,
            "publisher_id": pkg.publisher_id,
            "publisher_name": pkg.publisher_name,
            "category": pkg.category,
            "subcategory": pkg.subcategory,
            "tags": pkg.tags,
            "components": pkg.components,
            "component_count": pkg.component_count,
            "status": pkg.status.value,
            "badges": [b.value for b in pkg.badges],
            "downloads": pkg.downloads,
            "downloads_this_week": pkg.downloads_this_week,
            "downloads_this_month": pkg.downloads_this_month,
            "rating_average": pkg.rating_average,
            "rating_count": pkg.rating_count,
            "review_count": pkg.review_count,
            "published_at": pkg.published_at.isoformat() if pkg.published_at else None,
            "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
            "license": pkg.license,
            "homepage": pkg.homepage,
            "repository": pkg.repository,
            "documentation_url": pkg.documentation_url,
            "changelog_url": pkg.changelog_url,
            "icon_url": pkg.icon_url,
            "banner_url": pkg.banner_url,
            "screenshots": pkg.screenshots,
            "available_versions": pkg.available_versions,
            "latest_version": pkg.latest_version,
            "min_flowmason_version": pkg.min_flowmason_version,
            "dependencies": pkg.dependencies,
        }

    def _dict_to_package(self, data: Dict[str, Any]) -> MarketplacePackage:
        published_at = data.get("published_at")
        if published_at and isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return MarketplacePackage(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            long_description=data.get("long_description"),
            publisher_id=data.get("publisher_id", ""),
            publisher_name=data.get("publisher_name", ""),
            category=data.get("category"),
            subcategory=data.get("subcategory"),
            tags=data.get("tags", []),
            components=data.get("components", []),
            component_count=data.get("component_count", 0),
            status=PackageStatus(data.get("status", "published")),
            badges=[TrustBadge(b) for b in data.get("badges", [])],
            downloads=data.get("downloads", 0),
            downloads_this_week=data.get("downloads_this_week", 0),
            downloads_this_month=data.get("downloads_this_month", 0),
            rating_average=data.get("rating_average", 0.0),
            rating_count=data.get("rating_count", 0),
            review_count=data.get("review_count", 0),
            published_at=published_at,
            updated_at=updated_at,
            license=data.get("license"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            documentation_url=data.get("documentation_url"),
            changelog_url=data.get("changelog_url"),
            icon_url=data.get("icon_url"),
            banner_url=data.get("banner_url"),
            screenshots=data.get("screenshots", []),
            available_versions=data.get("available_versions", []),
            latest_version=data.get("latest_version", ""),
            min_flowmason_version=data.get("min_flowmason_version"),
            dependencies=data.get("dependencies", []),
        )

    def _review_to_dict(self, review: Review) -> Dict[str, Any]:
        return {
            "id": review.id,
            "package_name": review.package_name,
            "package_version": review.package_version,
            "user_id": review.user_id,
            "user_name": review.user_name,
            "rating": review.rating,
            "title": review.title,
            "body": review.body,
            "helpful_count": review.helpful_count,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": review.updated_at.isoformat() if review.updated_at else None,
        }

    def _dict_to_review(self, data: Dict[str, Any]) -> Review:
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return Review(
            id=data["id"],
            package_name=data["package_name"],
            package_version=data.get("package_version", ""),
            user_id=data["user_id"],
            user_name=data.get("user_name", ""),
            rating=data["rating"],
            title=data.get("title"),
            body=data.get("body"),
            helpful_count=data.get("helpful_count", 0),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _publisher_to_dict(self, pub: Publisher) -> Dict[str, Any]:
        return {
            "id": pub.id,
            "name": pub.name,
            "display_name": pub.display_name,
            "email": pub.email,
            "website": pub.website,
            "avatar_url": pub.avatar_url,
            "bio": pub.bio,
            "verified": pub.verified,
            "created_at": pub.created_at.isoformat() if pub.created_at else None,
            "package_count": pub.package_count,
            "total_downloads": pub.total_downloads,
        }

    def _dict_to_publisher(self, data: Dict[str, Any]) -> Publisher:
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return Publisher(
            id=data["id"],
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            email=data.get("email"),
            website=data.get("website"),
            avatar_url=data.get("avatar_url"),
            bio=data.get("bio"),
            verified=data.get("verified", False),
            created_at=created_at,
            package_count=data.get("package_count", 0),
            total_downloads=data.get("total_downloads", 0),
        )


# Singleton instance
_marketplace: Optional[MarketplaceService] = None


def get_marketplace_service() -> MarketplaceService:
    """Get the marketplace service singleton."""
    global _marketplace
    if _marketplace is None:
        _marketplace = MarketplaceService()
    return _marketplace
