# GraphRecon 🔎

**GraphRecon** is a fast, asynchronous GraphQL endpoint discovery tool.  
It scans common and misconfigured API paths to identify exposed GraphQL endpoints.

Designed for:
- Bug bounty hunters
- Pentesters
- Security researchers

---

## ✨ Features

- 🚀 Fully asynchronous (aiohttp + asyncio)
- 🔍 Detects GraphQL via real GraphQL queries
- 📍 Scans dozens of common GraphQL/API paths
- 🧠 Stops duplicate results
- 🌐 Detects if target is reachable
- 🎯 Clean CLI usage

---

## 📦 Installation

### Homebrew (macOS & Linux)

```bash
brew tap memirhan/graphrecon
brew install graphrecon