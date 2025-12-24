from setuptools import setup, find_packages

setup(
    name="eldar-math-duel",
    version="1.0.0",
    author="Eldar",
    description="Two-player Math Duel terminal game",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "math-duel=eldar_math_duel.game:main"
        ]
    }
)
