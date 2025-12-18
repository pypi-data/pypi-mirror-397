from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as arq:
    readme = arq.read()

setup(
    name='PyBetStoric',
    version='1.0.0',
    license='MIT',
    author='andre.melol',
    author_email='amelo171710@gmail.com',
    description='Biblioteca Python para acessar dados históricos de jogos de cassinos online.',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[
        'pragmatic-play', 'live-casino', 'historical-data', 'gambling-data',
        'casino-games', 'roulette', 'baccarat', 'blackjack', 'game-shows',
        'crash-games', 'dragon-tiger', 'andar-bahar', 'sic-bo', 'spaceman',
        'crazy-time', 'sweet-bonanza', 'monopoly-live', 'mega-roulette',
        'speed-baccarat', 'lightning-roulette', 'brazilian-games', 'asian-games',
        'casino-analytics', 'betting-history', 'live-dealer', 'casino-api'
    ],
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0',
        'playwright>=1.20.0',
        'supabase>=2.0.0',
        'bcrypt>=4.0.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment'
    ],
)