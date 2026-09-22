---
name: ghost
description: Control Ghost CMS Admin via browser automation using the Claude Chrome Extension or browser subagent tools. Use this skill whenever the user wants to interact with their Ghost CMS publication — drafting new posts or pages, editing existing content, formatting articles with Markdown cards or Lexical rich text, configuring post settings (tags, excerpts, slugs, authors, featured images, SEO metadata, code injection), scheduling or publishing posts, managing newsletter delivery options (publish only vs publish and email), or auditing published articles. Triggers on any phrase involving Ghost CMS — "open Ghost admin", "check my drafts in Ghost", "create a new post in Ghost", "publish [title] on Ghost", "schedule post in Ghost", "update tags on Ghost", "add featured image in Ghost", "paste markdown into Ghost", "set excerpt in Ghost", "get ghost_id", or any variation where the goal involves Ghost. When in doubt, use this skill — don't try to replicate Ghost admin workflows manually.
---

# Ghost CMS Skill

This skill uses browser automation (Claude in Chrome or browser subagent) to control Ghost CMS Admin (typically at `https://<your-domain>/ghost/` or `https://<site>/ghost/#/site`). It handles five main workflows: navigating and filtering content, creating posts/pages, editing and safely inserting Markdown cards into Ghost's Lexical editor, configuring post metadata and media, and managing the publication/scheduling flow with newsletter delivery safeguards.

---

## Step 0: Always Start Here

Before doing anything else:
1. Call `tabs_context_mcp` to get a valid tab ID — every browser tool requires one.
2. Call `computer` (action: `screenshot`) to see the current state of the browser.
3. Decide whether to navigate or work from the current page.
4. If not already on Ghost Admin, navigate there:
   ```
   navigate(url: "https://<your-ghost-domain>/ghost/#/posts", tabId: <tab_id>)
   ```
5. Take a screenshot to confirm the page loaded.
   - **Authentication check**: If you see the Ghost sign-in screen (`/#/signin`), **stop immediately** and inform the user that they must log in manually. Do not attempt to input credentials or handle 2FA autonomously.
   - Once authenticated, Ghost displays the left navigation sidebar (`Posts`, `Pages`, `Tags`, `Members`, `Settings`).

---

## Finding and Opening Content (Posts & Pages)

Ghost lists posts in a table/grid view at `/#/posts` and pages at `/#/pages`.

1. **Navigate to the list**:
   - For posts: Click "Posts" in the sidebar or navigate to `/ghost/#/posts`.
   - For pages: Click "Pages" in the sidebar or navigate to `/ghost/#/pages`.
2. **Filter content**:
   - Use the top filter dropdowns:
     - **Status**: `All posts`, `Draft posts`, `Scheduled posts`, `Published posts`.
     - **Access / Tags / Authors**: Filter by specific tag or author if multiple articles share similar titles.
   - Alternatively, open Ghost's universal search with `computer` (action: `hotkey`, key: `Control+k` or `Meta+k`) or click the magnifying glass search bar. Type the title or slug to jump directly to the editor.
3. **Open the item**:
   - Screenshot to locate the row.
   - Use `find("<post title> row", tabId)` or click directly on the title link from the screenshot.
   - If multiple drafts exist with identical or similar titles, take a screenshot and ask the user for confirmation before proceeding.

---

## Action: Create a New Post or Page

1. From the Posts view, click the **"New post"** button (top right green button, or `+` next to Posts in sidebar). URL changes to `/#/editor/post`.
2. **Set Title**:
   - Screenshot to locate the title field.
   - Click the title area: `find("Post title textarea", tabId)`.
   - Type the title using `computer` (action: `type`, text: `<title>`).
   - Press Enter to move focus to the body block.

3. **Insert Content (Lexical Editor Best Practice)**:
   Ghost uses the Koenig editor built on Lexical. Raw text pasting into the rich-text block can cause inconsistent formatting or duplicate pastes.
   
   - **Method A: Markdown Card (Strongly Recommended for Structured / Exported Markdown)**:
     - In an empty paragraph block, type `/markdown` and press Enter, or click the `+` icon that appears on the left of an empty line and select **"Markdown"**.
     - A dedicated Markdown card appears with an embedded code editor.
     - Focus the Markdown card textarea.
     - Paste or type the canonical Markdown content.
     - *Advantages*: Preserves complex tables, footnotes, code fences, and links cleanly without Lexical re-parsing quirks.
   
   - **Method B: Rich Text / Lexical Native Blocks**:
     - Type or paste standard text into the default content area.
     - Use `/image`, `/callout`, `/html`, `/divider`, `/bookmark` for specialized media cards.

4. **Verify auto-save**:
   - Look at the top left/right corner: wait for the status indicator to change from "Saving..." to "Draft - Saved".

---

## Action: Edit / Update Existing Content (Safe Replacement)

> [!WARNING]
> Ghost's Lexical editor manages text in contenteditable nodes. Attempting to fill or blindly paste over a non-empty document can concatenate or append text rather than replace it, producing duplicate sections or mangled headings.

1. Open the existing post in the editor.
2. Screenshot to inspect current content blocks.
3. If replacing existing content:
   - If it is inside a **Markdown card**: Click the card, use `computer` (action: `hotkey`, key: `Control+a`), press `Backspace`, then paste the new Markdown.
   - If it is native Lexical rich text: Select all content or delete individual blocks intentionally before pasting fresh content.
4. **Audit headings and structure**:
   - Verify that primary headings (H2, H3) and evidence/closing sections appear exactly once and are not duplicated.

