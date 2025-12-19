"""PyInstaller hook for gtec_licensing package.

This hook ensures all submodules and dependencies are automatically
included when building executables with PyInstaller.
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all gtec_licensing submodules and data files
datas, binaries, hiddenimports = collect_all('gtec_licensing')

# Add cryptography dependencies used by gtec_licensing
hiddenimports += [
    'cryptography',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.ciphers',
    'cryptography.hazmat.primitives.ciphers.algorithms',
    'cryptography.hazmat.primitives.ciphers.modes',
    'cryptography.hazmat.primitives.padding',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.bindings',
    'cryptography.hazmat.bindings.openssl',
    'cryptography.hazmat.bindings._rust',
    'requests'
]
