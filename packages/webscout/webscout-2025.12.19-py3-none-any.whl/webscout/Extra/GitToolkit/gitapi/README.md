# 🚀 GitAPI: GitHub Data Extraction Module

## Overview

GitAPI is a powerful, lightweight GitHub data extraction module within the Webscout Python package. It provides comprehensive tools for retrieving GitHub repository, user, organization, gist, and trending data without requiring authentication for public data access.

## ✨ Features

- **Repository Operations**
  - Repository metadata, README, license, topics
  - Commit history and comparison
  - Pull requests and issues
  - Releases, branches, and tags
  - Contributors, stargazers, watchers, forks
  - GitHub Actions workflows
  - Repository events and statistics

- **User Operations**
  - Profile information and social accounts
  - Repository listing and starred repos
  - Follower/Following data
  - Organizations and packages
  - Events, gists, and SSH/GPG keys

- **Search Operations** (NEW)
  - Search repositories by query, language, stars
  - Search users by name, location, followers
  - Search topics, commits, issues, and labels

- **Gist Operations** (NEW)
  - Get gist by ID with full content
  - List public gists
  - Gist commits, forks, and revisions
  - Gist comments

- **Organization Operations** (NEW)
  - Organization details and metadata
  - Organization repositories
  - Public members and events

- **Trending** (NEW)
  - Trending repositories by language/time
  - Trending developers

- **Error Handling**
  - Rate limit detection
  - Resource not found handling
  - Request retry mechanism
  - Custom error types

## 📦 Installation

Install as part of the Webscout package:

```bash
pip install webscout
```

## 💡 Quick Examples

### Repository Operations

```python
from webscout.Extra.GitToolkit.gitapi import Repository

repo = Repository("OE-LUCIFER", "Webscout")

# Get basic info
info = repo.get_info()
print(f"Stars: {info['stargazers_count']}")

# Get README
readme = repo.get_readme()
print(f"README: {readme['name']}")

# Get topics
topics = repo.get_topics()
print(f"Topics: {topics['names']}")

# Compare branches
diff = repo.compare("main", "dev")
print(f"Commits ahead: {diff['ahead_by']}")
```

### User Operations

```python
from webscout.Extra.GitToolkit.gitapi import User

user = User("OE-LUCIFER")

# Get profile
profile = user.get_profile()
print(f"Followers: {profile['followers']}")

# Get social accounts
socials = user.get_social_accounts()
for account in socials:
    print(f"{account['provider']}: {account['url']}")
```

### Search Operations

```python
from webscout.Extra.GitToolkit.gitapi import GitSearch

search = GitSearch()

# Search repositories
repos = search.search_repositories("webscout language:python stars:>100")
print(f"Found {repos['total_count']} repos")

# Search users
users = search.search_users("location:india followers:>1000")
print(f"Found {users['total_count']} users")

# Search topics
topics = search.search_topics("machine-learning")
for topic in topics['items'][:5]:
    print(f"Topic: {topic['name']}")
```

### Gist Operations

```python
from webscout.Extra.GitToolkit.gitapi import Gist

gist = Gist()

# List public gists
public = gist.list_public(per_page=5)
for g in public:
    print(f"Gist: {g['id']} - {g['description']}")

# Get specific gist
data = gist.get("gist_id_here")
print(f"Files: {list(data['files'].keys())}")
```

### Organization Operations

```python
from webscout.Extra.GitToolkit.gitapi import Organization

org = Organization("microsoft")

# Get org info
info = org.get_info()
print(f"Organization: {info['name']}")
print(f"Public repos: {info['public_repos']}")

# Get org repos
repos = org.get_repos(per_page=10)
for repo in repos:
    print(f"Repo: {repo['name']}")
```

### Trending

```python
from webscout.Extra.GitToolkit.gitapi import Trending

trending = Trending()

# Get trending repos
repos = trending.get_repositories(language="python", since="weekly")
for repo in repos[:5]:
    print(f"{repo['full_name']} - ⭐ {repo['stars']}")

# Get trending developers
devs = trending.get_developers(language="python")
for dev in devs[:5]:
    print(f"{dev['username']} - {dev.get('name', 'N/A')}")
```

## 🔧 Available Classes

### Repository Class
- `get_info()`, `get_readme()`, `get_license()`, `get_topics()`
- `get_commits()`, `get_commit()`, `compare()`
- `get_pull_requests()`, `get_issues()`, `get_labels()`, `get_milestones()`
- `get_releases()`, `get_branches()`, `get_tags()`
- `get_contributors()`, `get_stargazers()`, `get_watchers()`, `get_forks()`
- `get_contents()`, `get_languages()`, `get_events()`
- `get_workflows()`, `get_workflow_runs()`, `get_deployments()`
- `get_community_profile()`, `get_code_frequency()`, `get_commit_activity()`

### User Class
- `get_profile()`, `get_repositories()`, `get_starred()`
- `get_followers()`, `get_following()`
- `get_gists()`, `get_organizations()`
- `get_public_events()`, `get_received_events()`
- `get_keys()`, `get_gpg_keys()`
- `get_social_accounts()`, `get_packages()`

### GitSearch Class
- `search_repositories()` - Search repos by query
- `search_users()` - Search users
- `search_topics()` - Search topics
- `search_commits()` - Search commits
- `search_issues()` - Search issues/PRs
- `search_labels()` - Search labels

### Gist Class
- `get()` - Get gist by ID
- `list_public()` - List public gists
- `list_for_user()` - List user's gists
- `get_commits()`, `get_forks()`, `get_revision()`, `get_comments()`

### Organization Class
- `get_info()` - Organization details
- `get_repos()` - Organization repositories
- `get_public_members()` - Public members
- `get_events()` - Organization events

### Trending Class
- `get_repositories()` - Trending repos
- `get_developers()` - Trending developers

## ⚠️ Error Handling

```python
from webscout.Extra.GitToolkit.gitapi import Repository, NotFoundError, RateLimitError

try:
    repo = Repository("nonexistent", "repo")
    info = repo.get_info()
except NotFoundError:
    print("Repository not found")
except RateLimitError:
    print("Rate limit exceeded, try again later")
```

Exception types:
- `GitError`: Base exception for all GitHub API errors
- `RateLimitError`: Raised when hitting API rate limits
- `NotFoundError`: Raised when resource is not found
- `RequestError`: Raised for general request errors
