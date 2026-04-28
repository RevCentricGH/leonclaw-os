---
name: google-drive
description: Manage Google Drive and Google Docs from Claude Code. Use for any Drive operation (list, search, read, download, upload, audit) OR any Docs operation (read, edit, append, find-replace, create, tabs). Triggers on: "read the doc", "update the doc", "append to", "find and replace", "create a new doc", Google Doc by name or ID, Drive files, folders, upload, search Drive, knowledge base. NOT for Google Slides operations — use google-slides for any presentation or deck work.
allowed-tools: Bash(CLAUDECLAW_DIR=* ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py *), Bash(CLAUDECLAW_DIR=* ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py *)
---

# Google Drive + Docs Skill

## Environment

Every command MUST use this prefix:

```
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel)
```

Token paths:
- Docs: `~/.config/gdocs/token.json`
- Drive: `~/.config/gdrive/token.json`
- Credentials (shared): `~/.config/gmail/credentials.json`

---

## Google Docs CLI (gdocs.py)

### Read a document

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py read <doc_id>
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py read <doc_id> --json
```

### Get document metadata

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py info <doc_id>
```

### Append / find-replace / overwrite

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py append <doc_id> "Text"
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py replace <doc_id> "old" "new"
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py overwrite <doc_id> "Full content"
```

### Create a new doc

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py create "Title"
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdocs/gdocs.py create "Title" --folder <folder_id>
```

---

## Google Docs Tabs API (Raw REST — required for all tab operations)

The Python client library does NOT support tab operations. Use raw REST with a refreshed token.

### Auth boilerplate (required for all raw REST calls)

```python
import sys, requests
sys.path.insert(0, os.path.expanduser('~/.config/gdocs'))
import gdocs
from google.auth.transport.requests import Request as GoogleRequest

service = gdocs.get_service()
creds = service._http.credentials
creds.refresh(GoogleRequest())
token = creds.token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
BASE = "https://docs.googleapis.com/v1/documents/{doc_id}"
```

### Read doc with tabs (ALWAYS use this when doc may have tabs)

```python
resp = requests.get(f"{BASE}?includeTabsContent=true", headers=headers)
doc = resp.json()
tabs = doc.get('tabs', [])
for t in tabs:
    props = t.get('tabProperties', {})
    print(props.get('tabId'), props.get('title'))
```

### Create a new tab

**IMPORTANT: The correct method is `addDocumentTab`, NOT `createTab`.**

```python
body = {"requests": [{"addDocumentTab": {"tabProperties": {"title": "Tab Name", "index": 0}}}]}
resp = requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
tab_id = resp.json()['replies'][0]['addDocumentTab']['tabProperties']['tabId']
```

### Insert text into a specific tab

```python
body = {"requests": [{"insertText": {"location": {"index": 1, "tabId": tab_id}, "text": "Content\n"}}]}
requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
```

### Apply heading styles to a specific tab

Always include `tabId` in the range when working in a specific tab.

```python
body = {"requests": [{
    "updateParagraphStyle": {
        "range": {"startIndex": start, "endIndex": end, "tabId": tab_id},
        "paragraphStyle": {"namedStyleType": "HEADING_1"},  # or HEADING_2, HEADING_3, NORMAL_TEXT
        "fields": "namedStyleType"
    }
}]}
requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
```

### Delete content range in a specific tab

```python
body = {"requests": [{"deleteContentRange": {"range": {"startIndex": start, "endIndex": end, "tabId": tab_id}}}]}
requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
```

### Delete a tab

```python
body = {"requests": [{"deleteTab": {"tabId": tab_id}}]}
requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
```

### Update tab title

```python
body = {"requests": [{"updateDocumentTabProperties": {
    "tabProperties": {"tabId": tab_id, "title": "New Title"},
    "fields": "title"
}}]}
requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
```

### Full workflow: Create tab + populate + format

