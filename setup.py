from setuptools import setup, find_packages

setup(
    name="image-hosting",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "gradio>=4.0.0",
        "Pillow>=9.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "image-hosting=image_hosting.main:main",
        ],
    },
) 