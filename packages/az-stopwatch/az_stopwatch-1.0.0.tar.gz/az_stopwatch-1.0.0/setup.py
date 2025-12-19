from setuptools import setup, find_packages

setup(
    name="az_stopwatch",
    version="1.0.0",
    author="Eldar",
    # Qovluq strukturuna uyğun düzəliş:
    packages=find_packages(where="."), 
    install_requires=[],
    python_requires=">=3.7",
    long_description="Stopwatch converter for Azerbaijani language",
    long_description_content_type="text/plain",
)