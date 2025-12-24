<h1 align="center">
<img src="https://documentation.smartmt.com/MastaAPI/15.1.1/images/smt_logo.png" width="150" alt="SMT"><br>
<img src="https://documentation.smartmt.com/MastaAPI/15.1.1/images/MASTA_15_logo.png" width="400" alt="Mastapy">
</h1><br>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python](https://img.shields.io/pypi/pyversions/mastapy
)

Mastapy is the Python scripting API for MASTA.

- **Website**: https://www.smartmt.com/
- **Support**: https://support.smartmt.com/
- **Documentation**: https://documentation.smartmt.com/MastaAPI/15.1.1/


### Features

- Powerful integration with MASTA with the ability to run Python scripts from the MASTA interface directly.
- Ability to use MASTA functionality external to the MASTA software in an independent script.
- An up-to-date and tight integration with Python. This is not a lightweight wrapper around the C# API. It is specifically designed for Python and works great in tandem with other common scientific Python packages (e.g. SciPy, NumPy, Pandas, Matplotlib, Seaborn, etc.)
- Extensive backwards compatibility support. Scripts written in older versions of mastapy will still work with new versions of MASTA.
- Full support for Linux and .NET 8.0 versions of the MASTA API.

### Release Information

#### Minor Changes

- If the `description` keyword argument has not been set for a `masta_property`, it will attempt to derive it from the decorated function's documentation.
- Various improvements and bug fixes.
