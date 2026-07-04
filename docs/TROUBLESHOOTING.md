# Troubleshooting Guide

This document helps you solve common problems you may run into while using the zlibrary-to-notebooklm Skill.

---

## 🔐 Login Issues

### Issue: Login session not found

**Symptom:**
```
❌ Session state not found
💡 Please run first: python3 scripts/login.py
```

**Solution:**

1. **First-time use requires a login**
   ```bash
   cd ~/.claude/skills/zlibrary-to-notebooklm
   python3 scripts/login.py
   ```

2. **Login steps:**
   - The browser opens Z-Library automatically
   - Complete the login in the browser
   - Return to the terminal and press ENTER
   - The session is saved!

3. **Verify the login state:**
   ```bash
   ls -lh ~/.zlibrary/storage_state.json
   ```
   It should show a file of about 2KB

### Issue: Login fails

**Symptom:**
- The browser opens but you cannot log in
- A "network error" is shown

**Solution:**

1. **Check your network connection**
   ```bash
   ping -c 3 zh.zlib.li
   ```

2. **Try a backup domain**
   - https://zh.zlib.li/
   - https://z-lib.org/
   - https://zlibrary.org/

3. **Clear the cache and retry**
   ```bash
   rm ~/.zlibrary/storage_state.json
   python3 scripts/login.py
   ```

---

## 📥 Download Issues

### Issue: Download button not found

**Symptom:**
```
❌ No download button found
```

**Possible causes:**
1. The Z-Library page structure changed
2. Login required
3. Network issue

**Solution:**

1. **Check the login state**
   ```bash
   ls ~/.zlibrary/storage_state.json
   ```

2. **Open the page manually to confirm**
   - Copy the link into a browser and open it
   - Confirm you can access and download normally

3. **Use the fallback**
   - Manually download the PDF to `~/Downloads/`
   - Upload it with `notebooklm source add`

### Issue: Download timeout

**Symptom:**
```
⏳ Wait timed out
❌ Download failed
```

**Solution:**

1. **Check network stability**
   ```bash
   # Test the connection
   curl -I https://zh.zlib.li
   ```

2. **Increase the wait time**
   - The script waits 60 seconds by default
   - A slow network may need longer

3. **Retry the download**
   ```bash
   # Run it again
   python3 scripts/upload.py "your link"
   ```

### Issue: Conversion timeout

**Symptom:**
```
⚠️ Conversion timed out, trying to continue...
```

**Solution:**

1. **This is normal**
   - Z-Library needs time to convert formats
   - It can take up to 60 seconds

2. **Be patient**
   - The script automatically detects when the conversion completes
   - It starts downloading automatically once done

3. **If it keeps timing out**
   - Try refreshing the page and retrying
   - Choose a different format (such as a direct PDF)

---

## 📤 Upload Issues

### Issue: NotebookLM command not found

**Symptom:**
```
command not found: notebooklm
```

**Solution:**

1. **Install the NotebookLM CLI**
   ```bash
   npm install -g @google-notebooklm/cli
   ```

2. **Verify the installation**
   ```bash
   notebooklm --version
   ```

3. **Configure login**
   ```bash
   notebooklm login
   ```

### Issue: Upload fails

**Symptom:**
```
✅ Notebook created
❌ Upload failed
```

**Possible causes:**
1. The file is too large (NotebookLM has an upload limit)
2. Network issue
3. Unsupported format

**Solution:**

1. **Check the file size**
   ```bash
   ls -lh ~/Downloads/*.pdf
   ```
   - NotebookLM usually limits files to under 50MB
   - Larger files need to be compressed or split

2. **Check the file format**
   - Supported formats: PDF, TXT, Markdown, Google Docs
   - Not supported: EPUB, MOBI, AZW3

3. **Test a manual upload**
   ```bash
   notebooklm source add "file path"
   ```

---

## 🔧 Technical Issues

### Issue: Playwright is not installed

**Symptom:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Solution:**

1. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install the browser**
   ```bash
   playwright install chromium
   ```

3. **Verify the installation**
   ```bash
   python3 -c "import playwright; print(playwright.__version__)"
   ```

### Issue: ebooklib conversion fails

**Symptom:**
```
❌ Conversion failed: ...
```

**Solution:**

1. **Check the EPUB file**
   ```bash
   # Confirm the file exists
   ls -lh ~/Downloads/*.epub
   ```

