from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fabric-accessible-graphics",
    version="0.1.0",
    author="Fabric Accessible Graphics Project",
    description="A toolkit for converting images to tactile-ready formats for PIAF machines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fabric/accessible-graphics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fabric-access=fabric_access.cli:main",
            "fabric-access-mcp=fabric_access.mcp_server.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fabric_access": ["data/*.yaml"],
    },
)
