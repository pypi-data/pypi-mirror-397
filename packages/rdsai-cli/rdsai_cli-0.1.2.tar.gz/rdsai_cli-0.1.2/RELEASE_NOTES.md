# RDSAI CLI v0.1.0 - First Release 🎉

RDSAI CLI is a next-generation, AI-powered RDS CLI that transforms how you interact with the database. You describe your intent in natural language or SQL, and the AI agent performs hybrid processing of both: orchestrating diagnostic tools, analyzing execution plans, and executing queries — all without leaving your terminal.

## ✨ Key Features

### 🤖 AI Assistant
- **Natural Language Interaction** - Support for English and Chinese. Describe your needs in natural language to get optimized SQL and diagnostic results
- **Smart SQL Handling** - Auto-detects SQL vs natural language, supports SQL completer and query history
- **Instant SQL Result Explanation** - Press `Ctrl+E` after any SQL query to get AI-powered explanations of results or errors, helping you understand query outcomes and troubleshoot issues quickly
- **Multi-Model LLM Support** - Works with multiple providers (Qwen, OpenAI, DeepSeek, Anthropic, Gemini, OpenAI-compatible) and switch via `/model` command

### 🔍 Database Analysis
- **Schema Analysis** (`/research`) - Generate comprehensive database analysis reports with AI-powered schema review, index optimization suggestions, compliance checking against Alibaba Database Development Standards, and actionable recommendations
- **Performance Benchmarking** (`/benchmark`) - AI-powered sysbench performance testing with automated workflow (prepare → run → cleanup) and comprehensive analysis reports

### 🔌 Extensibility
- **MCP Integration** - Extend capabilities by connecting to external MCP servers, including Alibaba Cloud RDS OpenAPI for cloud RDS instance management, monitoring, and operations

### 🛡️ Security Features
- **Read-Only by Default** - DDL/DML operations require confirmation (unless YOLO mode is enabled)
- **SSL/TLS Support** - Full SSL configuration support (CA, client cert, key, mode)

## 📦 Installation

```bash
# Using uv (recommended)
uv tool install --python 3.13 rdsai-cli

# Or using pip
pip install rdsai-cli
```

## 🚀 Quick Start

```bash
# Start CLI (interactive mode)
rdsai

# Or connect directly
rdsai --host localhost -u root -p secret -D mydb

# Configure LLM
mysql> /setup
```

## 📖 Usage Examples

```text
mysql> analyze index usage on users table
mysql> show me slow queries from the last hour
mysql> check for lock waits
mysql> SELECT COUNT(*) FROM users;  # Press Ctrl+E to explain result
mysql> /research  # Generate database analysis report
mysql> /benchmark run  # Run performance benchmark
```

## 📋 Requirements

- Python 3.13+
- Network access to MySQL database
- API access to at least one LLM provider
- sysbench (optional, for `/benchmark` command)

## 🔗 Links

- [Full Documentation](https://github.com/aliyun/rdsai-cli/blob/main/README.md)
- [Issue Tracker](https://github.com/aliyun/rdsai-cli/issues)
- [Contributing Guide](https://github.com/aliyun/rdsai-cli/blob/main/CONTRIBUTING.md)

---

Thank you for using RDSAI CLI! For questions or suggestions, please submit an Issue or PR.

