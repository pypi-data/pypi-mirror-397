from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
        long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except UnicodeDecodeError:
    with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sticky-note-organizer",
    version="1.1.0",
    author="Primus-Izzy",
    author_email="",
    description="A powerful CLI and GUI tool to extract, organize, and analyze Microsoft Sticky Notes (modern and classic formats)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Primus-Izzy/Sticky-Note-Organizer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sticky-organizer=sticky_organizer.cli:main",
            "sticky-organizer-gui=sticky_organizer.gui_launcher:main",
        ],
        "gui_scripts": [
            "sticky-organizer-gui=sticky_organizer.gui_launcher:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)