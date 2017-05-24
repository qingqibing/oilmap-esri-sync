try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup
    packages = ['pystoch','pystoch/trajectory_data']


required = []
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='pystoch',
    version='0.1',
    description='Python implementation of stochastic lagrangian oil probablility analysis',
    author='David Stuebe',
    author_email='DStuebe@ASAScience.com',
    url='http://192.168.100.14/Commercial/pystoch.git',
    classifiers=[
        'License :: ASA Interal',
        'Topic :: Oil Model :: Stochastic',
        'Topic :: Grid:: Probability',
        ],
    license='ASA Internal',
    keywords='oil model probability grid',
    packages=packages,
    package_data={'':['trajectory_data']},
    install_requires = required
)
