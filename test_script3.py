import pytest
import json
import tempfile
import os
from io import StringIO
from unittest.mock import patch
from datetime import datetime
import argparse

# Импортируем функции из вашего файла (предположим, он называется script3.py)
# Если ваш файл называется иначе, замените название.
import script3

@pytest.fixture
def temp_log_file():
    # Создаём временный лог-файл с несколькими записями
    content = [
        json.dumps({
            "@timestamp": "2025-06-22T13:57:32+00:00",
            "url": "/api/v1/resource",
            "response_time": 120.5
        }),
        json.dumps({
            "@timestamp": "2025-06-22T14:00:00+00:00",
            "url": "/api/v1/resource",
            "response_time": 130.0
        }),
        json.dumps({
            "@timestamp": "2025-06-21T10:00:00+00:00",
            "url": "/api/v2/other",
            "response_time": 200.0
        }),
        ""  # пустая строка должна игнорироваться
    ]
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
        tf.write("\n".join(content))
        tf_name = tf.name
    yield tf_name
    os.remove(tf_name)

def test_extract_date_from_timestamp():
    timestamp = "2025-06-22T13:57:32+00:00"
    date_str = script3.extract_date_from_timestamp(timestamp)
    assert date_str == "2025-06-22"

    invalid_timestamp = "invalid-date"
    assert script3.extract_date_from_timestamp(invalid_timestamp) is None

def test_process_log_files_without_filter(temp_log_file):
    # Проверка без фильтрации по дате
    stats = script3.process_log_files([temp_log_file])
    # Проверяем, что есть записи по /api/v1/resource и /api/v2/other
    assert "/api/v1/resource" in stats
    assert "/api/v2/other" in stats

    total_count = sum(d['count'] for d in stats.values())
    assert total_count == 3  # 2 + 1 записи

    # Проверяем подсчёт response_time для /api/v1/resource
    resource_stats = stats["/api/v1/resource"]
    assert resource_stats['count'] == 2
    assert abs(resource_stats['total_response_time'] - (120.5 + 130.0)) < 1e-6

def test_process_log_files_with_date_filter(temp_log_file):
    # Фильтр по дате 2025-06-22 должен вернуть только записи за этот день
    stats = script3.process_log_files([temp_log_file], filter_date="2025-06-22")
    
    # Должен содержать только /api/v1/resource с двумя записями
    assert "/api/v1/resource" in stats
    assert "/api/v2/other" not in stats
    
    resource_stats = stats["/api/v1/resource"]
    assert resource_stats['count'] == 2

def test_process_log_files_with_no_matching_date(temp_log_file):
    # Фильтр по дате, которой нет записей, должен вернуть пустой результат
    stats = script3.process_log_files([temp_log_file], filter_date="2000-01-01")
    assert len(stats) == 0

def test_process_log_files_with_nonexistent_file(capsys):
    # Обработка несуществующего файла должна вывести сообщение и не падать
    nonexistent_file = "nonexistent.log"
    stats = script3.process_log_files([nonexistent_file])
    
    captured = capsys.readouterr()
    assert f"Файл {nonexistent_file} не найден" in captured.out or captured.out != ""

def test_main_output(capsys, temp_log_file):
    # Тестируем функцию main с фиктивными аргументами и выводом таблицы
    
    test_args = ["script_name", temp_log_file]
    
    with patch('sys.argv', test_args):
        with patch('script3.parse_args', return_value=argparse.Namespace(logfiles=[temp_log_file], date=None)):
            script3.main()
    
        out, _ = capsys.readouterr()
        # Проверяем наличие заголовков таблицы и URL из логов
        assert "handler" in out and "total" in out and "avg_response_time" in out
    
def test_main_with_date_filter(capsys, temp_log_file):
    test_args = ["script_name", temp_log_file, "--date", "2025-06-22"]
    
    with patch('sys.argv', test_args):
        with patch('script3.parse_args', return_value=argparse.Namespace(logfiles=[temp_log_file], date="2025-06-22")):
            script3.main()
    
        out, _ = capsys.readouterr()
        # Проверяем что вывод содержит ожидаемую дату фильтрации или соответствующие данные