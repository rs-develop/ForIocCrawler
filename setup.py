import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ForIocCrawler",
    version="1.0.4",
    author="rs-develop",
    author_email="rsdevelop.contact@gmail.com",
    description="A forensic ioc extractor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rs-develop/ForIocCrawler",
    project_urls={
        "Bug Tracker": "https://github.com/rs-develop/ForIocCrawler/issues",
    },
    scripts=['forioccrawler'],
    packages=['crawler'],
	include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8"
)