2. **Test a manual conversion**
   ```bash
   python3 scripts/convert_epub.py "EPUB path" "output path.txt"
   ```

3. **Use a PDF instead**
   - PDF format has better compatibility
   - No conversion needed, upload directly

### Issue: Browser crashes

**Symptom:**
```
Browser crashed: ...
```

**Solution:**

1. **Update Playwright**
   ```bash
   pip install --upgrade playwright
   playwright install chromium --force
   ```

2. **Use headless mode (may be more stable)**
   - Change `headless=False` to `headless=True` in the script

3. **Check system resources**
   ```bash
   # Check memory usage
   top
   ```

---

## 📊 Configuration Issues

### Issue: Session expires frequently

**Symptom:**
- You have to log in again on every run
- It says "session state not found"

**Solution:**

1. **Check the file permissions**
   ```bash
   ls -l ~/.zlibrary/storage_state.json
   ```
   It should show `-rw-------` (600)

2. **Fix the permissions**
   ```bash
   chmod 600 ~/.zlibrary/storage_state.json
   ```

3. **Regenerate the session**
   ```bash
   rm ~/.zlibrary/storage_state.json
   python3 scripts/login.py
   ```

### Issue: Wrong download directory

**Symptom:**
- Files download to an unknown location
- You cannot find the downloaded file

**Solution:**

1. **Default download directory**
   - macOS/Linux: `~/Downloads/`
   - Windows: `%USERPROFILE%/Downloads/`

2. **Find the most recently downloaded file**
   ```bash
   # Find the latest PDF/EPUB
   ls -lt ~/Downloads/*.{pdf,epub} 2>/dev/null | head -5
   ```

3. **Customize the download directory**
   - Change the `downloads_dir` variable in the script

---

## 🌐 Network Issues

### Issue: Cannot access Z-Library

**Symptom:**
```
Failed to connect to zh.zlib.li port 443
```

**Solution:**

1. **Check DNS**
   ```bash
   # See whether it is a Z-Library domain resolution issue
   nslookup zh.zlib.li
   ```

2. **Try a backup domain**
   - https://zh.zlib.li/
   - https://z-lib.org/
   - https://zlibrary.org/

3. **Check your proxy settings**
   - If you use a VPN, try switching nodes
   - Or temporarily turn off the VPN

4. **Use a mirror site** (if one is available)

---

## 📝 Usage Issues

### Issue: Claude does not recognize the Skill

**Symptom:**
- You mention the Skill in Claude Code, but Claude does not know how to use it

**Solution:**

1. **Confirm SKILL.md exists**
   ```bash
   ls -l ~/.claude/skills/zlib-to-notebooklm/SKILL.md
   ```

2. **Check the file permissions**
   ```bash
   chmod 644 ~/.claude/skills/zlib-to-notebooklm/SKILL.md
   ```

3. **Restart Claude Code**
   - Fully quit Claude Code
   - Reopen it
   - Let Claude reload the Skills

4. **Use the full trigger phrasing**
   - Mention a Z-Library link
   - Explicitly say "upload to NotebookLM"

---

## 🆘 Still Stuck?

### Collect diagnostic information

Before asking for help, please collect the following:

1. **System information**
   ```bash
   python3 --version
   uname -a  # macOS/Linux
   # or Windows: systeminfo
   ```

2. **Dependency versions**
   ```bash
   pip list | grep -E "playwright|ebooklib"
   ```

3. **Error logs**
   - The complete error message from the run
   - A screenshot (if possible)

4. **Reproduction steps**
   - What you did
   - What you expected to happen
   - What actually happened

### Get help

- **GitHub Issues**: [Submit an issue](https://github.com/zstmfhy/zlibrary-to-notebooklm/issues)
- **Read the docs**: [README.md](../README.md)
- **Check SKILL.md**: [SKILL.md](../SKILL.md)

---

## 💡 Best Practices

### Avoid common problems

1. **Check the login state regularly**
   ```bash
   # Check once a week
   ls -lh ~/.zlibrary/storage_state.json
   ```

2. **Keep dependencies up to date**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Use legal resources**
   - Only upload content you have the rights to
   - Follow your local laws and regulations

4. **Add a delay when batch processing**
   ```bash
   # Avoid sending requests too fast
   for url in "url1" "url2" "url3"; do
       python3 scripts/upload.py "$url"
       sleep 5  # wait 5 seconds
   done
   ```

---

**Document version**: 1.1.0
**Last updated**: 2026-07-04
