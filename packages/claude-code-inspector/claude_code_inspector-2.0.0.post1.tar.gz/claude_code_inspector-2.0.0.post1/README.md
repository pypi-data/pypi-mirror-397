# ⚠️ DEPRECATED: Claude Code Inspector

> **This package has been renamed and is no longer maintained.**
>
> The `claude-code-inspector` package has been completely rebranded as **[LLM Interceptor (LLI)](https://pypi.org/project/llm-interceptor/)**.
>
> Please migrate to the new package for continued support and updates.

## 🚨 Important Migration Notice

**This package (`claude-code-inspector`) is deprecated as of version 2.0.0.**

### What Changed
- **New Package Name**: `llm-interceptor`
- **New CLI Command**: `lli` (instead of `cci`)
- **New Repository**: [https://github.com/chouzz/llm-interceptor](https://github.com/chouzz/llm-interceptor)

### Migration Steps

1. **Uninstall the old package:**
   ```bash
   pip uninstall claude-code-inspector
   ```

2. **Install the new package:**
   ```bash
   pip install llm-interceptor
   # or using uv (recommended)
   uv add llm-interceptor
   ```

3. **Update your commands:**
   ```bash
   # Old command
   cci watch

   # New command
   lli watch
   ```

4. **Update environment variables if needed:**
   ```bash
   # The proxy setup remains the same
   export HTTP_PROXY=http://127.0.0.1:9090
   export HTTPS_PROXY=http://127.0.0.1:9090
   export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem
   ```

### Why the Change?

The project has evolved beyond just Claude Code inspection to support a broader range of LLM traffic analysis across multiple AI coding tools and providers. The new name "LLM Interceptor" better reflects this expanded scope.

### Features in LLM Interceptor

- ✅ **Enhanced Watch Mode** - Better session management and real-time capture
- ✅ **Modern Web UI** - Beautiful React-based interface for trace analysis
- ✅ **Broader Provider Support** - Anthropic, OpenAI, Google, Groq, Together, Mistral, and more
- ✅ **Improved Performance** - Better streaming support and data processing
- ✅ **Active Maintenance** - Regular updates and bug fixes

### Need Help?

- 📖 **Documentation**: [https://github.com/chouzz/llm-interceptor](https://github.com/chouzz/llm-interceptor)
- 🐛 **Issues**: [Report bugs](https://github.com/chouzz/llm-interceptor/issues)
- 💬 **Discussions**: [Get help](https://github.com/chouzz/llm-interceptor/discussions)

---

**Please update to `llm-interceptor` as soon as possible. This deprecated package will not receive any future updates or security fixes.**
