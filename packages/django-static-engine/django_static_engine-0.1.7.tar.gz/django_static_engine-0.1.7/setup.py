from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    desc = f.read()

setup(
    name='django-static-engine',
    version='0.1.7',
    description='A Django static site generator',
    long_description=desc,
    long_description_content_type='text/markdown',
    author_email='magilyas.doma.09@list.ru',
    author='Маг Ильяс DOMA (MagIlyasDOMA)',
    url='https://github.com/magilyasdoma/django-static-engine',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django==5.2.9',
        'filetype>=1.2.0',
        'pathlike-typing>=1.0.0'
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Framework :: Django',
        'Framework :: Django :: 5.2',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    project_urls=dict(
        Source='https://github.com/magilyasdoma/django-static-engine',
        Documentation='https://github.com/magilyasdoma/django-static-engine/README.md',
        Tracker='https://github.com/magilyasdoma/django-static-engine/issues',
    ),
    python_requires='>=3.10',
    keywords=[
        'django',
        'static',
        'file'
    ]
)