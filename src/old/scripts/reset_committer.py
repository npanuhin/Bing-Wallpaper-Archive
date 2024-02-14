print(commit.author_name, commit.committer_name, commit.author_name.decode('utf-8') == 'GitHub Actions' and commit.author_name != commit.committer_name)

if commit.author_name.decode('utf-8') == 'GitHub Actions' and commit.author_name != commit.committer_name:
    print(f'Commit {commit.id} has different author and committer: {commit.author_name} != {commit.committer_name}')
    commit.committer_name = commit.author_name
    commit.committer_email = commit.author_email
    commit.committer_date = commit.author_date


# def handle(commit):
#     'Reset the timezone of all commits.'
#     date_str = commit.author_date.decode('utf-8')
#     [seconds, timezone] = date_str.split()
#     new_date = f'{seconds} +0000'
#     commit.author_date = new_date.encode('utf-8')


# handle(commit)
