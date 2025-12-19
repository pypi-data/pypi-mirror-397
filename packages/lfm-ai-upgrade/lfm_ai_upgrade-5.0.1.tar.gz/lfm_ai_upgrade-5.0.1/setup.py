
from setuptools import setup, find_packages

setup(
    name="lfm-ai-upgrade",
    version="5.0.1",
    author="Keith Luton",
    author_email="keith@thenewfaithchurch.org",
    description="LFM V5.0 - Critical Security Patch & Axiom Lock",
    long_description="MANDATORY UPDATE: Fixes infinite recursion bug in V3.0. Enforces Axiomatic Stability Lock. Contact author for license keys.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "torch>=2.0.0",
        "lfm-universal>=5.0.1" # Force dependency on the other locked package
    ]
)
