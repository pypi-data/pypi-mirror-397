"""
Setup.py for hand_mouse — compatibility wrapper for setuptools.

Modern Python packaging uses pyproject.toml (PEP 517/518), but this setup.py
provides backward compatibility for older build tools and workflows.
"""

from setuptools import setup, find_packages
import os

# Read package version from __init__.py
init_file = os.path.join(os.path.dirname(__file__), 'hand_mouse', '__init__.py')
version = None
with open(init_file) as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

# Read README
readme_file = os.path.join(os.path.dirname(__file__), 'hand_mouse', 'README.md')
with open(readme_file, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="hand-mouse",
    version=version,
    author="FRANCIS JUSU",
    author_email="jusufrancis08@gmail.com",
    description="Control your computer with hand gestures or eye gaze (experimental).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jusufrancis/hand-mouse",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mediapipe",
        "opencv-python",
        "pyautogui",
        "numpy",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="computer-vision accessibility hands eye-tracking mediapipe",
    include_package_data=True,
)
