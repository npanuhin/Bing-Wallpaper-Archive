clear
set FILTER_BRANCH_SQUELCH_WARNING=1
git filter-branch -f --commit-filter '
    if [[ $(git show -s --format=%an "$GIT_COMMIT") == "GitHub Actions" && $(git show -s --format=%ae "$GIT_COMMIT") == $(git show -s --format=%ce "$GIT_COMMIT") ]];
    then
        echo "$(git show -s --format=%an "$GIT_COMMIT")";
        GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME";
        GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL";
        GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE";
    fi
    git commit-tree "$@";' HEAD
