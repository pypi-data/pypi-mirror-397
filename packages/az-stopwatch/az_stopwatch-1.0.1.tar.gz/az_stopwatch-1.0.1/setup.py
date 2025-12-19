from setuptools import setup, find_packages

setup(
    name="az_stopwatch",
    version="1.0.1",  # Versiyanı mütləq artırın!
    author="Eldar",
    packages=["az_stopwatch"], # Paketi birbaşa adla qeyd edirik
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.7",
    long_description="Stopwatch converter for Azerbaijani language",
    long_description_content_type="text/plain",
)