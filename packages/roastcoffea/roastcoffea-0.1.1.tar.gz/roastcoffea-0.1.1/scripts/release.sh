#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 0.1.1

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.1"
    exit 1
fi

echo "=== Releasing roastcoffea $VERSION ==="

# 1. Update version in __init__.py
echo "Updating version to $VERSION..."
sed -i '' "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/roastcoffea/__init__.py

# 2. Run tests
echo "Running tests..."
pixi run -e dev pytest -v -m "not slow"

# 3. Run pre-commit
echo "Running pre-commit checks..."
pre-commit run --all-files || true

# 4. Commit version bump
echo "Committing version bump..."
git add src/roastcoffea/__init__.py
git commit -m "chore: bump version to $VERSION"

# 5. Create tag
echo "Creating tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION"

# 6. Push to GitHub
echo "Pushing to GitHub..."
git push origin main
git push origin "$VERSION"

# 7. Build distribution
echo "Building distribution..."
rm -rf dist/
pixi run -e dev python -m build

# 8. Verify build
echo "Verifying build..."
pixi run -e dev twine check dist/*

# 9. Create GitHub release
echo "Creating GitHub release..."
gh release create "$VERSION" \
    --title "v$VERSION" \
    --generate-notes

# 10. Publish to PyPI
echo "Publishing to PyPI..."
pixi run -e dev twine upload dist/*

echo "=== Release $VERSION complete! ==="
