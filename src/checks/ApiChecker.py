import os
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Any, Callable, Iterable, TypeVar

sys.path.append('../')
from Region import REGIONS, Region
from structures import ApiEntry
from system_utils import mkpath

REPORT_FILE = mkpath(os.path.dirname(__file__), 'anomalies.txt')

T = TypeVar('T')
CheckFuncType = Callable[[T, Region], Iterable[str]]


@dataclass
class CheckResult:
    region: str
    date: str
    field: str
    value: str
    anomaly: str


class ApiChecker:
    def __init__(self):
        self.item_checks: list[CheckFuncType[ApiEntry]] = []
        self.api_checks: list[CheckFuncType[list[ApiEntry]]] = []
        self.field_checks: list[tuple[CheckFuncType[str], list[str]]] = []
        self.anomalies: list[CheckResult] = []

    def check_item(self, func: CheckFuncType[ApiEntry]) -> CheckFuncType[ApiEntry]:
        self.item_checks.append(func)
        return func

    def check_api(self, func: CheckFuncType[list[ApiEntry]]) -> CheckFuncType[list[ApiEntry]]:
        self.api_checks.append(func)
        return func

    def check_field(self, *fields: str) -> Callable[[CheckFuncType[str]], CheckFuncType[str]]:
        def decorator(func: CheckFuncType[str]) -> CheckFuncType[str]:
            if not fields:
                raise ValueError(f'No fields specified for {func.__name__}')
            self.field_checks.append((func, list(fields)))
            return func

        return decorator

    def add_anomaly(self, region: Region, date: Any, field: str, value: str, anomaly_text: str):
        self.anomalies.append(CheckResult(
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

        if self.anomalies:
            sys.exit(1)

    def write_report(self):
        if not self.anomalies:
            if os.path.isfile(REPORT_FILE):
                os.remove(REPORT_FILE)
            return

        grouped = defaultdict(list)
        for result in self.anomalies:
            key = (result.region, result.date, result.field, result.value)
            grouped[key].append(result.anomaly)

        anomalies_by_type = Counter()

        with open(REPORT_FILE, 'w', encoding='utf-8') as output_file:
            for (region, date, field, value), anomalies in grouped.items():
                output_file.write(f'Region: {region}, Date: {date}, Field: {field}\n')
                output_file.write(f'Value: {value}\n')
                output_file.write('Anomalies:\n')
                for anomaly in sorted(anomalies):
                    output_file.write(f'  {anomaly}\n')
                    anomaly_type = anomaly.split(':', 1)[0].strip() if ':' in anomaly else anomaly
                    anomalies_by_type[anomaly_type] += 1
                output_file.write('-' * 40 + '\n')

        print(f'\nChecks complete. Results saved to {REPORT_FILE}')
        print(f'Total entries with anomalies: {len(grouped)}')
        print(f'Total anomalies: {anomalies_by_type.total()}')
        if anomalies_by_type:
            print('Anomalies by type:')
            for type_name, count in sorted(anomalies_by_type.items(), key=lambda x: x[1], reverse=True):
                print(f'  {type_name}: {count}')
