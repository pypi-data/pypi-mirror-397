from setuptools import setup, find_packages

setup(
    name="aemuctrl",
    version="0.0.1",
    description="A lightweight Android Emulator Control library using ADB and PyAutoGUI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name", 
    url="https://github.com/Solee-in/aemuctrl", 
    license="MIT",
    packages=find_packages(),
    py_modules=["aemuctrl"], 
    install_requires=[
        "pyautogui", "subprocess" , 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
)
