from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A Python wrapper to generate real Outlook/Hotmail accounts."

setup(
    name="outlook-account-generator", 
    version="1.0.2",  # Versiyonu artırdık (Hata almamak için)
    author="TempOutlookAPI",
    author_email="support@tempoutlookapi.com",
    description="A Python wrapper to generate real Outlook/Hotmail accounts and fetch OTPs via JSON.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://rapidapi.com/EymenTakak/api/temp-outlook-api",  # BURASI DÜZELTİLDİ
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
    ],
)
