# OpenReef Website Setup Guide

## Recommended: GitHub Pages + Jekyll

### Why This Approach?

Your documentation is already in markdown format and perfectly structured. GitHub Pages with Jekyll will:
- ✅ Host for free on GitHub
- ✅ Use your existing markdown files (no conversion needed!)
- ✅ Look professional (like IoRodeo's documentation)
- ✅ Auto-deploy when you update docs
- ✅ Support custom domain (openreef.org)
- ✅ Include search, navigation, mobile-friendly design

### Option 1: GitHub Pages (Recommended)

#### Step 1: Create GitHub Repository

```bash
# In your openreef directory
cd /Users/davidchilds/Documents/Repositories/openreef

# Initialize Git (if not already)
git init
git add .
git commit -m "Initial OpenReef documentation"

# Create repo on GitHub
# Go to: github.com/new
# Name: openreef
# Public repository
# Don't initialize with README (you already have one)

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/openreef.git
git branch -M main
git push -u origin main
```

#### Step 2: Configure Jekyll (Documentation Theme)

Create `_config.yml` in root:

```yaml
# Site settings
title: OpenReef
description: Open-source automated water quality testing for phosphate and nitrate
baseurl: "" # Leave empty for username.github.io/openreef
url: "https://YOUR_USERNAME.github.io"

# Theme - Just the Docs (great for documentation)
remote_theme: just-the-docs/just-the-docs

# Color scheme
color_scheme: dark

# Logo
logo: "/assets/images/openreef-logo.png"

# Search
search_enabled: true

# Navigation
nav_sort: case_insensitive

# Footer
footer_content: "Copyright &copy; 2025 OpenReef Project. Licensed under MIT."

# Aux links (top right)
aux_links:
  "OpenReef on GitHub":
    - "https://github.com/YOUR_USERNAME/openreef"

# Collections
collections:
  docs:
    permalink: "/:collection/:path/"
    output: true

# Defaults
defaults:
  - scope:
      path: ""
      type: "docs"
    values:
      layout: "default"
```

#### Step 3: Add Front Matter to Markdown Files

Add this to the top of each markdown file:

**Example: docs/introduction/overview.md**
```yaml
---
layout: default
title: Overview
parent: Introduction
nav_order: 1
---

# OpenReef Automated System
(rest of your existing content...)
```

**Example: docs/assays/phosphate.md**
```yaml
---
layout: default
title: Phosphate Assay
parent: Assay Protocols
nav_order: 1
---

# Phosphate Assay Protocol
(rest of your existing content...)
```

#### Step 4: Create Navigation Structure

Create `docs/index.md`:

```yaml
---
layout: default
title: Documentation
nav_order: 1
has_children: true
---

# OpenReef Documentation

Welcome to the OpenReef automated system documentation.
```

#### Step 5: Enable GitHub Pages

1. Go to your GitHub repo
2. **Settings → Pages**
3. **Source:** Deploy from a branch
4. **Branch:** main, /root
5. **Save**

**Your site will be live at:**
```
https://YOUR_USERNAME.github.io/openreef/
```

In 2-3 minutes!

### Option 2: Google Sites (Easiest but Limited)

#### Pros:
- Drag-and-drop editor
- No coding needed
- Free
- Google account integration

#### Cons:
- Must manually copy/paste markdown content
- Limited customization
- Not version controlled
- Less professional for technical docs

#### Setup:

1. **Go to:** https://sites.google.com
2. **Create new site**
3. **Choose template** (e.g., "Blank" or "Documentation")
4. **Add pages:**
   - Home
   - Introduction
   - Getting Started
   - Assays
   - Hardware
   - Firmware
   - Calibration
5. **Copy content** from your markdown files
6. **Format** using Google Sites editor
7. **Publish**

**Takes:** 1-2 hours to manually format everything

### Option 3: ReadTheDocs

Perfect for software documentation.

#### Setup:

1. **Push to GitHub** (same as Option 1)
2. **Go to:** https://readthedocs.org
3. **Import project** from GitHub
4. **Add `docs/conf.py`** (Sphinx config)
5. **Auto-builds** on every commit

**Great for:** Pure documentation sites with search, versions, PDF export

### Option 4: Netlify + Docusaurus (Modern)

Beautiful, modern documentation sites.

#### Setup:

```bash
# Install Docusaurus
npx create-docusaurus@latest openreef-website classic

# Copy your markdown files to docs/
cp -r docs/* openreef-website/docs/

# Deploy to Netlify
# 1. Push to GitHub
# 2. Connect to Netlify
# 3. Auto-deploy on push
```

**Result:** Modern, fast, beautiful documentation site

### Comparison Matrix

| Feature | GitHub Pages | Google Sites | ReadTheDocs | Netlify |
|---------|-------------|--------------|-------------|---------|
| **Setup Time** | 15 min | 1-2 hours | 20 min | 30 min |
| **Cost** | Free | Free | Free | Free tier |
| **Markdown Support** | ✅ Native | ❌ Manual | ✅ Native | ✅ Native |
| **Search** | ✅ Yes | ⚠️ Basic | ✅ Excellent | ✅ Yes |
| **Custom Domain** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Version Control** | ✅ Git | ❌ No | ✅ Git | ✅ Git |
| **Auto Deploy** | ✅ Yes | ❌ Manual | ✅ Yes | ✅ Yes |
| **Mobile Friendly** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Tech Level** | Medium | Easy | Medium | Medium |

### My Recommendation

**For OpenReef: GitHub Pages + Just the Docs**

**Why:**
1. Your docs are already perfectly formatted
2. Free forever
3. Professional appearance
4. Easy to maintain (just edit markdown)
5. Integrated with your code repository
6. Similar to IoRodeo's documentation style

**Time to live site:** 15-20 minutes

### Quick Start Script

I can create an automated setup script for you:

```bash
#!/bin/bash
# setup-website.sh

# Add Jekyll config
cat > _config.yml << 'EOF'
title: OpenReef
remote_theme: just-the-docs/just-the-docs
search_enabled: true
EOF

# Add front matter to all docs
find docs -name "*.md" -exec sed -i '' '1i\
---\
layout: default\
---\
' {} \;

# Initialize Git
git add .
git commit -m "Setup Jekyll for GitHub Pages"
git push

echo "Website will be live at https://YOUR_USERNAME.github.io/openreef/"
echo "Enable Pages in repo Settings → Pages"
```

### Example Sites Using This Stack

**Similar projects:**
- IoRodeo Open Colorimeter docs
- Adafruit Learning System
- Arduino documentation
- Raspberry Pi documentation

### Next Steps

1. **Choose your approach** (I recommend GitHub Pages)
2. **Follow setup steps** above
3. **Push to GitHub**
4. **Enable Pages**
5. **Share link!**

Total time: **15-20 minutes** for GitHub Pages

### Custom Domain (Optional)

Once your site is live, you can add a custom domain:

1. **Buy domain:** openreef.org (~$12/year)
2. **Add to GitHub Pages:**
   - Settings → Pages → Custom domain
   - Enter: openreef.org
3. **Configure DNS:**
   - Add CNAME record pointing to: YOUR_USERNAME.github.io
4. **Wait 24 hours** for DNS propagation

**Your site:** https://openreef.org

### Support

**GitHub Pages Docs:**
https://docs.github.com/en/pages

**Just the Docs Theme:**
https://just-the-docs.github.io/just-the-docs/

**Need help?** Let me know which option you choose and I can create the specific config files!
