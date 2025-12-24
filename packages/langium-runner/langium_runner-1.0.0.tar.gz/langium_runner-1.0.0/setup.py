from setuptools import setup, find_packages

setup(
    name='langium_runner',
    version='1.0.0',
    packages=find_packages(exclude=["langium_runner.tests", "langium_runner.tests.*"]),
    install_requires=[
        # No runtime dependencies required - all types are self-contained
    ],
    description='A runner for evaluating Langium responses.',
    author='Typefox',
    author_email='dennis.huebner@typefox.io',
    url='https://github.com/TypeFox/langium-ai',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "run-langium=langium_runner.evaluator_runner:run_langium_evaluator_cli",
        ],
    },
)
