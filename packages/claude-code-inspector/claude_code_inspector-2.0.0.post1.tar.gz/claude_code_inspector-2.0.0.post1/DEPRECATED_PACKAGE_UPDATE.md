# Updating Deprecated claude-code-inspector Package

This guide explains how to update the deprecated `claude-code-inspector` package on PyPI with a deprecation warning that directs users to the new `llm-interceptor` package.

## 📋 Overview

After rebranding to LLM Interceptor, you need to update the old package to inform users about the migration.

## 🚀 Quick Steps

1. **Run the update script:**
   ```bash
   python update_deprecated_package.py
   ```

2. **Publish to PyPI:**
   ```bash
   uv publish
   ```

3. **Verify the update** by checking the package page on PyPI.

## 📁 Files Created

- `deprecated-README.md` - Deprecation warning README for the old package
- `update_deprecated_package.py` - Script to automate the package update process
- `DEPRECATED_PACKAGE_UPDATE.md` - This documentation

## 🔧 What the Script Does

The update script will:

1. **Backup current files** (`pyproject.toml` and `README.md`)
2. **Update `pyproject.toml`:**
   - Change package name back to `claude-code-inspector`
   - Update version to `2.0.0.post1`
   - Add deprecation notice to description
3. **Replace README.md** with deprecation warning
4. **Build the package** for publishing

## 🛡️ Safety Features

- **Automatic backups** of original files
- **Easy restoration** if something goes wrong
- **Manual confirmation** before making changes

## 🔄 Restoration

If you need to restore the original files:

```bash
# The script creates backups automatically
mv pyproject.toml.backup pyproject.toml
mv README.md.backup README.md
```

## 📦 Publishing

After running the script, publish using your preferred method:

```bash
# Using uv (recommended)
uv publish

# Or using twine
twine upload dist/*
```

## ✅ Verification

After publishing, verify that:

1. The package page shows the deprecation warning
2. Users are directed to `llm-interceptor`
3. Migration instructions are clear
4. Links work correctly

## 🆘 Troubleshooting

**Package already exists?**
- Use version `2.0.0.post1` or increment as needed
- PyPI allows multiple versions

**Permission issues?**
- Make sure you have PyPI credentials configured
- Check that you're the owner of the `claude-code-inspector` package

**Build fails?**
- Ensure all dependencies are installed
- Check the `uv build` output for specific errors
