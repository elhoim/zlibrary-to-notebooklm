# 📚 Z-Library to NotebookLM

[English](README.md) | [简体中文](README.zh-CN.md)

> Automatically download books from Z-Library and upload them to Google NotebookLM with one command.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-success.svg)](https://claude.ai/claude-code)

---

## ⚠️ Important Disclaimer

**This project is for educational, research, and technical demonstration purposes only. Please strictly comply with local laws and copyright regulations. Use only for:**

- ✅ Resources you have legal access to
- ✅ Public domain or open-source licensed documents (e.g., arXiv, Project Gutenberg)
- ✅ Content you personally own or have authorization to use

**The author does not encourage or support any form of copyright infringement and assumes no legal liability. Use at your own risk.**

**Please respect intellectual property rights and support authorized reading!**

---

## ✨ Features

- 🔐 **One-time Login, Forever Use** - Similar to `notebooklm login` experience
- 📥 **Smart Download** - Prioritizes PDF (preserves formatting), auto-fallback to EPUB → Markdown
- 📦 **Smart Chunking** - Large files auto-split (>350k words) for reliable CLI upload
- 🤖 **Fully Automated** - Complete workflow with a single command
- 🎯 **Format Adaptive** - Automatically detects and processes multiple formats (PDF, EPUB, MOBI, etc.)
- 📊 **Visual Progress** - Real-time display of download and conversion progress

## 🎯 Use as Claude Skill (Recommended)

### Installation

```bash
# 1. Navigate to Claude Skills directory
cd ~/.claude/skills  # Windows: %APPDATA%\Claude\skills

# 2. Clone the repository
git clone https://github.com/zstmfhy/zlibrary-to-notebooklm.git zlib-to-notebooklm

# 3. Complete initial login
cd zlib-to-notebooklm
python3 scripts/login.py
```

### Usage

After installation, simply tell Claude Code:

```text
Use zlib-to-notebooklm skill to process this Z-Library link:
https://zh.zlib.li/book/25314781/aa05a1/book-title
```

Claude will automatically:

- Download the book (prioritizing PDF)
- Create NotebookLM notebook
- Upload the file
- Return notebook ID
- Suggest follow-up questions

---

## 🛠️ Traditional Installation

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/zstmfhy/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm

# Install Python dependencies
pip install playwright ebooklib

# Install Playwright browser
playwright install chromium
```

### 2. Login to Z-Library (One-time Only)

```bash
python3 scripts/login.py
```

**Steps:**
1. Browser will automatically open and visit Z-Library
2. Complete login in the browser
3. Return to terminal and press **ENTER**
4. Session saved!

### 3. Download and Upload Books

```bash
python3 scripts/upload.py "https://zh.zlib.li/book/..."
```

**Automatically completes:**

- ✅ Login using saved session
- ✅ Download PDF (preserves formatting)
- ✅ Fallback to EPUB → Markdown
- ✅ Smart chunking for large files (>350k words)
- ✅ Create NotebookLM notebook
- ✅ Upload content
- ✅ Return notebook ID

## 📖 Usage Examples

### Basic Usage

```bash
# Download single book
python3 scripts/upload.py "https://zh.zlib.li/book/12345/..."
```

### Batch Processing

```bash
# Batch download multiple books
for url in "url1" "url2" "url3"; do
    python3 scripts/upload.py "$url"
done
```

### Using NotebookLM

```bash
# After upload, use the notebook
notebooklm use <returned-notebook-id>

# Start asking questions
notebooklm ask "What are the core concepts of this book?"
notebooklm ask "Summarize Chapter 3"
```

## 🔄 Workflow

```text
Z-Library URL
    ↓
1. Launch browser (using saved session)
    ↓
2. Visit book page
    ↓
3. Smart format selection:
   - Priority: PDF (preserves formatting)
   - Fallback: EPUB (convert to Markdown)
   - Other formats (auto-convert)
    ↓
4. Download to ~/Downloads
    ↓
5. Format processing:
   - PDF → Use directly
   - EPUB → Convert to Markdown
   - Check file size → Auto-chunk if >350k words
    ↓
6. Create NotebookLM notebook
    ↓
7. Upload content (chunked files uploaded individually)
    ↓
8. Return notebook ID ✅
```

## 📁 Project Structure

```text
zlibrary-to-notebooklm/
├── SKILL.md              # Core Skill definition (required)
├── README.md             # Project documentation
├── README.zh-CN.md       # Chinese documentation
├── LICENSE               # MIT License
├── package.json          # npm config (for Claude Code skill)
├── skill.yaml            # Skill configuration
├── requirements.txt      # Python dependencies
├── scripts/              # Executable scripts (official standard)
│   ├── login.py         # Login script
│   ├── upload.py        # Download + Upload script
│   └── convert_epub.py  # EPUB conversion tool
├── docs/                 # Documentation
│   ├── WORKFLOW.md      # Workflow details
│   └── TROUBLESHOOTING.md # Troubleshooting guide
└── INSTALL.md            # Installation guide
```

## 🔧 Configuration

All configurations are saved in `~/.zlibrary/` directory:

```text
~/.zlibrary/
├── storage_state.json    # Login session (cookies)
├── browser_profile/      # Browser data
└── config.json          # Account config (backup)
```

## 🛠️ Dependencies

- **Python 3.8+**
- **playwright** - Browser automation
- **ebooklib** - EPUB file processing
- **NotebookLM CLI** - Google NotebookLM command-line tool

## 📝 Command Reference

### Login

```bash
python3 scripts/login.py
```

### Upload

```bash
python3 scripts/upload.py <Z-Library URL>
```

### Check Session Status

```bash
ls -lh ~/.zlibrary/storage_state.json
```

### Re-login

```bash
rm ~/.zlibrary/storage_state.json
python3 scripts/login.py
```

## 📊 NotebookLM Limits

This project is optimized for NotebookLM's actual limitations:

### Official Limits
- **File Size**: 200MB per file
- **Words per Source**: 500,000 words

### Practical Recommendations (CLI Tool)
- **Safe Word Count**: Maximum 350,000-380,000 words per file
- **Reason**: NotebookLM CLI tool has timeout and API limitations with large files

### Our Solution
✅ **Automatic File Chunking**:
- When EPUB is converted to Markdown, the script automatically detects word count
- Files exceeding 350,000 words are automatically split into multiple smaller files
- Each chunk is uploaded individually to the same NotebookLM notebook
- Smart chapter-based splitting preserves content integrity

**Example**:
```bash
📊 Word count: 2,700,000
⚠️  File exceeds 350k words (NotebookLM CLI limit)
📊 File too large, starting split...
   Total words: 2,700,000
   Max per chunk: 350,000 words
   ✅ Part 1/8: 342,000 words
   ✅ Part 2/8: 338,000 words
   ...
📦 Detected 8 file chunks
```

### Why 350k Words?
- Official limit is 500k words, but CLI tools tend to timeout near this limit
- 350k words is a tested safe value for reliable uploads
- Web interface can handle larger files directly, but CLI tools require chunking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Contributors

- [zstmfhy](https://github.com/zstmfhy) - Author
- [elhoim](https://github.com/elhoim) - English translation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Z-Library](https://zh.zlib.li/) - World's largest digital library
- [Google NotebookLM](https://notebooklm.google.com/) - AI-powered note-taking tool
- [Playwright](https://playwright.dev/) - Powerful browser automation tool

## 📮 Contact

- GitHub Issues: [Submit issues](https://github.com/zstmfhy/zlibrary-to-notebooklm/issues)
- Discussions: [GitHub Discussions](https://github.com/zstmfhy/zlibrary-to-notebooklm/discussions)

---

**⭐ If this project helps you, please give it a Star!**
