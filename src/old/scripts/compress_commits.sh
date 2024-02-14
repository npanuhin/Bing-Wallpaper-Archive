#!/bin/bash

clear

# Get current branch name
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Get the commit list
commits=$(git log --oneline --pretty=format:"%H|%s|%an|%ae|%ad")

# Initialize variables to track next commit
next_commit_hash=""
next_commit_message=""

# Loop through the commits
while IFS='|' read -r commit_hash commit_message author_name author_email author_date; do

  if [ "$commit_message" = "Archive update" ] && [ "$next_commit_message" = "Archive update" ]; then
    echo "Squashing $commit_hash into $next_commit_hash"

    # Checkout the parent of the asked commit
    git -c advice.detachedHead=false checkout "$commit_hash"
    git checkout HEAD~

    # Merge the commit into it's parent, keeping the commit message of the parent
    git merge --squash "$commit_hash"
    git add .
    git add --update

    export GIT_COMMITTER_NAME="$author_name"
    export GIT_COMMITTER_EMAIL="$author_email"
    export GIT_COMMITTER_DATE="$author_date"
    git commit --amend --no-edit

    # Store the current commit
    newcommit=$(git rev-parse HEAD)

    # Rebase the starting branch onto the new commit
    echo "Checking out $BRANCH_NAME"
    git checkout "$BRANCH_NAME"
    echo "Rebasing"
    git rebase --committer-date-is-author-date -X theirs "$newcommit"

    break
  fi

  # Update nextious commit variables
  next_commit_hash=$commit_hash
  next_commit_message=$commit_message
done <<< "$commits"

