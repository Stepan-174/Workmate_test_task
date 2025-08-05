import argparse
import json
from collections import defaultdict
from tabulate import tabulate
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Анализ лог-файлов и вывод отчета по эндпоинтам.')
    parser.add_argument('logfiles', nargs='+', help='example1.log example2.log')
    parser.add_argument('--date', type=str, default=None, help='Фильтр по дате в формате YYYY-MM-DD (в default можно установить, например 2025-06-22 или оставить None)')
    args, unknown = parser.parse_known_args()
    return args

def extract_date_from_timestamp(timestamp_str):
    # Пример: "2025-06-22T13:57:32+00:00"
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

def process_log_files(logfiles, filter_date=None):
    endpoint_stats = defaultdict(lambda: {'count': 0, 'total_response_time': 0.0})

    for logfile in logfiles:
        try:
            with open(logfile, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        log_entry = json.loads(line)
                        # Извлекаем дату из "@timestamp"
                        timestamp_str = log_entry.get('@timestamp')
                        if timestamp_str is None:
                            continue
                        entry_date = extract_date_from_timestamp(timestamp_str)
                        if filter_date and entry_date != filter_date:
                            continue
                        url = log_entry.get('url')
                        response_time = log_entry.get('response_time', 0)
                        if url is not None:
                            stats = endpoint_stats[url]
                            stats['count'] += 1
                            stats['total_response_time'] += response_time
                    except json.JSONDecodeError:
                        print(f"Некорректная строка: {line}")
        except FileNotFoundError:
            print(f"Файл {logfile} не найден. Пропускаю.")
        except Exception as e:
            print(f"Ошибка при обработке файла {logfile}: {e}")

    total_records = sum(d['count'] for d in endpoint_stats.values())
    print(f"Обработано записей по фильтру '{filter_date}': {total_records}")
    return endpoint_stats

def main():
    args = parse_args()
    endpoint_stats = process_log_files(args.logfiles, args.date)

    table_data = []
    for url, data in endpoint_stats.items():
        count = data['count']
        avg_response_time = data['total_response_time'] / count if count > 0 else 0
        table_data.append([url, count, f"{avg_response_time:.3f}"])

    table_data.sort(key=lambda x: x[1], reverse=True)

    print(tabulate(table_data, headers=["handler", "total", "avg_response_time"], tablefmt="grid"))

if __name__ == '__main__':
    main()