# setup.py
from setuptools import setup, find_packages

setup(
    name='logica-desvios',
    version='0.1.0', # Mantenha ou atualize a versão se necessário
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
    ],
    author='Marcos Sea',
    author_email='wss13.framework@gmail.com', # E-mail atualizado
    description='Agente Inteligente para Resiliência Adaptativa (Método do Desvio)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/WSS13Framework/curso-automacao-linux-resiliente-limpo', # URL atualizada
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: Adaptive Systems',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
    ],
    python_requires='>=3.8',
)