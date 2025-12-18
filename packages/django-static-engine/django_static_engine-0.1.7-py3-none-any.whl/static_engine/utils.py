import filetype, os
from datetime import datetime
from django.template.loader import get_template
from django.utils.safestring import mark_safe


def get_mime_type(path):
    # Сначала проверяем расширение файла для распространенных типов
    ext = os.path.splitext(path)[1].lower()

    mime_map = {
        '.html': 'text/html',
        '.htm': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.xml': 'application/xml',
    }

    if ext in mime_map:
        return mime_map[ext]

    # Если не нашли в карте, используем filetype
    kind = filetype.guess(path)
    if kind is None:
        return 'application/octet-stream'
    return kind.mime


class File:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.bytes_size = os.path.getsize(path)
        self.timestamp = os.path.getmtime(path)

    @property
    def size(self):
        s = float(self.bytes_size)
        sizes = ['b', 'kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']
        for i, size_unit in enumerate(sizes):
            if s < 1024 or i == len(sizes) - 1:
                return f"{s:.2f} {size_unit}"
            s /= 1024

    @property
    def date(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%d-%m-%Y %H:%M:%S')

    def to_table(self):
        return mark_safe(f'<td>{self.name}</td>\n<td>{self.size}</td>\n<td>{self.date}</td>')
