from setuptools import setup, find_packages

setup(
    name="az_stopwatch",
    version="1.0.4",  # Versiyanı 1.0.4 et ki, PyPI yeniliyi görsün
    author="Eldar",
    description="Saniyəölçən vaxtını Azərbaycan dilində oxuyan kitabxana",
    # Sənin şəkildəki strukturuna uyğun dəqiq ünvan:
    package_dir={"": "az_stopwatch/src"},
    packages=find_packages(where="az_stopwatch/src"),
    include_package_data=True,
    python_requires=">=3.7",
)