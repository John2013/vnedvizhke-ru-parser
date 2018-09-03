# vnedvizhke-ru-parser

Парсер контактов с сайта [vnedvizhke.ru](https://vnedvigke.ru)


# Как установить

Python 3 должен быть установлен.

```bash
$ pip install -r requirements.txt  # или pip3
```

Рекомендуется использовать [virtualenv/venv](https://devman.org/encyclopedia/pip/pip_virtualenv/).


# Как запустить

## Через *.py файл

Пример:
```bash
python seek_dev_nighters.py # или python3
```

Ответ:
```
count: 122
Готово, результат в файле C:\parser\contacts.csv
```

## exe файл

### собрать 

```bash
pyinstaller --onefile  parser.py
```

exe файл будет в 'dist/parser.exe'

### запустить

Запустите файл `dist/parser.exe`

Скрипт выполняется около минуты, результаты сохраняются в csv файле `contacts.csv` 
в директории скрипта