import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="app_catalog_cleanup_tool",
    version="0.0.1",
    author="Łukasz Piątkowski",
    author_email="lukasz@giantswarm.io",
    description="Application that removes old charts from chart repos.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giantswarm/app-catalog-cleanup-tool",
    packages=setuptools.find_packages(),
    keywords=["helm registry", "helm"],
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.9",
)
