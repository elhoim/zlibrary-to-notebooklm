#!/usr/bin/env python3
"""
Z-Library fully automated download and upload to NotebookLM
"""

import asyncio
import sys
import time
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

# UUID pattern used to extract notebook/source IDs from CLI output
# (both the native `notebooklm` CLI and `nlm` identify resources by UUID)
_UUID_RE = re.compile(
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
)

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright is not installed")
    print("Please run: pip install playwright")
    sys.exit(1)


class ZLibraryAutoUploader:
    """Z-Library automatic download-and-upload helper"""

    def __init__(self):
        self.downloads_dir = Path.home() / "Downloads"
        self.temp_dir = Path("/tmp")
        self.config_dir = Path.home() / ".zlibrary"
        self.config_file = self.config_dir / "config.json"

    def load_credentials(self) -> dict | None:
        """Load Z-Library credentials"""
        if not self.config_file.exists():
            return None

        try:
            import json
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return None

    async def login_to_zlibrary(self, page):
        """Log in to Z-Library"""
        credentials = self.load_credentials()

        if not credentials:
            print("⚠️  Z-Library configuration not found")
            print("💡 Please run first: python3 scripts/login.py")
            return False

        print("🔐 Logging in to Z-Library...")
        print(f"📧 Using account: {credentials['email']}")

        try:
            # Check whether a login dialog is already present
            modal = await page.query_selector('#zlibrary-modal-auth')
            if modal:
                print("📝 Login dialog detected")
                # Fill the fields directly in the dialog
                email_input = await page.wait_for_selector('#modal-auth input[type="email"], #modal-auth input[name="email"]', timeout=5000)
                await email_input.fill(credentials['email'])

                password_input = await page.wait_for_selector('#modal-auth input[type="password"], #modal-auth input[name="password"]', timeout=5000)
                await password_input.fill(credentials['password'])

                # Click login
                submit_button = await page.wait_for_selector('#modal-auth button[type="submit"]', timeout=5000)
                await submit_button.click()
            else:
                # Click the login button (Chinese selector text matches the live page)
                login_button = await page.wait_for_selector('a:has-text("Log in"), a:has-text("登录")', timeout=5000)
                await login_button.click()
                await asyncio.sleep(2)

                # Enter the email
                email_input = await page.wait_for_selector('input[type="email"], input[name="email"]', timeout=5000)
                await email_input.fill(credentials['email'])

                # Enter the password
                password_input = await page.wait_for_selector('input[type="password"], input[name="password"]', timeout=5000)
                await password_input.fill(credentials['password'])

                # Click login (Chinese selector text matches the live page)
                submit_button = await page.wait_for_selector('button[type="submit"], button:has-text("Log in"), button:has-text("登录")', timeout=5000)
                await submit_button.click()

            # Wait for the login to complete
            await asyncio.sleep(5)

            # Check whether the login succeeded
            current_url = page.url
            page_content = await page.content()

            # "登录" ("Log in") disappearing from the page indicates a successful login
            if "logout" in page_content.lower() or "登录" not in page_content:
                print("✅ Login successful")
                return True
            else:
                print("❌ Login may have failed, please check your account and password")
                return False

        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False

    async def download_from_zlibrary(self, url: str) -> Path | None:
        """Download a book from Z-Library"""
        print("="*70)
        print("🌐 Starting browser-automated download")
        print("="*70)

        # Check whether a saved session exists
        storage_state = self.config_dir / "storage_state.json"

        if not storage_state.exists():
            print("❌ Session state not found")
            print("💡 Please run first: python3 scripts/login.py")
            return None

        print(f"✅ Using the saved session")

        async with async_playwright() as p:
            # Launch the browser (using a persistent context)
            print("🚀 Launching browser...")

            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.config_dir / "browser_profile"),
                headless=False,
                accept_downloads=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            page = browser.pages[0] if browser.pages else await browser.new_page()
            page.set_default_timeout(60000)

            # Set up download handling
            download_path = None

            async def handle_download(download):
                nonlocal download_path
                print("✅ Download start detected...")
                suggested_filename = download.suggested_filename
                print(f"📄 Filename: {suggested_filename}")
                download_path = self.downloads_dir / suggested_filename
                await download.save_as(download_path)
                print(f"💾 Saved: {download_path}")

            page.on('download', handle_download)

            try:
                # Visit the target page
                print(f"📖 Visiting the book page...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)

                print("⏳ Waiting for the page to load...")
                await asyncio.sleep(5)

                # Step 1: find a download method (prefer PDF, then EPUB)
                print("🔍 Step 1: looking for a download method...")

                # First check for a three-dot menu button (new UI); Chinese selector text matches the live page
                dots_button = await page.query_selector('button[aria-label="更多选项"], button[title="更多"], .more-options, [class*="dots"], [class*="more"]')

                download_link = None
                downloaded_format = None

                if dots_button:
                    print("📱 New UI detected (three-dot menu)")
                    # Click to open the menu
                    await dots_button.click()
                    await asyncio.sleep(2)

                    # Look for a PDF option (preferred)
                    print("🔍 Looking for a PDF option...")
                    pdf_options = await page.query_selector_all('a:has-text("PDF"), button:has-text("PDF")')
                    if pdf_options:
                        # Pick the first PDF (usually the smallest file)
                        download_link = pdf_options[0]
                        downloaded_format = 'pdf'
                        print(f"✅ Found a PDF option")
                    else:
                        # Fallback: look for EPUB
                        print("🔍 No PDF found, looking for an EPUB option...")
                        epub_options = await page.query_selector_all('a:has-text("EPUB"), button:has-text("EPUB")')
                        if epub_options:
                            download_link = epub_options[0]
                            downloaded_format = 'epub'
                            print(f"✅ Found an EPUB option")

                else:
                    # Old UI: check for a convert button
                    print("📱 Old UI detected")
                    convert_selector_pdf = 'a[data-convert_to="pdf"]'
                    convert_selector_epub = 'a[data-convert_to="epub"]'

                    # Try PDF first
                    convert_button = await page.query_selector(convert_selector_pdf)

                    if convert_button:
                        print("📝 PDF convert button detected")
                        downloaded_format = 'pdf'
                        await convert_button.evaluate('el => el.click()')
                        print("✅ Clicked the PDF convert button")

                        # Wait for the conversion to complete
                        print("⏳ Waiting for the PDF conversion to complete...")
                        for i in range(60):
                            await asyncio.sleep(1)
                            try:
                                # Chinese "转换为" ("converted to") matches the live status message
                                message = await page.query_selector('.message:has-text("转换为")')
                                if message:
                                    message_text = await message.inner_text()
                                    # Chinese "完成" means "done/complete"
                                    if 'pdf' in message_text.lower() and '完成' in message_text:
                                        print("✅ PDF conversion complete!")
                                        break
                            except:
                                pass
                            if i % 10 == 0 and i > 0:
                                print(f"   ⏳ Waiting... {i}s")

                        # Look for the download link
                        download_link = await page.query_selector('a[href*="/dl/"][href*="convertedTo=pdf"]')

                        if not download_link:
                            all_links = await page.query_selector_all('a[href*="/dl/"]')
                            if all_links:
                                download_link = all_links[0]
                                href = await download_link.get_attribute('href')
                                print(f"✅ Found download link: {href}")

                    else:
                        # Fallback: try EPUB
                        convert_button = await page.query_selector(convert_selector_epub)

                        if convert_button:
                            print("📝 EPUB convert button detected")
                            downloaded_format = 'epub'
                            await convert_button.evaluate('el => el.click()')
                            print("✅ Clicked the EPUB convert button")

                            # Wait for the conversion to complete
                            print("⏳ Waiting for the EPUB conversion to complete...")
                            for i in range(60):
                                await asyncio.sleep(1)
                                try:
                                    # Chinese "转换为" ("converted to") matches the live status message
                                    message = await page.query_selector('.message:has-text("转换为")')
                                    if message:
                                        message_text = await message.inner_text()
                                        # Chinese "完成" means "done/complete"
                                        if 'epub' in message_text.lower() and '完成' in message_text:
                                            print("✅ EPUB conversion complete!")
                                            break
                                except:
                                    pass
                                if i % 10 == 0 and i > 0:
                                    print(f"   ⏳ Waiting... {i}s")

                            # Look for the download link
                            download_link = await page.query_selector('a[href*="/dl/"][href*="convertedTo=epub"]')

                            if not download_link:
                                all_links = await page.query_selector_all('a[href*="/dl/"]')
                                if all_links:
                                    download_link = all_links[0]
                                    href = await download_link.get_attribute('href')
                                    print(f"✅ Found download link: {href}")

                # If still not found, try a direct download link
                if not download_link:
                    print("🔍 No convert button detected, looking for a direct download link...")

                    # Chinese "下载" ("Download") selector text matches the live page
                    selectors = [
                        'a[href*="/dl/"]',
                        'a:has-text("下载")',
                        'a:has-text("Download")',
                        'button:has-text("下载")',
                    ]

                    for selector in selectors:
                        try:
                            links = await page.query_selector_all(selector)
                            if links:
                                for link in links:
                                    href = await link.get_attribute('href')
                                    if href and '/dl/' in href:
                                        download_link = link
                                        # Infer the format from the URL
                                        if 'pdf' in href.lower():
                                            downloaded_format = 'pdf'
                                        elif 'epub' in href.lower():
                                            downloaded_format = 'epub'
                                        print(f"✅ Found download link: {href} (format: {downloaded_format})")
                                        break
                                if download_link:
                                    break
                        except:
                            continue

                if not download_link:
                    print("❌ No download link found")
                    await browser.close()
                    return None

                # Click to download
                print("⬇️  Step 2: clicking the download link...")

                try:
                    await download_link.evaluate('el => el.click()')
                    print("✅ Click succeeded")
                except Exception as e:
                    print(f"❌ Click failed: {e}")
                    await browser.close()
                    return None

                # Wait for the download
                print("⏳ Step 3: waiting for the download to complete...")
                await asyncio.sleep(20)

                # Check the result
                if download_path and download_path.exists():
                    file_size = download_path.stat().st_size / 1024
                    print(f"✅ Download successful!")
                    print(f"   Format: {downloaded_format.upper() if downloaded_format else 'Unknown'}")
                    print(f"   File: {download_path.name}")
                    print(f"   Path: {download_path}")
                    print(f"   Size: {file_size:.1f} KB")
                    await browser.close()
                    return download_path, downloaded_format

                # Fallback: scan the downloads directory
                print("🔍 Checking the downloads directory...")

                # Look for a file based on the format
                if downloaded_format == 'pdf':
                    pattern = "*.pdf"
                else:
                    pattern = "*.epub"

                downloaded_files = list(self.downloads_dir.glob(pattern))

                if downloaded_files:
                    latest_file = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                    file_age = time.time() - latest_file.stat().st_mtime

                    if file_age < 120:
                        file_size = latest_file.stat().st_size / 1024
                        print(f"✅ Download successful!")
                        print(f"   Format: {downloaded_format.upper() if downloaded_format else 'Unknown'}")
                        print(f"   File: {latest_file.name}")
                        print(f"   Path: {latest_file}")
                        print(f"   Size: {file_size:.1f} KB")
                        await browser.close()
                        return latest_file, downloaded_format

                print("❌ No downloaded file found")
                await browser.close()
                return None, None

            except Exception as e:
                print(f"❌ Download failed: {e}")
                import traceback
                traceback.print_exc()
                await browser.close()
                return None, None

    def count_words(self, text: str) -> int:
        """Count words for both Chinese and English text"""
        import re
        # Match Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Match English words
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + english_words

    def split_markdown_file(self, file_path: Path, max_words: int = 350000) -> list[Path]:
        """Split a large Markdown file into several smaller files"""
        print(f"📊 File too large, starting split...")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        total_words = self.count_words(content)
        print(f"   Total words: {total_words:,}")
        print(f"   Max per chunk: {max_words:,} words")

        # Split by chapter (looking for ## or ### headings)
        import re
        chapters = re.split(r'\n(?=#{1,3}\s)', content)

        chunks = []
        current_chunk = ""
        current_words = 0
        chunk_num = 1

        for i, chapter in enumerate(chapters):
            chapter_words = self.count_words(chapter)

            # If a single chapter exceeds the limit, split it further
            if chapter_words > max_words:
                # First save the current chunk
                if current_chunk:
                    chunks.append(current_chunk)
                    chunk_num += 1
                    current_chunk = ""
                    current_words = 0

                # Split the large chapter (by paragraph)
                paragraphs = chapter.split('\n\n')
                temp_chunk = ""
                temp_words = 0

                for para in paragraphs:
                    para_words = self.count_words(para)
                    if temp_words + para_words > max_words and temp_chunk:
                        chunks.append(temp_chunk)
                        chunk_num += 1
                        temp_chunk = para + "\n\n"
                        temp_words = para_words
                    else:
                        temp_chunk += para + "\n\n"
                        temp_words += para_words

                if temp_chunk:
                    current_chunk = temp_chunk
                    current_words = temp_words

            elif current_words + chapter_words > max_words:
                # The current chunk is full; save it and start a new one
                chunks.append(current_chunk)
                chunk_num += 1
                current_chunk = chapter + "\n\n"
                current_words = chapter_words
            else:
                # Append to the current chunk
                current_chunk += chapter + "\n\n"
                current_words += chapter_words

        # Save the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        # Write the files
        chunk_files = []
        stem = file_path.stem
        for i, chunk in enumerate(chunks, 1):
            chunk_file = file_path.parent / f"{stem}_part{i}.md"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            chunk_files.append(chunk_file)
            chunk_words = self.count_words(chunk)
            print(f"   ✅ Part {i}/{len(chunks)}: {chunk_words:,} words")

        return chunk_files

    def convert_to_txt(self, file_path: Path, file_format: str = None) -> Path | list[Path]:
        """Convert the file to TXT, or use the PDF directly"""
        print("")
        print("="*70)
        print("📝 Processing file")
        print("="*70)

        file_ext = file_path.suffix.lower()

        # If it is a PDF, use it directly (option A)
        if file_ext == '.pdf' or file_format == 'pdf':
            print("✅ PDF format detected, using it directly")
            print(f"   File: {file_path.name}")
            return file_path

        md_file = self.temp_dir / f"{file_path.stem}.md"

        # If it is an EPUB, convert it to Markdown
        if file_ext == '.epub':
            print("📖 EPUB format detected, converting to Markdown...")
            # Get the directory this script lives in
            script_dir = Path(__file__).parent
            convert_script = script_dir / "convert_epub.py"

            cmd = f"python3 '{convert_script}' '{file_path}' '{md_file}'"
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Conversion failed: {result.stderr}")
                return file_path

            print(f"✅ Conversion successful: {md_file}")

            # Check the file size and split it if it is too large
            word_count = self.count_words(open(md_file, 'r', encoding='utf-8').read())
            print(f"📊 Word count: {word_count:,}")

            if word_count > 350000:
                print(f"⚠️  File exceeds 350k words (NotebookLM CLI limit)")
                return self.split_markdown_file(md_file)
            else:
                return md_file

        else:
            print(f"ℹ️  File format: {file_ext}, using it directly")
            return file_path

    def detect_notebooklm_backend(self) -> str | None:
        """Detect which NotebookLM command-line tool is installed.

        Returns the backend name to use, preferring the skill's native
        `notebooklm` CLI when present and falling back to `nlm`
        (the NotebookLM companion CLI, https://github.com/tmc/nlm).
        Returns None if neither tool is on PATH.
        """
        if shutil.which("notebooklm"):
            return "notebooklm"
        if shutil.which("nlm"):
            return "nlm"
        return None

    def _nlm_notebook_ids(self) -> set:
        """Return the set of existing notebook UUIDs known to `nlm`."""
        import subprocess
        try:
            r = subprocess.run(
                ["nlm", "notebook", "list", "--quiet"],
                capture_output=True, text=True
            )
            return set(_UUID_RE.findall(r.stdout))
        except Exception:
            return set()

    def _nb_create(self, backend: str, title: str):
        """Create a notebook. Returns (notebook_id, error)."""
        import subprocess
        import json

        if backend == "notebooklm":
            result = subprocess.run(
                ["notebooklm", "create", title, "--json"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return None, result.stderr
            try:
                return json.loads(result.stdout)["notebook"]["id"], None
            except Exception:
                return None, "Failed to parse the notebook ID from notebooklm output"

        # backend == "nlm": no --json flag, so snapshot IDs to identify the new one
        before = self._nlm_notebook_ids()
        result = subprocess.run(
            ["nlm", "notebook", "create", title],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None, result.stderr
        # Primary: the created notebook's UUID is usually echoed in the output
        match = _UUID_RE.search(result.stdout)
        if match:
            return match.group(0), None
        # Fallback: diff the notebook list to find the newly created ID
        new_ids = self._nlm_notebook_ids() - before
        if len(new_ids) == 1:
            return next(iter(new_ids)), None
        return None, "Created the notebook but could not determine its ID from nlm"

    def _nb_use(self, backend: str, notebook_id: str) -> None:
        """Set the active notebook context (only meaningful for `notebooklm`)."""
        import subprocess
        if backend == "notebooklm":
            subprocess.run(["notebooklm", "use", notebook_id], capture_output=True)
        # `nlm` takes the notebook ID explicitly per command, so there is no context to set

    def _nb_add_source(self, backend: str, notebook_id: str, file_path: Path):
        """Upload one file as a source. Returns (source_id, error).

        source_id may be an empty string on success if the tool does not
        print a parseable ID (the upload still succeeded).
        """
        import subprocess
        import json

        if backend == "notebooklm":
            # Relies on the notebook context set by _nb_use()
            result = subprocess.run(
                ["notebooklm", "source", "add", str(file_path), "--json"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return None, result.stderr
            try:
                return json.loads(result.stdout)["source"]["id"], None
            except Exception:
                return "", None  # succeeded but no parseable ID

        # backend == "nlm": pass the notebook ID explicitly and wait for processing
        result = subprocess.run(
            ["nlm", "source", "add", notebook_id, "--file", str(file_path), "--wait"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None, result.stderr
        match = _UUID_RE.search(result.stdout)
        return (match.group(0) if match else ""), None

    def upload_to_notebooklm(self, file_path: Path | list[Path], title: str = None) -> dict:
        """Upload to NotebookLM"""
        print("")
        print("="*70)
        print("⬆️  Uploading to NotebookLM")
        print("="*70)

        # Detect which NotebookLM CLI to use (notebooklm preferred, nlm as fallback)
        backend = self.detect_notebooklm_backend()
        if backend is None:
            return {
                "success": False,
                "error": (
                    "No NotebookLM CLI found. Install the native 'notebooklm' CLI "
                    "or 'nlm' (https://github.com/tmc/nlm) and make sure it is on PATH."
                ),
            }
        print(f"🔧 NotebookLM backend: {backend}")

        # Handle a list of files (the split chunks)
        if isinstance(file_path, list):
            print(f"📦 Detected {len(file_path)} file chunks")

            # Use the first file to determine the title
            first_file = file_path[0]
            if not title:
                title = first_file.stem.replace('_part1', '').replace('_', ' ')
                # Clean up the filename
                title = re.sub(r'\[.*?\]', '', title)
                title = re.sub(r'\(.*?\)', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 50:
                    title = title[:50] + "..."

            # Create the notebook
            print(f"📚 Creating notebook: {title}")
            notebook_id, error = self._nb_create(backend, title)
            if notebook_id is None:
                return {"success": False, "error": error}
            print(f"✅ Notebook created (ID: {notebook_id[:8]}...)")

            # Set the context (no-op for nlm)
            print(f"🎯 Setting the notebook context...")
            self._nb_use(backend, notebook_id)

            # Upload all chunks
            source_ids = []
            uploaded = 0
            for i, chunk_file in enumerate(file_path, 1):
                print(f"📄 Uploading chunk {i}/{len(file_path)}: {chunk_file.name}")
                source_id, error = self._nb_add_source(backend, notebook_id, chunk_file)
                if error is not None:
                    print(f"⚠️  Chunk {i} upload failed: {error}")
                    continue
                uploaded += 1
                if source_id:
                    source_ids.append(source_id)
                    print(f"   ✅ Success (ID: {source_id[:8]}...)")
                else:
                    print(f"   ✅ Success")

            return {
                "success": uploaded > 0,
                "notebook_id": notebook_id,
                "source_ids": source_ids,
                "uploaded": uploaded,
                "title": title,
                "chunks": len(file_path)
            }

        # Single-file upload
        # Determine the title
        if not title:
            title = file_path.stem.replace('_', ' ')
            # Clean up the filename
            title = re.sub(r'\[.*?\]', '', title)
            title = re.sub(r'\(.*?\)', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            # Truncate an overly long title
            if len(title) > 50:
                title = title[:50] + "..."

        # Create the notebook
        print(f"📚 Creating notebook: {title}")
        notebook_id, error = self._nb_create(backend, title)
        if notebook_id is None:
            return {"success": False, "error": error}
        print(f"✅ Notebook created (ID: {notebook_id[:8]}...)")

        # Set the context (no-op for nlm)
        print(f"🎯 Setting the notebook context...")
        self._nb_use(backend, notebook_id)

        # Upload the file
        print(f"📄 Uploading file...")
        source_id, error = self._nb_add_source(backend, notebook_id, file_path)
        if error is not None:
            return {"success": False, "error": error}

        if source_id:
            print(f"✅ Upload successful (ID: {source_id[:8]}...)")
        else:
            print(f"✅ Upload successful")

        return {
            "success": True,
            "notebook_id": notebook_id,
            "source_id": source_id,
            "title": title
        }


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Z-Library fully automated download and upload to NotebookLM")
        print("")
        print("Usage: python3 scripts/upload.py <Z-Library URL>")
        sys.exit(1)

    url = sys.argv[1]
    uploader = ZLibraryAutoUploader()

    # Download
    downloaded_file, file_format = await uploader.download_from_zlibrary(url)

    if not downloaded_file or not downloaded_file.exists():
        print("")
        print("="*70)
        print("❌ Download failed, cannot continue")
        print("="*70)
        sys.exit(1)

    # Convert
    final_file = uploader.convert_to_txt(downloaded_file, file_format)

    # Upload
    result = uploader.upload_to_notebooklm(final_file)

    print("")
    print("="*70)
    if result['success']:
        print("🎉 Full workflow complete!")
        print("="*70)
        print(f"📚 Title: {result['title']}")
        print(f"🆔 Notebook ID: {result['notebook_id']}")

        # Handle the result of a chunked upload
        if 'chunks' in result:
            print(f"📦 Chunks: {result['chunks']}")
            uploaded = result.get('uploaded', len(result['source_ids']))
            print(f"📄 Successfully uploaded {uploaded}/{result['chunks']} chunks")
            if result['source_ids']:
                print("   Source IDs:")
                for sid in result['source_ids']:
                    print(f"      - {sid}")
        elif result.get('source_id'):
            print(f"📄 Source ID: {result['source_id']}")

        print("")
        print("💡 Next steps:")
        backend = uploader.detect_notebooklm_backend()
        question = "What are the core ideas of this book?"
        if backend == "nlm":
            print(f"   nlm notebook query {result['notebook_id']} \"{question}\"")
        else:
            print(f"   notebooklm use {result['notebook_id']}")
            print(f"   notebooklm ask \"{question}\"")
    else:
        print("❌ Upload failed")
        print("="*70)
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
