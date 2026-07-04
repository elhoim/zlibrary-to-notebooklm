---
name: zlibrary-to-notebooklm
description: Automatically download books from Z-Library and upload them to Google NotebookLM. Supports PDF/EPUB formats, automatic conversion, and one-command knowledge base creation.
---

# Z-Library to NotebookLM Skill

Let Claude automatically download books and upload them to NotebookLM for a "zero-hallucination" AI conversational reading experience.

## 🎯 Core Features

- One-command book download (prefers PDF, automatically falls back to EPUB)
- Automatically creates a NotebookLM notebook
- Uploads the file and returns the notebook ID
- Supports AI conversations grounded in the book's content

## 📋 Triggers

Use this Skill when the user mentions any of the following:

- The user provides a Z-Library book link (containing domains such as `zlib.li`, `z-lib.org`, `zh.zlib.li`)
- The user says "help me upload this book to NotebookLM"
- The user says "automatically download and read this book"
- The user says "create a NotebookLM knowledge base from a Z-Library link"
- The user asks to download and analyze a book from a specific URL

## 🔧 Core Instructions

When the user provides a Z-Library link, follow this workflow:

### Step 1: Extract information

Extract the following from the URL the user provides:
- Book title
- Author (if available)
- Full URL
- Format options (PDF/EPUB/MOBI, etc.)

### Step 2: Automatic download

Use the saved session (`~/.zlibrary/storage_state.json`) to log in to Z-Library automatically:

1. **Prefer PDF** (preserves formatting, better for AI analysis)
2. **Automatic fallback**: if no PDF is available, download the EPUB
3. **Format conversion**: if an EPUB is downloaded, convert it to plain text using ebooklib

### Step 3: Create a NotebookLM notebook

```bash
notebooklm create "Book Title"
```

### Step 4: Upload the file

```bash
notebooklm source add "file path"
```

### Step 5: Return the result

Return to the user:
- ✅ Download success confirmation
- 📚 Notebook ID
- 💡 Example follow-up questions

### Step 6: Error handling

If an error occurs:
- Retry up to 3 times
- If login fails, prompt the user to run `python3 ~/.claude/skills/zlibrary-to-notebooklm/scripts/login.py`
- If the download fails, provide troubleshooting suggestions

## ⚠️ Important Restrictions

**Legal resources only!**

- ✅ Resources the user has legal access to
- ✅ Public domain or open-source licensed documents
- ✅ Content the user personally owns or is authorized to use
- ❌ Do not encourage or assist with copyright infringement

**If the URL clearly involves copyrighted commercial works, remind the user:**
> "Please make sure you have legal access. This project is for learning and research purposes only — please support official, authorized reading."

## 🛠️ Dependencies

### Required tools

1. **Playwright** - browser automation
   - Used for automatic login and download
   - Requires running `playwright install chromium` beforehand

2. **ebooklib** - EPUB processing
   - Used to convert EPUB to plain text

3. **NotebookLM CLI** - upload tool
   - `notebooklm create` - create a notebook
   - `notebooklm source add` - upload a file

### Configuration files

- `~/.zlibrary/storage_state.json` - saved login session
- `~/.zlibrary/browser_profile/` - browser data

## 📝 Usage Example

### User request

```
Help me upload this book to NotebookLM:
https://zh.zlib.li/book/25314781/aa05a1/the-fourth-dimension-of-money
```

### Execution flow

1. **Confirm and extract information**
   ```
   Title: The Fourth Dimension of Money
   URL: https://zh.zlib.li/book/25314781/aa05a1/the-fourth-dimension-of-money
   ```

2. **Run the download script**
   ```bash
   cd ~/.claude/skills/zlibrary-to-notebooklm
   python3 scripts/upload.py "https://zh.zlib.li/book/25314781/aa05a1/the-fourth-dimension-of-money"
   ```

3. **Return the result**
   ```
   ✅ Download successful!
   📚 Notebook ID: 22916611-c68c-4065-a657-99339e126fb4

   Now you can ask me:
   - "What are the core ideas of this book?"
   - "Summarize Chapter 3"
   - "What unique insights does the author offer?"
   ```

## 🔄 Alternative Flows

### If the user provides only a title

```
User: "Help me download the book 'Awakening'"
```

**Actions:**
1. Ask: "Do you have a Z-Library link for it?"
2. If there is a link, run the standard flow
3. If there is no link, prompt: "Please provide a Z-Library book page link, and I can automatically download it and upload it to NotebookLM"

### If the user provides another source

```
User: "Can this PDF be uploaded to NotebookLM? [local file path]"
```

**Actions:**
1. Tell the user: "This Skill is primarily for Z-Library links"
2. Suggest: "For local files, you can upload directly with the notebooklm source add command"

## 📊 Technical Details

### Download priority

1. **PDF** - preserves formatting, best for AI analysis
2. **EPUB** - converted to plain text (using ebooklib)
3. **Other formats** - attempt conversion or prompt the user

### Session management

- **Log in once, use forever**
- The session is saved in `~/.zlibrary/storage_state.json`
- If the session expires, prompt the user to log in again

### Error retries

- Download failure: automatically retry 3 times
- Login failure: prompt the user to log in manually
- Upload failure: check the file size and format

## 💡 Best Practices

### First-time use

Before the first use, make sure the user has logged in:

```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
python3 scripts/login.py
```

### Batch processing

If the user has multiple links:

```
User: "Help me download these 3 books: [link1] [link2] [link3]"
```

**Actions:**
1. Process them one at a time (one link per run)
2. Move on to the next one after each completes
3. Avoid concurrency, which can cause session conflicts

### Content analysis

After the upload completes, proactively suggest:

```
✅ The book has been uploaded! You can:

• Start reading right away: "What are the core ideas of this book?"
• Go deeper: "Explain the case study in Chapter 5"
• Generate notes: "Create detailed reading notes"
• Compare and contrast: "How does this differ from the book's viewpoint?"
```

## 🚨 Troubleshooting

### Common questions

**Q: It says "login session not found"**
A: You need to run `python3 scripts/login.py` to log in once first

**Q: Download failed with a timeout**
A: It may be a network issue; try again or check your connection

**Q: The download button cannot be found**
A: The Z-Library page structure may have changed; use the fallback to download manually

**Q: NotebookLM upload failed**
A: Check the file size (NotebookLM has an upload limit)

### Detailed help

See `docs/TROUBLESHOOTING.md` for the complete troubleshooting guide.

## 📚 Related Resources

- [NotebookLM Official Docs](https://notebooklm.google.com/)
- [Z-Library Website](https://zh.zlib.li/)
- [Playwright Docs](https://playwright.dev/)
- [Project GitHub](https://github.com/zstmfhy/zlibrary-to-notebooklm)

## 🎓 Learning Resources

If you want to learn more:

- **How to use NotebookLM effectively**: ask "What are some tips for using NotebookLM?"
- **How to build a personal knowledge base**: ask "How can I build a knowledge management system with NotebookLM?"
- **AI conversational reading**: ask "How can AI help me deeply read a book?"

---

**Skill Version:** 1.1.0
**Last Updated:** 2026-07-04
**Author:** zstmfhy
**Contributors:** elhoim