```python
# 1. Create tab
body = {"requests": [{"addDocumentTab": {"tabProperties": {"title": "Campaign Status", "index": 0}}}]}
resp = requests.post(f"{BASE}:batchUpdate", headers=headers, json=body)
tab_id = resp.json()['replies'][0]['addDocumentTab']['tabProperties']['tabId']

# 2. Insert content
content = "Section Title\n\nBody content here\n"
requests.post(f"{BASE}:batchUpdate", headers=headers, json={"requests": [
    {"insertText": {"location": {"index": 1, "tabId": tab_id}, "text": content}}
]})

# 3. Re-read to get fresh indices
doc = requests.get(f"{BASE}?includeTabsContent=true", headers=headers).json()
tab_content = next(t['documentTab']['body']['content'] for t in doc['tabs'] if t['tabProperties']['tabId'] == tab_id)

# 4. Apply heading styles
style_requests = []
for elem in tab_content:
    if 'paragraph' in elem:
        text = ''.join(r.get('textRun', {}).get('content', '') for r in elem['paragraph']['elements'])
        if text.strip() == 'Section Title':
            style_requests.append({"updateParagraphStyle": {
                "range": {"startIndex": elem['startIndex'], "endIndex": elem['endIndex'], "tabId": tab_id},
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "fields": "namedStyleType"
            }})
if style_requests:
    requests.post(f"{BASE}:batchUpdate", headers=headers, json={"requests": style_requests})
```

---

## Docs Formatting Rules

- `replace` uses `replaceAllText` — matches must be exact including Unicode (curly quotes, em dashes, ellipses)
- For Unicode-safe matching, inspect exact chars with `repr(text)` before targeting
- `overwrite` loses all formatting — avoid for docs with headings/structure
- For partial rewrites: use `deleteContentRange` + `insertText` (bottom-to-top order to preserve indices)
- After any insert, always re-read the doc for fresh indices before subsequent range operations
- `replaceAllText` does NOT support empty string replacement — use range delete instead
- Doc IDs are in the URL: `docs.google.com/document/d/<DOC_ID>/edit`
- Tab IDs look like `t.abc123xyz`
- When doing multiple range operations in one batchUpdate, order bottom-to-top to avoid index shift

**Verify formatting after insert:**
- `namedStyleType` — NORMAL_TEXT for body, HEADING_1/2/3 for headers
- `bold`, `foregroundColor`, `backgroundColor` — should be None/default for body copy

---

## Complex Editing Patterns (Multi-pass approach)

For complex edits (content restructuring + formatting), use sequential passes. Each pass avoids the index-shift problems that come from mixing insert/delete with style ops.

### The 5-pass model

**Pass 1 — Deletions only** (single batchUpdate, bottom-to-top order)
- Multiple deletes in one batchUpdate are applied sequentially
- Order bottom-to-top (highest startIndex first) so earlier deletes don't shift indices of later ones
- Everything before the deleted range is unaffected; everything after shifts down by `(endIndex - startIndex)`

**Pass 2 — replaceAllText for unique substrings**
- Re-read after Pass 1 before running these
- Use after deleting duplicates — ensures the target string is now unique in the doc
- Safe to batch multiple replaceAllText ops together (they don't shift indices in a way that matters since they're search-based)
- Use a short unique fragment in `containsText.text` if the full string has tricky Unicode

**Pass 3 — Range-based paragraph rewrites** (for long/Unicode-heavy text)
- Re-read after Pass 2 for fresh indices
- To replace a paragraph's content while keeping its paragraph boundary:
  - `deleteContentRange` on `[si, ei-1]` (all content except trailing `\n`)
  - `insertText` at `si` with the new content
  - This preserves the paragraph's style (NORMAL_TEXT, HEADING_X, etc.)
- To insert a new paragraph after an existing one:
  - `insertText` at `ei-1` (before the trailing `\n`) with `"\n" + new_text`
  - The new paragraph inherits NORMAL_TEXT by default
- Re-read after each insert/delete before targeting anything that followed it

**Pass 4 — Paragraph style changes** (namedStyleType, heading level changes)
- Re-read after Pass 3
- `updateParagraphStyle` with `namedStyleType` to change heading levels
- Combine with `updateTextStyle` in the same batchUpdate to apply color/bold/underline
- These do NOT shift indices, so you can batch multiple style ops together

**Pass 5 — Global formatting** (bulk text style pass — run last)
- Re-read once, then scan all paragraphs and build a list of `updateTextStyle` and `updateParagraphStyle` requests
- Neither shifts indices, so batch all 50+ in one or two chunked calls
- Scan patterns:
  - Question prompts: `bold=True and italic=True and style=='NORMAL_TEXT'`
  - Branch labels: bold runs within bullet paragraphs matching known prefixes
  - NO/YES highlights: runs in title paragraphs where `run_text.strip() in ('NO', 'YES')`
  - Heading spacing: all H1/H2/H3 paragraphs in one pass
- Run-level targeting: `ParagraphElement` objects have their own `startIndex`/`endIndex` — use `run.get('startIndex')` directly

