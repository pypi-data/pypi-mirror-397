from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent

INFO = "A Flask-based REST API for retrieving jokes with support for multiple categories and languages."

# Long description from README
long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
  # Basic identity
  name="ckx-jokes",
  version="0.4",

  # Author info
  author="CryptoKingXavier",
  author_email="cryptokingxavier001@gmail.com",

  # Project description
  summary=INFO,
  description=INFO,
  long_description=long_description,
  long_description_content_type="text/markdown",

  # URLs
  url="https://pyjok-es.onrender.com/",
  project_urls={
    "Documentation": "https://pypi.org/project/ckx-jokes/",
    "Source": "https://github.com/CryptoKingXavier/PyJok.Es/",
    "Tracker": "https://github.com/CryptoKingXavier/PyJok.Es/issues/",
  },

  # Packaging
  packages=find_packages(),
  include_package_data=True,

  # Python Compatibility
  python_requires=">=3.10",

  # Runtime dependencies
  install_requires=[
    # Add dependencies here.
    "flask",
    "wheel",
    "pyjokes",
    "ascii-magic",
    "python-dotenv",
  ],

  # Optional dependencies
  extras_require={
    "dev": ["pytest", "mypy", "twine", "snoop", "gunicorn"],
  },

  # Entry points (CLI tools)
  entry_points={
    "console_scripts": [
      "jokes-server=ckx_jokes:server",
    ],
  },

  # License
  license="MIT",

  # Classifiers (PyPI SEO)
  classifiers=[
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries",
  ],

  # Keywords (searchability)
  keywords="python packaging cli utilities jokes",

  # Zip safety (usually True)
  zip_safe=False,
)
