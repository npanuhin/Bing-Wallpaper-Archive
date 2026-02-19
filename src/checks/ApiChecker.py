import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Iterable, List

sys.path.append('../')
from Region import REGIONS, Region
from structures import ApiEntry
from system_utils import mkpath


@dataclass
class CheckResult:
    region: str
    date: str
    field: str
    value: str
    anomaly: str


class ApiChecker:
    def __init__(self):
        self.item_checks = []
        self.api_checks = []
        self.field_checks = []
        self.results = []
        self.report_file = mkpath(os.path.dirname(__file__), 'anomalies.txt')

    def check_item(self, func: Callable[[ApiEntry, Region], Iterable[str]]):
        self.item_checks.append(func)
        return func

    def check_api(self, func: Callable[[List[ApiEntry], Region], Iterable[str]]):
        self.api_checks.append(func)
        return func

    def check_field(self, *fields):
        def decorator(func: Callable[..., Iterable[str]]):
            if not fields:
                raise ValueError(f'No fields specified for {func.__name__}')
            self.field_checks.append((func, list(fields)))
            return func

        return decorator

    def add_anomaly(self, region: Region, date: Any, field: str, value: str, anomaly_text: str):
        self.results.append(CheckResult(
            region=str(region),
            date=str(date),
            field=field,
            value=value,
            anomaly=anomaly_text
        ))

    def run(self):
        for region in REGIONS:
            print(f'Checking {region}...')
            api = region.read_api()

            for check_func in self.api_checks:
                for anomaly in check_func(api, region):
                    self.add_anomaly(region, 'N/A', 'N/A', 'N/A', anomaly)

            for item in api:
                for check_func in self.item_checks:
                    for anomaly in check_func(item, region):
                        self.add_anomaly(region, item.date, 'N/A', 'N/A', anomaly)

                for check_func, fields in self.field_checks:
                    for field in fields:
                        value = getattr(item, field)
                        if value and isinstance(value, str):
                            for anomaly in check_func(value, region):
                                self.add_anomaly(region, item.date, field, value, anomaly)

        self.write_report()

        if not self.results:
            print('\nAll checks passed!')
            return True

        print('\nSome checks failed')
        sys.exit(1)

    def write_report(self):
        if not self.results:
            if os.path.exists(self.report_file):
                os.remove(self.report_file)
            return

        grouped = {}
        for result in self.results:
            key = (result.region, result.date, result.field, result.value)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result.anomaly)

        total_anomalies_count = 0
        anomalies_by_type = {}

        with open(self.report_file, 'w', encoding='utf-8') as output_file:
            for (region, date, field, value), anomalies in grouped.items():
                output_file.write(f'Region: {region}, Date: {date}, Field: {field}\n')
                output_file.write(f'Value: {value}\n')
                output_file.write('Anomalies:\n')
                for anomaly in sorted(anomalies):
                    output_file.write(f'  {anomaly}\n')
                    total_anomalies_count += 1
                    anomaly_type = anomaly.split(':', 1)[0].strip() if ':' in anomaly else anomaly
                    anomalies_by_type[anomaly_type] = anomalies_by_type.get(anomaly_type, 0) + 1
                output_file.write('-' * 40 + '\n')

        print(f'\nChecks complete. Results saved to {self.report_file}')
        print(f'Total entries with anomalies: {len(grouped)}')
        print(f'Total anomalies: {total_anomalies_count}')
        print('Anomalies by type:')
        for type_name, count in sorted(anomalies_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f'  {type_name}: {count}')


checker = ApiChecker()
