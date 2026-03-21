# AI Generated
import subprocess
from datetime import datetime, timedelta

REGIONS = [
    'pt-BR', 'en-CA', 'fr-CA', 'fr-FR', 'de-DE', 'en-IN',
    'it-IT', 'ja-JP', 'zh-CN', 'es-ES', 'en-GB', 'en-US', 'ROW'
]

TARGET_AUTHOR = 'GitHub Actions <41898282+github-actions[bot]@users.noreply.github.com>'
TARGET_SUBJECT = 'Archive update'
COMMIT_COUNT = 1000
SINCE_DATE = '2026-01-01T00:00:00Z'


class RegionUpdateTracker:
    def __init__(self, regions):
        self.regions = regions
        self.possible_hours = {region: set(range(24)) for region in regions}
        self.runs = []

    def add_run(self, time_str, updated_regions):
        time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        self.runs.append((time_obj, updated_regions))

    def process_runs(self):
        if not self.runs:
            print('No runs to process.')
            return

        self.runs.sort(key=lambda x: x[0])
        last_run_time = self.runs[0][0]

        for current_time, updated_regions in self.runs[1:]:
            crossed_hours = set()
            t = last_run_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

            while t <= current_time:
                crossed_hours.add(t.hour)
                t += timedelta(hours=1)

            if crossed_hours:
                for region in self.regions:
                    if region in updated_regions:
                        self.possible_hours[region] &= crossed_hours
                    else:
                        self.possible_hours[region] -= crossed_hours

            last_run_time = current_time

    def print_results(self):
        print('\n--- Analysis Results ---')
        for region, hours in self.possible_hours.items():
            if len(hours) == 1:
                print(f'[OK] {region.ljust(6)}: Exactly updates at {list(hours)[0]:02d}:00')
            elif len(hours) > 1:
                print(f'[?]  {region.ljust(6)}: Needs more data. Possible hours: {sorted(list(hours))}')
            else:
                print(f'[X]  {region.ljust(6)}: Hypothesis error. No options left.')
        print('------------------------\n')


def get_git_data():
    cmd = [
        'git', 'log', '--name-only', '--date=iso-strict',
        f'--since={SINCE_DATE}',
        '--pretty=format:Commit: %h | Date: %cd | Author: %an <%ae> | Subject: %s',
        '-n', str(COMMIT_COUNT)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def parse_git_log(log_output):
    runs = []
    current_date = None
    current_regions = set()
    is_valid_commit = False

    for line in log_output.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith('Commit:'):
            if is_valid_commit and current_date:
                runs.append((current_date, list(current_regions)))

            current_date = None
            current_regions = set()
            is_valid_commit = False

            parts = list(map(str.strip, line.split('|')))
            if len(parts) >= 4:
                date_str = parts[1].replace('Date:', '').strip()
                author_str = parts[2].replace('Author:', '').strip()
                subject_str = parts[3].replace('Subject:', '').strip()

                if author_str == TARGET_AUTHOR and subject_str.lower() == TARGET_SUBJECT.lower():
                    is_valid_commit = True
                    current_date = date_str

        elif is_valid_commit:
            if line.startswith('api/') and line.endswith('.json'):
                path_parts = line.split('/')
                if len(path_parts) == 3:
                    country = path_parts[1]
                    lang = path_parts[2].replace('.json', '')

                    if country == 'ROW':
                        current_regions.add('ROW')
                    else:
                        region = f'{lang}-{country}'
                        if region in REGIONS:
                            current_regions.add(region)

    if is_valid_commit and current_date:
        runs.append((current_date, list(current_regions)))

    return runs


if __name__ == '__main__':
    tracker = RegionUpdateTracker(REGIONS)

    try:
        log_output = get_git_data()
        parsed_runs = parse_git_log(log_output)

        if not parsed_runs:
            print('Warning: No valid commits found. Check git log output.')
        else:
            print(f'Found {len(parsed_runs)} relevant commits. Processing...')
            for date_str, regions in parsed_runs:
                tracker.add_run(date_str, regions)

            tracker.process_runs()
            tracker.print_results()

    except subprocess.CalledProcessError:
        print("Error: The 'git log' command failed. Make sure you run the script in the repository root.")
    except Exception as e:
        print(f'Unknown error: {e}')
