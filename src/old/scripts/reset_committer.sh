git filter-repo --commit-callback "$(cat src/scripts/reset_committer.py)"
git remote add origin "git@github.com:npanuhin/Bing-Wallpaper-Archive.git"
git fetch origin
git branch --set-upstream-to=origin/master master
