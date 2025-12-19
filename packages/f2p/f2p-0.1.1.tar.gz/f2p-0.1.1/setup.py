from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="f2p",  # This is the name for pip install
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "astropy",
        "scipy"
    ],
    description="FITS 2D/3D physical size analyzer",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Utsav Siwakoti",
    author_email="siwakotiutsav@gmail.com",  # replace with your email
    url="https://github.com/siwakotiutsav/fits2physical",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
