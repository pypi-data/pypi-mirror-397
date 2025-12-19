from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys

QUETZAL_LOGO = """
\033[92m\033[1m
╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║   ██████╗  ██╗   ██╗ ███████╗ ████████╗ ███████╗  █████╗  ██╗               ║
║  ██╔═══██╗ ██║   ██║ ██╔════╝ ╚══██╔══╝ ╚══███╔╝ ██╔══██╗ ██║               ║
║  ██║   ██║ ██║   ██║ █████╗      ██║      ███╔╝  ███████║ ██║               ║
║  ██║▄▄ ██║ ██║   ██║ ██╔══╝      ██║     ███╔╝   ██╔══██║ ██║               ║
║  ╚██████╔╝ ╚██████╔╝ ███████╗    ██║    ███████╗ ██║  ██║ ███████╗          ║
║   ╚══▀▀═╝   ╚═════╝  ╚══════╝    ╚═╝    ╚══════╝ ╚═╝  ╚═╝ ╚══════╝          ║
║                                                                             ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║                                                                             ║
║  Lightning-Fast CPU Training for Low-Resource Language Models               ║
║  Optimized Performance • Enterprise-Ready • Production-Grade                ║
║  Powered by Axya-Tech                                                       ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
\033[0m
"""

class PostInstallCommand(install):
    def run(self):
        try:
            print(QUETZAL_LOGO)
            print("\n\033[92m✓ Quetzal installed successfully!\033[0m")
            print("\033[93mGet started: from quetzal import FastLanguageModel\033[0m\n")
        except UnicodeEncodeError:
            # On terminals that can't render all characters, skip decorative output
            pass
        install.run(self)

class PostDevelopCommand(develop):
    def run(self):
        try:
            print(QUETZAL_LOGO)
            print("\n\033[92m✓ Quetzal development mode activated!\033[0m\n")
        except UnicodeEncodeError:
            pass
        develop.run(self)

setup(
    name="quetzal-ai",
    version="1.0.7",
    author="Axya-Tech",
    description="Ultra-fast CPU training for low-resource languages",
    long_description=open("README.md", encoding="utf-8").read() if sys.path[0] else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.36.0",
        "tokenizers>=0.15.0",
        "datasets>=2.14.0",
        "accelerate>=0.25.0",
        "peft>=0.7.0",
        "bitsandbytes>=0.41.0",
        "sentencepiece>=0.1.99",
        "numpy>=1.24.0",
        "tqdm>=4.65.0",
        "scikit-learn>=1.3.0",
    ],
    python_requires=">=3.8",
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    entry_points={
        "console_scripts": [
            "quetzal=quetzal.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
