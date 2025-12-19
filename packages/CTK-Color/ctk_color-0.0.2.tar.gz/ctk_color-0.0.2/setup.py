from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="CTK_Color",
    version="0.0.2",
    description="A customizable color tool for CTkinter Textboxes",
    author="Vishal Sharma",
    author_email="vishalsharma659615@gmail.com",
    keywords="customtkinter ctkinter tkinter gui color textbox widget",
    long_description=long_description,  # 📝 From README.md
    long_description_content_type="text/markdown",  # 📄 Type of README
    license="MIT",
    packages=find_packages(),  # This finds CTK_Color/
    classifiers=[  # ✅ Optional classifiers for PyPI & users
        "Development Status :: 3 - Alpha",  # or "4 - Beta", "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License"
    ],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "customtkinter>=5.0.0",  # Adjust to the minimum version you support/test against
    ],
    url="https://github.com/vishal24102002/CTK_Color",  # 🌐 Project URL
    project_urls={  # 🔗 Additional links
        "Bug Tracker": "https://github.com/vishal24102002/CTK_Color/issues",
        "Documentation": "https://github.com/vishal24102002/CTK_Color#readme",
        "Source Code": "https://github.com/vishal24102002/CTK_Color",
    },
)
