from setuptools import setup, find_packages

setup(
    name="esm_rhythm",
    version="2.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author="Michael Ordon",
    description="Ephemeral Spectral Memory (ESM) Core Engine",
    license="PROPRIETARY - Trade Secret",
    install_requires=[
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
)
