# Django StaticEngine - Документация
## Обзор
**Django StaticEngine** — это Django-приложение для обслуживания статических файлов и директорий с поддержкой шаблонов Django. Оно позволяет превратить любую папку с HTML-файлами в полнофункциональный статический сайт с обработкой Django-шаблонов.

## Установка
```shell
pip install django-static-engine
```

## Быстрый старт
#### 1. Добавьте `'staticsite'` в `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...,
    'staticsite.apps.StaticSiteConfig',
]
```

#### 2. Настройте базовую директорию в `settings.py`:
```python
STATICSITE_DIR = BASE_DIR / 'src'  # или любой другой путь
```

#### 3. Добавьте URL-конфигурацию в ваш `urls.py`:
```python
from django.conf import settings
from django.urls import path, include
from staticsite.views import view_constructor

urlpatterns = [
    # ... другие URL ...
    path('site/', include('staticsite.urls')),
]

# Или создайте собственное представление
urlpatterns = [
    path('src/<path:path>', view_constructor('src'), name='src')
]
```

#### 4. Создайте структуру файлов:
```text
src/
├── static_content/
│   ├── index.html
│   ├── about.html
│   ├── styles.css
│   └── images/
│       └── logo.png
```

## Конфигурация
```python
from pathlib import Path

# settings.py
# Обязательная настройка
BASE_DIR = Path(__file__).parent.parent

# Включить шаблон для отображения директорий
STATICSITE_USE_DIR_TEMPLATE = True  # По умолчанию: False

# Путь к директории с исходными файлами (если отличается от BASE_DIR/src)
STATIC_SITE_DIR = BASE_DIR / 'my_static_files'
```

## Использование
### Базовая структура URL
#### После установки приложение обслуживает файлы по следующим URL:

- `http://localhost:8000/site/ `- корневая директория
- `http://localhost:8000/site/path/to/file.html` - конкретный файл
- `http://localhost:8000/site/directory/` - директория (если включен шаблон)

### Поддерживаемые типы файлов
#### Приложение автоматически определяет MIME-типы для:

- HTML файлы (`.html`, `.htm`) - обрабатываются как Django-шаблоны
- JSON файлы (`.json`) - возвращаются как JSON-ответы
- CSS/JavaScript (`.css`, `.js`) - обслуживаются как статические файлы
- Изображения (`.png`, `.jpg`, `.gif`, etc.)
- PDF документы (`.pdf`)
- Текстовые файлы (`.txt`, `.xml`)
- Другие бинарные файлы - обслуживаются с соответствующими MIME-типами

### Особенности работы
#### HTML-файлы как шаблоны
HTML-файлы обрабатываются движком шаблонов Django, что позволяет использовать:

- Теги шаблонов ({% tag %})
- Переменные ({{ variable }})
- Наследование шаблонов
- Встроенные фильтры

#### Пример `index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Мой сайт{% endblock %}</title>
</head>
<body>
    <h1>Добро пожаловать</h1>
    <p>Текущее время: {{ now|date:"H:i" }}</p>
</body>
</html>
```

#### JSON-файлы
JSON-файлы автоматически парсятся и возвращаются как JSON-ответы API.

#### Отображение директорий
При включении `STATICSITE_USE_DIR_TEMPLATE = True`, приложение будет отображать содержимое директорий в виде таблицы с информацией о файлах:

- Имя файла
- Размер (в удобном формате: b, Kb, Mb, etc.)
- Дата последнего изменения

## Безопасность
Приложение включает следующие меры безопасности:

1. Проверка пути: Предотвращает доступ к файлам вне базовой директории
2. Скрытые файлы: Игнорирует файлы, начинающиеся с точки (.)
3. Нормализация путей: Защита от path traversal атак

## Кастомизация
### Шаблон для директорий
Вы можете создать собственный шаблон для отображения директорий. Создайте файл `__directory__.html` в директории шаблонов вашего проекта:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Содержимое: {{ path }}</title>
</head>
<body>
    <h1>Содержимое директории: {{ path }}</h1>
    <table>
        <tr>
            <th>Имя</th>
            <th>Размер</th>
            <th>Дата изменения</th>
        </tr>
        {% for file in files %}
        <tr>
            <td><a href="{{ file.name }}">{{ file.name }}</a></td>
            <td>{{ file.size }}</td>
            <td>{{ file.date }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
```

## Примеры использования
### Служение статического сайта

```python
# urls.py проекта
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('', include('staticsite.urls')),  # Корневой URL
]
```

### Мультисайтовость

```python
# urls.py проекта
from django.urls import path
from django.conf import settings
from staticsite.views import view_constructor
import os

urlpatterns = [
    path('site1/', view_constructor(os.path.join(settings.BASE_DIR, 'sites/site1'))),
    path('site2/', view_constructor(os.path.join(settings.BASE_DIR, 'sites/site2'))),
]
```

### API-эндпоинты из JSON
Создайте файл `api/data.json`:

```json
{
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
}
```

Доступно по адресу: `http://localhost:8000/site/api/data.json`

## Ограничения
1. Не предназначен для замены Django Static Files в production
2. Не поддерживает кэширование (используйте nginx или CDN для production)
3. Не рекомендуется для больших файлов (>100MB)
4. Все HTML-файлы обрабатываются через движок шаблонов Django, что может замедлить работу при большой нагрузке

## Производительность
Для production-окружения рекомендуется:

1. Использовать веб-сервер (nginx, Apache) для обслуживания статических файлов
2. Настроить кэширование
3. Использовать CDN для медиа-файлов

## Отладка
При возникновении проблем проверьте:

1. Правильность пути к базовой директории
2. Разрешения на чтение файлов
3. Корректность MIME-типов для нестандартных файлов
4. Кодировку HTML-файлов (поддерживаются UTF-8 и cp1251)

## Лицензия
MIT License

## Поддержка
Для отчетов об ошибках и предложений используйте issue tracker на GitHub репозитории проекта.
