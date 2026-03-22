# AI Generated
import subprocess
import json
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Tuple

REGIONS = [
    'pt-BR', 'en-CA', 'fr-CA', 'fr-FR', 'de-DE', 'en-IN',
    'it-IT', 'ja-JP', 'zh-CN', 'es-ES', 'en-GB', 'en-US',
    'ROW'
]

COMMIT_AUTHOR = 'GitHub Actions <41898282+github-actions[bot]@users.noreply.github.com>'
COMMIT_NAME = 'Archive update'
LIMIT_COUNT = 500
WORKFLOW_NAME = 'Archive update'
SINCE_DATE = '2026-01-01T00:00:00Z'


class RegionUpdateTracker:
    def __init__(self, regions: List[str]) -> None:
        self.regions = regions
        self.possible_hours = {region: set(range(24)) for region in regions}
        self.runs = []

    def load_merged_runs(self, merged_runs: List[Tuple[datetime, List[str], datetime]]) -> None:
        self.runs = merged_runs

    def process_runs(self) -> None:
        if not self.runs:
            print('Not enough data to process intervals.')
            return

        for run_info in self.runs:
            curr_time, updated_regions, last_time = run_info

            if (curr_time - last_time).total_seconds() < 1:
                continue

            spanned_hours = set()
            t = last_time
            if t.minute > 0 or t.second > 0 or t.microsecond > 0:
                t = (t + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            else:
                t = t.replace(minute=0, second=0, microsecond=0)

            while t <= curr_time:
                spanned_hours.add(t.hour)
                t += timedelta(hours=1)

            if not spanned_hours:
                spanned_hours.add(curr_time.hour)

            changes = []
            for region in self.regions:
                before = self.possible_hours[region].copy()
                is_hit = region in updated_regions

                if is_hit:
                    new_val = self.possible_hours[region] & spanned_hours
                else:
                    new_val = self.possible_hours[region] - spanned_hours

                if not new_val and self.possible_hours[region]:
                    continue

                self.possible_hours[region] = new_val
                if before != self.possible_hours[region]:
                    changes.append(region)

            if changes:
                status = f"Updated: {', '.join(updated_regions)}" if updated_regions else 'No updates'
                print(f"[DEBUG] {curr_time.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
                      f"{status} | "
                      f"Interval: ({last_time.strftime('%H:%M:%S')}, {curr_time.strftime('%H:%M:%S')}] | "
                      f"Spanned: {sorted(list(spanned_hours))}")

    def print_results(self) -> None:
        print('\n--- Analysis Results ---')
        for region, hours in self.possible_hours.items():
            if len(hours) == 1:
                h = list(hours)[0]
                print(f'[OK] {region.ljust(6)}: {h:02d}:00 UTC')
            elif 1 < len(hours) < 24:
                print(f'[?]  {region.ljust(6)}: Possible hours: {sorted(list(hours))}')
            elif len(hours) == 24:
                print(f'[-]  {region.ljust(6)}: No updates captured yet.')
            else:
                print(f'[X]  {region.ljust(6)}: Logic error (Check debug logs for contradictions)')
        print('------------------------\n')


def get_git_commits() -> List[Tuple[datetime, List[str], str]]:
    cmd = [
        'git', 'log', '--name-only', '--date=iso-strict',
        f'--since={SINCE_DATE}',
        '--pretty=format:Commit: %h | Date: %cd | Author: %an <%ae> | Subject: %s',
        '-n', str(LIMIT_COUNT)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception as e:
        print(f'Error executing git: {e}. Make sure you are in the repository root and git is installed.')
        sys.exit(1)

    commits = []
    current_date = None
    current_regions = set()
    current_hash = ''
    is_valid_commit = False

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith('Commit:'):
            if is_valid_commit and current_date:
                commits.append((current_date, list(current_regions), current_hash))

            current_date, current_regions, is_valid_commit, current_hash = None, set(), False, ''
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 4:
                h = parts[0].replace('Commit:', '').strip()
                author_str = parts[2].replace('Author:', '').strip()
                subject_str = parts[3].replace('Subject:', '').strip()
                if author_str == COMMIT_AUTHOR and subject_str.lower() == COMMIT_NAME.lower():
                    is_valid_commit = True
                    current_hash = h
                    dt = datetime.fromisoformat(parts[1].replace('Date:', '').strip())
                    current_date = dt.astimezone(timezone.utc).replace(microsecond=0)

        elif is_valid_commit and line.startswith('api/') and line.endswith('.json'):
            parts_path = line.split('/')
            if len(parts_path) == 3:
                country = parts_path[1]
                lang = parts_path[2].replace('.json', '')
                region = 'ROW' if country == 'ROW' else f'{lang}-{country}'
                if region in REGIONS:
                    current_regions.add(region)

    if is_valid_commit and current_date:
        commits.append((current_date, list(current_regions), current_hash))

    commits.sort(key=lambda x: x[0])
    return commits


def get_gh_actions_runs() -> List[datetime]:
    cmd = [
        'gh', 'run', 'list',
        '--workflow', WORKFLOW_NAME,
        '--json', 'createdAt',
        '--limit', str(LIMIT_COUNT)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        runs_data = json.loads(result.stdout)

        run_times = []
        since_dt = datetime.fromisoformat(SINCE_DATE.replace('Z', '+00:00'))
        for run in runs_data:
            t = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
            t = t.replace(microsecond=0)
            if t >= since_dt:
                run_times.append(t)

        run_times = sorted(list(set(run_times)))
        return run_times
    except Exception as e:
        print(f"Error fetching Actions: {e}. Make sure 'gh' CLI is installed and you ran 'gh auth login'.")
        sys.exit(1)


def merge_runs_and_commits(
    run_times: List[datetime],
    commits: List[Tuple[datetime, List[str], str]]
) -> List[Tuple[datetime, List[str], datetime]]:
    merged = []
    commit_idx = 0
    num_commits = len(commits)

    for i in range(1, len(run_times)):
        prev_time = run_times[i - 1]
        curr_time = run_times[i]
        updated_regions = set()
        matched_hashes = []

        while commit_idx < num_commits:
            commit_time = commits[commit_idx][0]
            if commit_time <= prev_time:
                commit_idx += 1
                continue
            if commit_time <= curr_time:
                updated_regions.update(commits[commit_idx][1])
                matched_hashes.append(commits[commit_idx][2])
                commit_idx += 1
            else:
                break

        print(f"[MATCH] Run {curr_time.strftime('%Y-%m-%d %H:%M:%S')} UTC -> "
              f"{len(matched_hashes)} commits: {', '.join(matched_hashes)}")
        merged.append((curr_time, list(updated_regions), prev_time))
    return merged


if __name__ == '__main__':
    tracker = RegionUpdateTracker(REGIONS)
    try:
        print('Fetching GitHub Actions runs (this may take a few seconds)...')
        run_times_list = get_gh_actions_runs()

        print('Fetching Git commits...')
        commits_list = get_git_commits()

        print(f'Fetched {len(run_times_list)} workflow runs and {len(commits_list)} commits. Matching...')

        merged_runs_list = merge_runs_and_commits(run_times_list, commits_list)
        tracker.load_merged_runs(merged_runs_list)

        tracker.process_runs()
        tracker.print_results()

    except Exception as e_main:
        print(f'Error: {e_main}')
