readme= open('README.md').read()
VERSION= "0.0.3"

requirements= []

setup(
    name= 'Web Transfert Protocol',
    version= VERSION,
    author= 'Torzivalds',
    author_email= 'tozivalds@gmail.com',
    url= 'https://myrasp.fr/WTP',
    description='P2P Network',
    long_description= readme,
    license= 'GPL3.0'
    # Package info
    packages= find_packages(exclude=('test',)),
    zip_safe= True,
    install_requires= requirements,
    extras_require= {},
)
