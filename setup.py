readme = open('README.md').read()
VERSION = "0.0.1"

requirements = []

setup(
    
    name = 'Web Transfert Protocol',
    version = VERSION,
    author = 'Torzivalds',
    author_email = 'tozivalds@gmail.com',
    url = '...',
    description ='P2P Network',
    long_description = readme,
    license = 'GPL',

    # Package info
    packages = find_packages(exclude=('test',)),
    zip_safe = True,
    install_requires = requirements,
    extras_require = {},
)