from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

"""
ext_modules = [
    Extension("edgelistParser",  ["edgelistParser.pyx"], extra_compile_args = ["-Ofast -march=native"]),
    Extension("pageRank",  ["pageRank.pyx"], include_dirs=[numpy.get_include()], extra_compile_args = ["-Ofast -march=native"]),
    Extension("plotNetwork",  ["plotNetwork.pyx"], extra_compile_args = ["-Ofast -march=native"]),
    Extension("utils",  ["utils.pyx"], include_dirs=[numpy.get_include()], extra_compile_args = ["-Ofast -march=native"])
]
"""
# we use the non-cpu specific compilation
ext_modules = [
    Extension("edgelistParser",  ["edgelistParser.pyx"], extra_compile_args = ["-O3"]),
    #Extension("pageRank",  ["pageRank.pyx"], include_dirs=[numpy.get_include()], extra_compile_args = ["-O3"]),
    #Extension("plotNetwork",  ["plotNetwork.pyx"], extra_compile_args = ["-O3"]),
    Extension("utils",  ["utils.pyx"], include_dirs=[numpy.get_include()], extra_compile_args = ["-O3"])
]

setup(
    name = 'LocalPagerank Utils',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
