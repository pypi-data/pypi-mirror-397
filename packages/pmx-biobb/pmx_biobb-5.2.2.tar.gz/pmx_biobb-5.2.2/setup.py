"""pmx: a toolkit for free-energy calculation setup/analysis and
biomolecular structure handling.

For installation type the command::
  python setup.py install
or
  pip install .
"""

from setuptools import setup, Extension
import versioneer


def readme():
    with open('README.rst') as f:
        return f.read()

# ----------
# Extensions
# ----------
pmx = Extension('pmx._pmx',
                libraries=['m'],
                include_dirs=['src/pmx/extensions/pmx'],
                sources=['src/pmx/extensions/pmx/Geometry.c',
                         'src/pmx/extensions/pmx/wrap_Geometry.c',
                         'src/pmx/extensions/pmx/init.c',
                         'src/pmx/extensions/pmx/Energy.c']
                )

xdrio = Extension('pmx._xdrio',
                  libraries=['m'],
                  include_dirs=['src/pmx/extensions/xdr'],
                  sources=['src/pmx/extensions/xdr/xdrfile.c',
                           'src/pmx/extensions/xdr/xdrfile_trr.c',
                           'src/pmx/extensions/xdr/xdrfile_xtc.c']
                  )
extensions = [pmx, xdrio]

# -----
# Setup
# -----
setup(name='pmx_biobb',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Toolkit for free-energy calculation setup/analysis and biomolecular structure handling',
      long_description_content_type='text/x-rst',
      long_description=readme(),
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
      ],
      url='https://github.com/deGrootLab/pmx/tree/develop',
      author='Daniel Seeliger, Vytautas Gapsys',
      author_email='d.seeliger@gmx.net, vytautas.gapsys@gmail.com',
      license='LGPL-3.0',
      packages=['pmx'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      ext_modules=extensions,
      tests_require=['pytest'],
      install_requires=['numpy', 'scipy', 'matplotlib', 'rdkit'],
      python_requires=">=3.9",
      entry_points={'console_scripts': ['pmx = pmx.scripts.cli:entry_point']},
      )
