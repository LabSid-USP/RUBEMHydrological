<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/LabSid-USP/RUBEMHydrological">
    <img src="https://github.com/LabSid-USP/RUBEMHydrological/blob/develop/images/icon.png" alt="Logo" width="120" height="120">
  </a>

  <h3 align="center">RUBEM Hydrological</h3>

  <p align="center">
    QGIS plugin that uses <b>R</b>ainfall r<b>U</b>noff <b>B</b>alance <b>E</b>nhanced <b>M</b>odel (a distributed hydrological model) to calculate monthly flows with changes in land use over time
    <br />
    <a href="https://github.com/LabSid-USP/RUBEMHydrological"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://www.youtube.com/playlist?list=PL3Wazcs1VbKlM6N4Q8A8Pry7Aoug9v-Fl">View Demo</a>
    ·
    <a href="https://github.com/LabSid-USP/RUBEMHydrological/issues">Report Bug</a>
    ·
    <a href="https://github.com/LabSid-USP/RUBEMHydrological/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!--
<p align="center">
  <img width="373" height="456" src="https://user-images.githubusercontent.com/70075435/120209930-9a0b7800-c205-11eb-8289-8148d0b62db1.png">
</p>
-->

RUBEM Hydrological is a QGIS plugin that assists in the configuration and execution of the [Rainfall rUnoff Balance Enhanced Model (RUBEM)](https://github.com/LabSid-USP/RUBEM#readme) algorithm, which is an improved model of balance between rain and runoff.

RUBEM provides a powerful distributed hydrologic model for spatial and temporal representation of hydrological processes such as rainfall, land use and ground elevation. The model is based on equations that represent the physical processes of the hydrological cycle, with the flexibility to study a wide range of applications, including impacts of changes in climate and land use. Furthermore, the model presents resolution flexible spatial, inputs are raster-type files taken from remote sensing data and operates with a reduced number of calibration parameters.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* [**QGIS 3.22**](https://qgis.org) or newer;
* [**PCRaster Processing Provider**](https://jvdkwast.github.io/qgis-processing-pcraster/).

### Installation

1. Download the latest release zip file from the [releases page](https://github.com/LabSid-USP/RUBEMHydrological/releases);
2. Open QGIS and go to the `Plugin` menu;
3. Choose `Manage and Install Plugins...`;
4. Choose `Install from ZIP`;
5. Choose the downloaded zip file;
6. Click `Install Plugin`;
7. The successful message will show if the RUBEM Hydrological is installed.

<!-- USAGE EXAMPLES -->
## Usage

To locate and start the plugin in the QGIS GUI use the submenu of the `Plugins` menu (`Plugins -> RUBEM Hydrological -> RUBEM Hydrological`).

Walk through the [basic tutorial](https://github.com/LabSid-USP/RUBEMHydrological), check out the rest of the [documentation](https://github.com/LabSid-USP/RUBEMHydrological), and [ask questions](https://forms.gle/JmxWKoXh4C29V2rD8) if you run into trouble.


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/LabSid-USP/RUBEMHydrological/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**. See [`CONTRIBUTING.md`](https://github.com/LabSid-USP/RUBEMHydrological/blob/main/CONTRIBUTING.md) for more information.



<!-- LICENSE -->
## License

Distributed under the GPLv3 License. See [`LICENSE.md`](https://github.com/LabSid-USP/RUBEMHydrological/blob/main/LICENSE.md) for more information.



<!-- CONTACT -->
## Contact

In any of our communication channels please abide by the [RUBEM Hydrological Code of Conduct](https://github.com/LabSid-USP/RUBEMHydrological). In summary, being friendly and patient, considerate, respectful, and careful in your choice of words.

- Contact us at: [rubem.hydrological@labsid.eng.br](mailto:rubem.hydrological@labsid.eng.br)

- Support Form: [https://forms.gle/JmxWKoXh4C29V2rD8](https://forms.gle/JmxWKoXh4C29V2rD8)

- Project Link: [https://github.com/LabSid-USP/RUBEMHydrological](https://github.com/LabSid-USP/RUBEMHydrological)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Laboratório de Sistemas de Suporte a Decisões Aplicados à Engenharia Ambiental e de Recursos Hídricos](http://labsid.eng.br/Contato.aspx)
* [Departamento de Engenharia Hidráulica e Ambiental da Escola Politécnica da Universidade de São Paulo](http://www.pha.poli.usp.br/)
* [Fundo Patrimonial Amigos da Poli](https://www.amigosdapoli.com.br/)
