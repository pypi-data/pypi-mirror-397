from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="redzone-lib",
    version="1.0.10",  # automatically updated by CI/CD pipeline
    author="RedZone Co",
    author_email="info@redzone.co",
    description="Contains common utilities for use across Redzone projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=[
        "redzone",
        "redzone.auth",
        "redzone.caches",
        "redzone.event_buses",
        "redzone.exceptions",
        "redzone.handlers",
        "redzone.handlers.events",
        "redzone.middleware",
        "redzone.objects",
        "redzone.schemas",
        "redzone.services",
        "redzone.settings",
        "redzone.utils",
    ],
    python_requires=">=3.10",
)
