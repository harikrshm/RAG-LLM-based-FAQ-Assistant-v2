# Vercel Branch Configuration Guide

## How to Verify Which Branch Vercel is Deploying

### Step 1: Check Vercel Dashboard

1. Go to https://vercel.com and sign in
2. Select your project
3. Go to **Settings** → **Git**
4. Check the **Production Branch** setting
   - Should be set to `main` (or `master`)
   - This is the branch that deploys to production

### Step 2: Check Recent Deployments

1. In Vercel dashboard, go to **Deployments** tab
2. Look at the latest deployment
3. Check the **Git Commit** column
   - Click on the commit hash
   - Verify it matches your latest commit on `main` branch

### Step 3: Verify Branch in GitHub

1. Go to your GitHub repository
2. Check the `main` branch
3. Verify the latest commit matches what Vercel deployed

## How to Change Vercel Production Branch

If Vercel is deploying from the wrong branch:

1. Go to Vercel dashboard → Your project → **Settings** → **Git**
2. Under **Production Branch**, click **Edit**
3. Select `main` (or your desired branch)
4. Click **Save**
5. Vercel will redeploy from the new branch

## Current Repository Status

**Main Branch:** `main`
**Latest Commit on Main:** `c7d7240` (Add Node.js version via engines field)

**To verify locally:**
```bash
git checkout main
git pull origin main
git log --oneline -5
```

## Ensuring Main Has Latest Changes

If you've been working on a feature branch and want to ensure main is up to date:

```bash
# Check current branch
git branch

# Switch to main
git checkout main

# Pull latest from remote
git pull origin main

# Merge feature branch (if needed)
git merge chore-update-readme-u3X3p

# Push to main
git push origin main
```

## Troubleshooting

### Vercel Not Deploying from Main

1. **Check Git Integration:**
   - Vercel dashboard → Settings → Git
   - Verify repository is connected
   - Check if auto-deployments are enabled

2. **Check Branch Protection:**
   - GitHub → Repository → Settings → Branches
   - Ensure `main` branch doesn't have restrictions blocking Vercel

3. **Manual Deploy:**
   - Vercel dashboard → Deployments → **Redeploy**
   - Select the correct commit from `main` branch

### Vercel Deploying Wrong Branch

1. **Update Production Branch:**
   - Vercel dashboard → Settings → Git → Production Branch
   - Change to `main`

2. **Disable Auto-Deploy for Other Branches:**
   - Vercel dashboard → Settings → Git
   - Under **Ignored Build Step**, you can add conditions

## Quick Verification Commands

```bash
# Check what branch you're on
git branch

# Check latest commit on main
git log origin/main --oneline -1

# Check if local main matches remote
git fetch origin
git log main..origin/main --oneline
git log origin/main..main --oneline
```

## Current Configuration

- **Production Branch:** Should be `main`
- **Auto-Deploy:** Enabled (deploys on push to main)
- **Preview Deployments:** Enabled (deploys on PRs)

If you see deployments from other branches, they are likely preview deployments (which is normal for pull requests).

