import os, json
from django.http import Http404, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.template import engines
from pathlike_typing import PathLike
from . import STATICSITE_USE_DIR_TEMPLATE
from .utils import get_mime_type, File


def view_constructor(base_dir: PathLike):
    def view(request, path: str):
        # Нормализуем путь
        if path:
            path = os.path.normpath(path).lstrip('/').lstrip('\\')
            if path.startswith('/') or path.startswith('\\'):
                path = path[1:]

        abspath = os.path.join(base_dir, path)

        # Проверка безопасности
        real_base = os.path.realpath(base_dir)
        real_path = os.path.realpath(abspath)

        if not real_path.startswith(real_base):
            raise Http404("Access denied")

        if not os.path.exists(abspath):
            raise Http404(f"Path not found: {abspath}")

        # Если это директория
        if os.path.isdir(abspath):
            # Проверяем index.html, index.htm
            for index_file in ['index.html', 'index.htm', 'default.html']:
                index_path = os.path.join(abspath, index_file)
                if os.path.exists(index_path):
                    abspath = index_path
                    break
            else:
                # Если нет индексного файла
                if STATICSITE_USE_DIR_TEMPLATE:
                    files = []
                    try:
                        for f in os.listdir(abspath):
                            if not f.startswith('.'):  # Пропускаем скрытые файлы
                                file_path = os.path.join(abspath, f)
                                if os.path.isfile(file_path) or os.path.isdir(file_path):
                                    files.append(File(file_path))
                        return render(request, '__directory__.html', {'files': files, 'path': path})
                    except Exception as e:
                        raise Http404("DirTemplate error")
                raise Http404("NotDirTemplateError")

        # Если это файл
        if os.path.isfile(abspath):
            mime_type = get_mime_type(abspath)

            # HTML файлы
            if mime_type == 'text/html':
                try:
                    with open(abspath, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # Создаем простой шаблонный движок
                    from django.template import Engine
                    engine = Engine.get_default()

                    # Создаем шаблон из строки
                    template = engine.from_string(content)

                    # Рендерим с минимальным контекстом
                    rendered = template.render({}, request)

                    return HttpResponse(rendered, content_type='text/html')

                except UnicodeDecodeError:
                    # Если не UTF-8, пробуем другие кодировки
                    try:
                        with open(abspath, 'r', encoding='cp1251') as file:
                            content = file.read()
                        engine = engines['django'].engine
                        template = engine.from_string(content)
                        rendered = template.render({}, request)
                        return HttpResponse(rendered, content_type='text/html')
                    except Exception as e:
                        # Отдаем как бинарный файл - ПРАВИЛЬНЫЙ ФИКС
                        try:
                            return FileResponse(open(abspath, 'rb'), as_attachment=False, content_type=mime_type)
                        except:
                            raise Http404("Cannot read HTML file")
                except Exception as e:
                    # Вместо ошибки, просто отдаем содержимое файла
                    try:
                        with open(abspath, 'r', encoding='utf-8') as file:
                            return HttpResponse(file.read(), content_type='text/html')
                    except:
                        try:
                            return FileResponse(open(abspath, 'rb'), as_attachment=False, content_type=mime_type)
                        except:
                            raise Http404("Cannot read file")

            # JSON файлы
            elif mime_type == 'application/json':
                try:
                    with open(abspath, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    return JsonResponse(data, safe=False)
                except Exception as e:
                    return HttpResponse(f"Invalid JSON: {str(e)}", status=500, content_type='text/plain')

            # Все остальные файлы
            else:
                try:
                    # Простой и правильный способ - FileResponse сам закроет файл
                    response = FileResponse(
                        open(abspath, 'rb'),
                        as_attachment=False,
                        content_type=mime_type
                    )
                    # Для текстовых файлов можно добавить кодировку
                    if mime_type.startswith('text/'):
                        response['Content-Type'] = f'{mime_type}; charset=utf-8'
                    return response
                except Exception as e:
                    raise Http404(f"Cannot read file: {str(e)}")

        raise Http404("Root error")

    return view