FAQ
===

Here are some commonly-asked questions and their answers.

General
-------

Why does this project exist?
````````````````````````````

The distributed hydrological model was developed as part of the process by Professor Arisvaldo Vieira Méllo Júnior to become an Associate professor at São Paulo University. The model was applied to Petrobras project of development and research.

What does "RUBEM Hydrological" mean?
````````````````````````````````````

RUBEM means the "Rainfall-Runoff Balance Enhanced Model". Also is a homage in memory of the Professor Rubem La Laina Porto, who has made significant contributions to teach, research, and for the entire water resource brazilian community.
 
Who's behind this?
``````````````````

The RUBEM Hydrological was developed by the `LabSid at the Polytechnic School of São Paulo University <http://labsid.eng.br>`__. The LabSid team had the valuable contribution of the "Associação Fundo Patrimonial Amigos da Poli", financing the development of the plugin and the improvement of the model. We would also like to mention the important contribution of "Petróleo Brasileiro S.A. – Petrobras" for financing the development and application of the model. And finally, the contributions and efforts of Professor Rubem La Laina Porto to the Brazilian water resources community.

How is RUBEM Hydrological licensed?
```````````````````````````````````

RUBEM Hydrological is licensed by the `General Public Licence (GPL) v3 <https://github.com/LabSid-USP/RUBEMHydrological/blob/main/LICENSE.md>`__. The GPL v3 is a strong copyleft license that allows any copy or modification of the original code must also be released under the GPL v3. In other words, you can take the GPL 3 code, add to it or make major changes, then distribute your version.

<QGIS Plugin X> does <feature Y> – why doesn't RUBEM Hydrological?
```````````````````````````````````````````````````````````````````

RUBEM Hydrological provides a tool to facilitate the use of the RUBEM model in a free GIS environment. RUBEM provides a powerful distributed hydrologic model for spatial and temporal representation of hydrological processes such as rainfall, land use and ground elevation. The model is based on equations that represent the physical processes of the hydrological cycle, with the flexibility to study a wide range of applications, including impacts of changes in climate and land use. Furthermore, the model presents resolution flexible spatial, inputs are raster-type files taken from remote sensing data and operates with a reduced number of calibration parameters.

We're well aware that there are other powerful distributed hydrologic models out there, and we're not averse to borrowing ideas where appropriate. However, RUBEM Hydrological was developed precisely because we were unhappy with the *status quo*, so please be aware that "because <QGIS Plugin X> does it" is not going to be a sufficient reason to add a given feature to RUBEM Hydrological.

How do I cite RUBEM Hydrological?
``````````````````````````````````

.. important::

    There is an original paper under evaluation with the RUBEM Hydrological model application and validation. As soon as the paper gets the publication we will update the citation reference.

How do I cite the dataset?
```````````````````````````

Please consider citing the datasets when using them:

`Méllo, A. V., L. M. O. Olivos, C. Billerbeck, S. S. Marcellini, W. D. Vichete, D. M. Pasetti, L. M. d. Silva, G. A. d. S. Soares, J. R. B. Tercini (2021). Rainfall-Runoff Balance Enhanced Model Applied to Tropical Hydrology, HydroShare, http://www.hydroshare.org/resource/6f3670b8cd944e7ea72e03d1b9ca928f`

Plugin Installation
--------------------

How do I get started?
``````````````````````

1. Download the latest stable release (.zip file);
2. Install RUBEM Hydrological (read the :doc:`installation guide </installation>`);
3. Walk through the tutorial;
4. Check out the rest of the :doc:`documentation </index>`, and `ask questions <https://forms.gle/JmxWKoXh4C29V2rD8>`__ if you run into trouble.

A `step-by-step plugin installation video tutorial <https://www.youtube.com/watch?v=F8zx9So2nrI>`__ is available on our YouTube channel.

..  youtube:: F8zx9So2nrI
    :width: 100%

---------

What are RUBEM Hydrological's prerequisites?
`````````````````````````````````````````````

RUBEM Hydrological was developed to work on QGIS version 3.22 or higher. Typically, we will support a QGIS version up to and including the first RUBEM Hydrological LTS release whose support ends after support for that version of QGIS ends.

.. note::

    RUBEM model relies on the `PCRaster Python Modelling Framework <https://pcraster.geo.uu.nl>`__, `NumPy <https://numpy.org/>`__ and `GDAL <https://gdal.org/>`__. The `PCRaster Processing Provider <https://github.com/jvdkwast/qgis-processing-pcraster>`__ must be installed in your QGIS Python environment, check out the `related documentation <https://jvdkwast.github.io/qgis-processing-pcraster/>`__ for more information.

What QGIS version can I use with RUBEM Hydrological?
`````````````````````````````````````````````````````

The latest version of QGIS 3 is recommended.

Should I use the stable version or development version?
````````````````````````````````````````````````````````

If you're using it in production, you should be using a stable release.

Using RUBEM Hydrological
------------------------

See the RUBEM Hydrological :doc:`user guide </userguide>` and the :doc:`basic tutorial </tutorials>` on how to use it.

A `basic video tutorial <https://www.youtube.com/watch?v=R8CcLSkLj0Q>`__ on how to use the plugin is available on our YouTube channel.

..  youtube:: R8CcLSkLj0Q
    :width: 100%

---------

Getting Help
------------

Where can I go to get help?
````````````````````````````

You can get help by hitting the help button in the plugin window. You might also find the answers you are looking for in our documentation guides and tutorials. These provide step-by-step solutions to common user requirements. Check if anyone else had the same question/problem in `our repository issues <https://github.com/LabSid-USP/RUBEMHydrological/issues>`__.

If you still have questions, fill out the `support form <https://forms.gle/JmxWKoXh4C29V2rD8>`__ or `sending us an email <mailto:rubem.hydrological+support@labsid.eng.br>`__ 

.. note::

    In any of our communication channels please abide by the :doc:`RUBEM Hydrological Code of Conduct </code-of-conduct>`. In summary, being friendly and patient, considerate, respectful, and careful in your choice of words.

I think I've found a bug! What should I do?
```````````````````````````````````````````

Detailed instructions on how to handle a potential bug can be found in our `Guide to contributing to RUBEM Hydrological <https://github.com/LabSid-USP/RUBEMHydrological/blob/main/CONTRIBUTING.md>`__.

How can I get started contributing code to RUBEM Hydrological?
```````````````````````````````````````````````````````````````

Thanks for asking! We've written an entire document devoted to this question. It's titled `Contributing to RUBEM Hydrological <https://github.com/LabSid-USP/RUBEMHydrological/blob/main/CONTRIBUTING.md>`__.

Troubleshooting
----------------

This section contains some advice about errors and problems commonly encountered during the development of RUBEM Hydrological.

Common Problems Checklist
``````````````````````````

- Check the start and the end of the simulation period, they should fall within the dataset - period;
- Before starting the simulation, we recommend to create the station location in the place you - would like to have the flow (hypothetical or gauged section);
- Make sure you have correctly pre-processed all the raw input data;
- The soil map classification should have a special care in the urban areas;
- The model does not provide an automatic calibration for gauges sections, you should do it - manually (this feature is under evaluation and may be available in future releases).
