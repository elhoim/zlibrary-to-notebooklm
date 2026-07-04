# Workflow Details

## Full Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Z-Library to NotebookLM                   │
│                        Full Workflow                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  1. User enters a Z-Library book link │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  2. Check the local session state     │
        │     ~/.zlibrary/storage_state.json     │
        └───────────────────────────────────────┘
                     ↙              ↘
           Session exists      No session
                 ↓                      ↓
    ┌──────────────────┐      ┌─────────────────┐
    │  Use saved session│      │  Prompt to login │
    └──────────────────┘      │  python3 login.py│
                              └─────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  3. Launch the browser (Playwright)   │
        │     - Use a persistent context        │
        │     - Load the saved cookies          │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  4. Visit the book page               │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  5. Detect the page type              │
        └───────────────────────────────────────┘
                     ↙              ↘
             New UI                Old UI
         (three-dot menu)      (convert button)
                 ↓                   ↓
    ┌─────────────────┐   ┌──────────────────┐
    │ Click the menu  │   │ Find convert btn  │
    │ Choose a format │   │ Click convert     │
    └─────────────────┘   └──────────────────┘
                 ↘                   ↙
                  └─────────┬──────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  6. Smart format selection            │
        │     Priority: PDF > EPUB > Other      │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  7. Wait for conversion (if needed)   │
        │     - Detect the "conversion done" msg│
        │     - Wait up to 60 seconds           │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  8. Click the download link           │
        │     - Click via JavaScript            │
        │     - Bypass visibility issues        │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  9. Wait for the download to finish   │
        │     - Listen for the download event   │
        │     - Save to ~/Downloads/            │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  10. Format processing                │
        │      ↙          ↘                    │
        │   Is PDF        Is EPUB               │
        │     ↓            ↓                    │
        │  Use directly  Convert to TXT         │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  11. Create a NotebookLM notebook     │
        │      - notebooklm create              │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  12. Upload the content               │
        │      - notebooklm source add          │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  13. Return the notebook ID           │
        │      - The user can start using it    │
        └───────────────────────────────────────┘
                            ↓
                      ✅ Done!
```

## Detailed Step Descriptions

### Steps 1-2: Initialization and session check

**Detecting the session state:**
- Location: `~/.zlibrary/storage_state.json`
- Contents: cookies, localStorage, sessionStorage
- Permissions: 600 (owner read/write only)

**If there is no session:**
```bash
python3 scripts/login.py
```

### Steps 3-4: Browser launch and page visit

**Using a Playwright persistent context:**
```python
browser = await p.chromium.launch_persistent_context(
    user_data_dir="~/.zlibrary/browser_profile",
    headless=False,
    accept_downloads=True
)
```

**Advantages:**
- Retains all cookies
- Retains the browser cache
- No repeated logins needed

### Steps 5-6: Page type detection and format selection

**New UI (three-dot menu):**
```python
dots_button = await page.query_selector('[class*="dots"]')
if dots_button:
    # Click the menu and choose a format
```

**Old UI (convert button):**
```python
convert_button = await page.query_selector('a[data-convert_to="pdf"]')
if convert_button:
    # Click the convert button
```

**Format priority:**
1. **PDF** ⭐ - preserves formatting, no conversion needed
2. **EPUB** - converted to plain text (best for AI retrieval)
3. **Other** - handled case by case

### Steps 7-8: Conversion and download

**Wait for the conversion to complete:**
```python
for i in range(60):
    message = await page.query_selector('.message:has-text("转换为")')
    if '完成' in await message.inner_text():
        break
    await asyncio.sleep(1)
```

**JavaScript click (bypasses visibility issues):**
```python
await download_link.evaluate('el => el.click()')
```

### Steps 9-10: Download and format processing

**Listen for the download event:**
```python
async def handle_download(download):
    file_path = downloads_dir / download.suggested_filename
    await download.save_as(file_path)

page.on('download', handle_download)
```

**Format processing:**
- **PDF** → use directly
- **EPUB** → extract text with ebooklib

### Steps 11-12: NotebookLM upload

**Create a notebook:**
```bash
notebooklm create "Book Title" --json
```

**Upload the content:**
```bash
notebooklm source add "file path" --json
```

## Troubleshooting

### Issue 1: Session expired

**Symptom:** it says you are not logged in

**Fix:**
```bash
rm ~/.zlibrary/storage_state.json
python3 scripts/login.py
```

### Issue 2: Download button not found

**Symptom:** "No download link found"

**Possible causes:**
- Page structure changed
- Login required
- Network issue

**Fix:**
- Check the browser window
- Complete the action manually
- Take a screenshot for debugging

### Issue 3: Conversion timeout

**Symptom:** "Conversion timeout"

**Fix:**
- Check your network connection
- Try clicking convert manually
- Increase the wait time

## Best Practices

1. **Check the session state regularly**
   ```bash
   ls -lh ~/.zlibrary/storage_state.json
   ```

2. **Add a delay when batch processing**
   ```bash
   for url in "url1" "url2" "url3"; do
       python3 scripts/upload.py "$url"
       sleep 5  # avoid sending requests too fast
   done
   ```

3. **Keep the original files**
   - All downloaded files are saved in `~/Downloads/`
   - Converted text is in `/tmp/`
   - You can back them up or reprocess them at any time

## Performance Optimization

- Use a persistent browser context (reduces startup time)
- Concurrent downloads (when batch processing)
- Smart format selection (prefer PDF to reduce conversion time)

---

**Need help?** See the [Troubleshooting Guide](TROUBLESHOOTING.md)
