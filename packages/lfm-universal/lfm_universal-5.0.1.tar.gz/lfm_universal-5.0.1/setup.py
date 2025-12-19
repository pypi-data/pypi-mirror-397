
from setuptools import setup, find_packages

setup(
    name="lfm-universal",
    version="5.0.1",
    author="Keith Luton",
    author_email="keith@thenewfaithchurch.org",
    description="LFM V5.0 - Physics-Based Inference & Geometric Pruning Engine",
    long_description="The official implementation of the Luton Field Model (LFM). Includes the V3 Stability Lock and V5 Axiomatic Derivation Engine. MANDATORY: Requires LFM_AXIOM_ACCEPTED=TRUE environment variable.",
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
        "transformers>=4.30.0",
        "accelerate>=0.20.0"
    ]
)
