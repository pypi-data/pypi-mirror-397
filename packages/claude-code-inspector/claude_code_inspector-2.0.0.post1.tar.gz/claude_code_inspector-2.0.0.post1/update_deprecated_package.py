#!/usr/bin/env python3
"""
Script to update the deprecated claude-code-inspector package on PyPI
with a deprecation warning README.
"""

import shutil
import subprocess
from pathlib import Path

def update_deprecated_package():
    """Update the deprecated claude-code-inspector package."""

    print("🔄 Updating deprecated claude-code-inspector package...")

    # Create backup of current files
    print("📁 Creating backups...")
    shutil.copy("pyproject.toml", "pyproject.toml.backup")
    shutil.copy("README.md", "README.md.backup")

    try:
        # Update pyproject.toml to use old package name
        print("📝 Updating pyproject.toml...")
        with open("pyproject.toml", "r") as f:
            content = f.read()

        # Change package name back to claude-code-inspector
        content = content.replace('name = "llm-interceptor"', 'name = "claude-code-inspector"')

        # Update version to indicate deprecation (keep same version but add .post1)
        content = content.replace('version = "2.0.0"', 'version = "2.0.0.post1"')

        # Update description to indicate deprecation
        content = content.replace(
            'description = "Intercept and analyze LLM traffic from AI coding tools"',
            'description = "DEPRECATED: Use llm-interceptor instead. Intercept and analyze LLM traffic from AI coding tools"'
        )

        with open("pyproject.toml", "w") as f:
            f.write(content)

        # Replace README with deprecated version
        print("📖 Updating README.md...")
        shutil.copy("deprecated-README.md", "README.md")

        # Build and publish
        print("🔨 Building package...")
        subprocess.run(["uv", "build"], check=True)

        print("📤 Publishing to PyPI...")
        print("⚠️  Please run the following command manually:")
        print("   uv publish")
        print("\nOr if using twine:")
        print("   twine upload dist/*")

        print("\n✅ Package updated for deprecation warning!")
        print("   - Package name: claude-code-inspector")
        print("   - Version: 2.0.0.post1")
        print("   - README: Contains migration instructions")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Restoring backups...")
        restore_backups()
        return False

    return True

def restore_backups():
    """Restore backup files."""
    try:
        if Path("pyproject.toml.backup").exists():
            shutil.move("pyproject.toml.backup", "pyproject.toml")
        if Path("README.md.backup").exists():
            shutil.move("README.md.backup", "README.md")
        print("✅ Backups restored.")
    except Exception as e:
        print(f"❌ Error restoring backups: {e}")

if __name__ == "__main__":
    print("🚨 DEPRECATED PACKAGE UPDATE SCRIPT")
    print("=" * 50)
    print("This script will update the claude-code-inspector package on PyPI")
    print("with a deprecation warning pointing users to llm-interceptor.")
    print()

    response = input("Do you want to continue? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        exit(0)

    if update_deprecated_package():
        print("\n" + "=" * 50)
        print("🎉 SUCCESS!")
        print("The deprecated package has been prepared.")
        print("Run 'uv publish' to upload to PyPI.")
        print("\nAfter publishing, you can restore the original files by running:")
        print("python update_deprecated_package.py --restore")
    else:
        print("\n❌ Update failed. Check the error messages above.")
