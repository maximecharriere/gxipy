# Daheng Imaging Galaxy SDK - Python API

> [!IMPORTANT]
> **THIS IS AN UNOFFICIAL PUBLISH ON PYPI OF THE GXIPY API DEVELOPED BY DAHENG IMAGING !**  
> I'm not the developer or maintainer of the Python API, nor the Galaxy SDK. For any questions or issues, **please contact Daheng Imaging directly**.

> [!NOTE]
> If a new version of the Python API is offered by Daheng Imaging, please create an issue or a PR, and I will update the Package on PyPi.

This package provides Python bindings for the Daheng Imaging Galaxy SDK, allowing you to control Daheng cameras in Python applications.

## Prerequisites

- Galaxy SDK must be installed on your system
  - Windows: Download from [Daheng Imaging Download Page](https://va-imaging.com/pages/customerdownloads)
  - Linux: Download from [Daheng Imaging Download Page](https://va-imaging.com/pages/customerdownloads)
- Python 3.6 or higher

## Installation

1. Install the Galaxy SDK for your operating system
2. Run `pip install iai-gxipy`

## Documentation

The documentation is provided by Daheng Imaging and can be found in `C:\Program Files\Daheng Imaging\GalaxySDK\Development\Doc\Python Interface Development User Manual.pdf`

## Note for myself : How to update the package

1. Download the `Galaxy Linux x86 SDK` from the [Daheng Imaging website](https://va-imaging.com/fr/pages/telechargementsclients)
2. Extract `Galaxy Linux x86 SDK_x.x.xxxx\Galaxy_Linux-x86_Gige-U3_32bits-64bits_x.x.xxxx.xxxx\Galaxy_Linux_Python_x.x.xxxx.xxxx\api`
3. Replace `gxipy` and `setup.py` in the repo root with the new ones from the extracted folder.
4. Update `pyproject.toml` > version with the new version number (same as in the new `setup.py`).
   - **Mandatory**: the published version is read from `pyproject.toml`, not from the git tag, and PyPI refuses to upload a version that already exists.
   - To re-publish the same SDK version (e.g. a packaging fix), use a post-release: `x.x.xxxx.xxxx.post1`.
5. (Optional) Check the build locally:
   ```shell
   pip install --upgrade build twine
   python -m build
   python -m twine check dist/*
   ```
6. Commit and push the changes to `main`.
7. Create a GitHub release with a tag matching the version, prefixed with `v` (e.g. `v2.6.2606.9081`).
8. Publishing the release automatically triggers the [Publish to PyPI](.github/workflows/publish-to-pypi.yml) GitHub Action.

---

@DahengImaging If you want me to remove this package from PyPi, please create an issue on the corresponding Github repo.