### Key rules

```python
# Chunk all batchUpdate calls to max 50 ops to avoid request size limits
def batch(reqs, label=""):
    for i in range(0, len(reqs), 50):
        chunk = reqs[i:i+50]
        r = requests.post(f"{BASE}:batchUpdate", headers=headers, json={"requests": chunk})
        if r.status_code != 200:
            print(f"ERROR {label}: {r.text[:300]}")

# ALWAYS read with includeTabsContent=true — plain read misses tab content
resp = requests.get(f"{BASE}?includeTabsContent=true", headers=headers)

# Paragraph elements have run-level indices — use them directly
for run in elem['paragraph']['elements']:
    rsi = run.get('startIndex')  # works — ParagraphElement has its own startIndex
    rei = run.get('endIndex')
    run_text = run.get('textRun', {}).get('content', '')
```

### When to use replaceAllText vs range-based

| Situation | Use |
|---|---|
| Short unique string, mostly ASCII | `replaceAllText` with full or partial match |
| Long paragraph with smart quotes/em dashes | Range delete + insert (avoids Unicode matching issues) |
| Duplicate strings exist (need to disambiguate first) | Delete duplicates in Pass 1, then `replaceAllText` in Pass 2 |
| Inserting a new paragraph after an existing one | `insertText` at `ei-1` with `"\n" + text` |
| Replacing paragraph content, keeping its style | Delete `[si, ei-1]`, insert at `si` |

---

## Google Drive CLI (gdrive.py)

### List files (most recently modified first)

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py list
```

Returns JSON array. Each entry has: `id`, `name`, `type`, `size`, `modified`, `modified_date`, `owner`.

### List files in a specific folder

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py list --folder <folder_id>
```

### Filter by type

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py list --type docs
```

Types: `docs`, `sheets`, `slides`, `folders`, `pdf`

### Search files (full-text content + name search)

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py search "revenue playbook"
```

### Read file content

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py read <file_id>
```

- Google Docs exported as plain text, Sheets as CSV
- Binary files (PDF, images): use `download` instead
- Truncated at 50k chars by default; use `--max-chars` to adjust

### Get file metadata

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py info <file_id>
```

### Show folder tree

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py tree
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py tree --folder-id <folder_id> --depth 2
```

### Download a file

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py download <file_id>
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py download <file_id> --output /tmp/report.csv
```

### Upload a file

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py upload /path/to/file.pdf
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py upload /path/to/file.pdf --name "Q1 Report.pdf" --folder <folder_id>
```

### Audit Drive (count files and total size)

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py audit
```

### Re-authenticate

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.config/gdrive/gdrive.py auth
```

---

## Shared Drive Operations (Raw Python — required for delete/move)

The gdrive.py CLI does NOT pass `supportsAllDrives=True`. Any delete or move on a Shared Drive file will return 404 unless you use raw Python with this flag.

### Auth boilerplate

```python
import sys
sys.path.insert(0, os.path.expanduser('~/.config/gdocs'))
import gdocs
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

service = gdocs.get_service()
creds = service._http.credentials
creds.refresh(GoogleRequest())
drive_service = build('drive', 'v3', credentials=creds)
```

### Delete a file from a Shared Drive

```python
# ALWAYS use supportsAllDrives=True — without it you get 404 on Shared Drive files
drive_service.files().delete(
    fileId='<file_id>',
    supportsAllDrives=True
).execute()
```

### Move a file between folders in a Shared Drive

```python
file = drive_service.files().get(fileId='<file_id>', fields='parents', supportsAllDrives=True).execute()
drive_service.files().update(
    fileId='<file_id>',
    addParents='<new_folder_id>',
    removeParents=','.join(file['parents']),
    supportsAllDrives=True,
    fields='id, parents'
).execute()
```

### Create a file in a Shared Drive folder

```python
metadata = {'name': 'My File', 'parents': ['<folder_id>']}
drive_service.files().create(
    body=metadata,
    supportsAllDrives=True,
    fields='id'
).execute()
```

---

## Key Folder / Doc IDs

Add your frequently used Drive folder and doc IDs here for quick reference:

<!-- Example:
- My Shared Drive root: `<folder_id>`
- Projects folder: `<folder_id>`
- Company Roadmap doc: `<doc_id>`
-->

Doc IDs are in the URL: `docs.google.com/document/d/<DOC_ID>/edit`
Folder IDs are in the URL: `drive.google.com/drive/folders/<FOLDER_ID>`