---

## Action: Post Settings Drawer (Metadata, Media & SEO)

Open the post settings panel by clicking the **cog / sidebar toggle icon** in the top right corner (`find("Settings toggle button", tabId)`).

A drawer slides in from the right with the following critical fields:

1. **Post URL (Slug)**:
   - Locate the "Post URL" input field.
   - Ensure the slug matches the canonical identifier (e.g. `aneurisma-aortico-abdominal`).
2. **Publish Date**:
   - Set current time or schedule for a specific date/time.
3. **Tags**:
   - Locate the Tags multi-select input.
   - Type tag names (e.g., `POCUS`, `Cardiovascular`, `Signos`) and press Enter to confirm each tag. Primary tag is the first one listed.
4. **Excerpt**:
   - Locate the "Excerpt" textarea.
   - Paste the short abstract/summary (typically 40–80 words). Ghost uses this for previews, newsletter summaries, and search snippets.
5. **Featured Image (Header image)**:
   - **Do NOT click the standard file picker button directly** (native OS file dialogs cannot be controlled via browser automation).
   - Use `file_upload` targeting the hidden `<input type="file">` element inside the image uploader zone with the absolute path to the local image.
   - Set image Alt Text and Caption if required.
6. **Meta data & Social Cards** (Under the "Meta data", "X card", "Facebook card" sub-sections):
   - Set custom SEO Title and Description if they differ from post title/excerpt.
   - Set Canonical URL if republishing or linking to an authoritative source.
7. **Code Injection** (Under "Code injection"):
   - Post header (`<head>`): Custom CSS, scripts, or meta tags.
   - Post footer: Custom embeds (e.g., interactive widgets or challenge links).
8. Close settings drawer: Click the cog icon again or click outside the drawer.

---

## Action: Publishing, Scheduling & Newsletter Safety

> [!CRITICAL]
> **Newsletter Safeguard**: Ghost instances with active email newsletters default to "Publish and email". Always check the delivery setting before confirming publication to prevent unwanted mass emails to subscribers.

1. **Initiate Publication**:
   - Click the **"Publish"** button in the top right corner. A modal flyout opens.
2. **Review Delivery Settings**:
   - Screenshot the publish modal.
   - Check the delivery target:
     - **Publish only (Web only)**: Select this if the content should only be live on the web without dispatching an email blast to members.
     - **Publish and email**: Only choose this if the user explicitly requested newsletter delivery.
3. **Set Schedule / Timing**:
   - Choose **"Right now"** for immediate release, or **"Schedule for later"** and specify date and time.
4. **Final Confirmation**:
   - Click **"Continue, final review"**.
   - Review the summary confirmation screen.
   - Click **"Publish post, right now"** (or "Schedule post").
5. **Post-publish dialog**:
   - Ghost shows a celebration modal with:
     - The public post URL (e.g., `https://<domain>/<slug>/`).
     - A "View post" link.
   - Copy or record this URL.

### Updating Already Published Posts:
- If the post is already published, the top right button displays **"Update"** instead of "Publish".
- Clicking "Update" saves changes immediately to the live post.

### Unpublishing / Reverting to Draft:
- Click the "Unpublish" or drop-down next to Update -> select **"Revert to draft"** -> confirm in modal.

---

## Action: Verification & Auditing

After drafting or publishing:
1. **Extract Ghost Post ID**:
   - Inspect the current editor URL: `https://<domain>/ghost/#/editor/post/<ghost_id>`.
   - The hex/alphanumeric string at the end is the internal `ghost_id` (crucial for indexing and local database synchronization).
2. **Use Preview Mode**:
   - Click the **"Preview"** button in the top bar.
   - Toggle between **Desktop**, **Mobile**, **Email**, and **Social card** views.
   - Take a screenshot to verify layout, image rendering, and typography.
3. **Verify Public Article**:
   - If published, open the public URL in a new tab or navigate there.
   - Verify featured image, title, headings, links, and embedded widgets render correctly.

---

## General Tips & Pitfalls

- **Lexical Koenig Cards**: When inside a Markdown card or HTML card, clicking outside the card blurs it and renders the preview. To edit again, click directly on the card.
- **Auto-save Delay**: Ghost auto-saves continuously, but network latency can cause delays. Always verify the top-bar indicator shows "Saved" before closing or navigating away.
- **Never trigger native OS dialogs**: Avoid clicking buttons that launch system file pickers; always use `file_upload` on the corresponding `<input type="file">`.
- **Keyboard Shortcuts in Ghost Admin**:
  - `Ctrl+S` / `Cmd+S`: Save draft / update post.
  - `Ctrl+Alt+P` / `Cmd+Option+P`: Open publish menu.
  - `Ctrl+K` / `Cmd+K`: Omni-search across all posts, pages, tags, and settings.
  - `/` at the start of a line: Open the Koenig block insertion menu.

---

## Reporting Back

After completing any Ghost action, report:
1. **Action performed**: (Created draft, updated content, configured metadata, scheduled, published).
2. **Post Title & Slug**: Exact title and URL slug.
3. **Ghost ID**: Internal post ID extracted from the editor URL (`/#/editor/post/<ghost_id>`).
4. **Publication Status**: `Draft`, `Scheduled` (with date/time), or `Published` (with live public URL).
5. **Newsletter Status**: Explicitly state whether the post was published web-only or dispatched via email.
6. **Visual confirmation**: Final screenshot showing the saved editor state or published post modal.
