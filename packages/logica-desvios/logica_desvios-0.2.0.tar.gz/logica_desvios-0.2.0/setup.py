from setuptools import setup, find_packages

setup(
    name='logica-desvios',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
    ],
    author='Marcos Sea',
    author_email='seu.email@example.com', # Substitua pelo seu e-mail
    description='Biblioteca para o Método do Desvio com Circuit Breaker Adaptativo',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/WSS13Framework/curso-automacao-linux-resiliente-limpo', # Substitua pela URL do seu repositório
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
