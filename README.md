# Workmate_test_task
Скрипт для обработки лог-файла

Чтобы отображать табличные данные используем модуль tabulate. Он не входит в стандартную библиотеку Python, поэтому tabulate нужно установить:
pip install tabulate

Назначение файлов:
example1.log, example2.log - содержат логи

script3.py - содержит скрипт, обрабатывающий файлы с логами

test_script3.py - содержит скрипт тестов

Запуск кода без фильтра по дате в консоли:
python script3.py example1.log example2.log

Запуск кода с фильтром по дате в консоли:
python script3.py --date 2025-06-22 example1.log example2.log


Запуск тестов в консоли:
pytest test_script3.py
pytest test_script3.py --maxfail=1 --disable-warnings -q

Проверяем покрытие тестами.
Установим pytest-cov:
pip install pytest-cov

Запускаем проверку покрытия:
pytest --cov=script3 --cov-report=term-missing





