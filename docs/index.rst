
Current release info
====================

.. image:: https://img.shields.io/pypi/v/pyramids-gis
  :target: https://pypi.org/project/pyramids-gis/0.1.0/


.. image:: https://img.shields.io/conda/v/conda-forge/hapi?label=conda-forge
  :target: https://pypi.org/project/pyramids-gis/0.1.0/


.. image:: https://img.shields.io/pypi/pyversions/pyramids-gis
  :target: https://pypi.org/project/pyramids-gis/0.1.0/


.. image:: https://img.shields.io/github/forks/mafarrag/hapi?style=social   :alt: GitHub forks


.. image:: https://anaconda.org/conda-forge/hapi/badges/downloads.svg
  :target: https://anaconda.org/conda-forge/hapi


.. image:: https://img.shields.io/conda/vn/conda-forge/hapi   :alt: Conda (channel only)
  :target: https://pypi.org/project/pyramids-gis/0.1.0/


.. image:: https://img.shields.io/gitter/room/mafarrag/Hapi
  :alt: Gitter


.. image:: https://static.pepy.tech/personalized-badge/pyramids-gis?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
  :target: https://pypi.org/project/pyramids-gis/0.1.0/


.. image:: https://img.shields.io/pypi/v/pyramids-gis
  :alt: PyPI


.. image:: https://anaconda.org/conda-forge/hapi/badges/platforms.svg
  :target: https://anaconda.org/conda-forge/hapi


.. image:: https://static.pepy.tech/personalized-badge/pyramids-gis?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
  :target: https://pepy.tech/project/pyramids-gis



.. image:: https://static.pepy.tech/personalized-badge/pyramids-gis?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
  :target: https://pepy.tech/project/pyramids-gis


.. image:: https://static.pepy.tech/personalized-badge/pyramids-gis?period=week&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
  :target: https://pepy.tech/project/pyramids-gis




pyramids - GIS utility package
=====================================================================


**pyramids** is a Python package providing fast and flexible way to build Hydrological models with different spatial
representations (lumped, semidistributed and conceptual distributed) using HBV96.
The package is very flexible to an extent that it allows developers to change the structure of the defined conceptual model or to enter
their own model, it contains two routing functions muskingum cunge, and MAXBAS triangular function.


Main Features
-------------
- Modified version of HBV96 hydrological model (Bergström, 1992) with 15 parameters in case of considering
  snow processes, and 10 parameters without snow, in addition to 2 parameters of Muskingum routing method
- GIS modules to enable the modeler to fully prepare the meteorological inputs and do all the preprocessing
  needed to build the model (align rasters with the DEM), in addition to various methods to manipulate and
  convert different forms of distributed data (rasters, NetCDF, shapefiles)
- Visualization module for animating the results of the distributed model, and the meteorological inputs

.. digraph:: Linking

    GIS -> raster;
    GIS -> vector;
    GIS -> giscatchment;
    dpi=200;

.. toctree::
   :hidden:
   :maxdepth: 1

   Installation <00Installation.rst>
   Tutorial <03tutorial.rst>
   GIS <05GIS.rst>
