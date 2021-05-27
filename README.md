<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM">
    <img src="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM/blob/develop/images/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">RUBEM Hydrological</h3>

  <p align="center">
    QGIS plugin that uses <b>R</b>ainfall r<b>U</b>noff <b>B</b>alance <b>E</b>nhanced <b>M</b>odel (a distributed hydrological model) to calculate monthly flows with changes in land use over time
    <br />
    <a href="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM">View Demo</a>
    ·
    <a href="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM/issues">Report Bug</a>
    ·
    <a href="https://github.com/LabSid-USP/Plugin_QGIS_RUBEM/issues">Request Feature</a>
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

[![Product Name Screen Shot][product-screenshot]](https://example.com)

RUBEM Hydrological is a QGIS plugin that assists in the configuration and execution of the **Rainfall rUnoff Balance Enhanced Model** algorithm, which is an improved model of balance between rain and runoff.

The distributed hydrological model for transforming precipitation into total flow is based on equations that represent the physical processes of the hydrological cycle, with spatial distribution defined in a grid and monthly time scale. The model was developed based on classic concepts of hydrological processes and equations based mainly on the formulations of the SPHY (TERINK et al., 2015), WEAP (YATES et al., 2005) and WetSpass-M (ABDOLLAHI et al., 2017).

The name is a posthumous tribute to Professor Rubem La Laina Porto, dean of the [Department of Hydraulic and Environmental Engineering](http://www.pha.poli.usp.br/), of the [Escola Politécnica of the University of São Paulo](https://www.poli.usp.br/), who dedicated his professional life to the study, development and practices in hydrological sciences, contributing to the improvement of the state of art and training of students and professionals working in the area.



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* QGIS 3.16.7 'Hannover' long-term release or newer

### Installation

1. Download the repo branch as zip;
2. Open QGIS `Plugins`->`Install plugin from zip file`;

  Or 

1. Clone the repo
   ```sh
   git clone https://github.com/LabSid-USP/Plugin_QGIS_RUBEM.git
   ```
2. Copy the repo folder to QGIS plugin directory 
   
   Windows:
   ```powershell
   Xcopy /E /I C:\Plugin_QGIS_RUBEM %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Plugin_QGIS_RUBEM
   ```
   GNU/Linux:
   ```sh
   cp -R /Plugin_QGIS_RUBEM /home/USER/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Plugin_QGIS_RUBEM 
   ```


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/LabSid-USP/Plugin_QGIS_RUBEM/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the GPLv3 License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/LabSid-USP/Plugin_QGIS_RUBEM](https://github.com/LabSid-USP/Plugin_QGIS_RUBEM)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Laboratório de Sistemas de Suporte a Decisões Aplicados à Engenharia Ambiental e de Recursos Hídricos](http://labsid.eng.br/Contato.aspx)
* [Departamento de Engenharia Hidráulica e Ambiental da Escola Politécnica da Universidade de São Paulo](http://www.pha.poli.usp.br/)
* [Fundo Patrimonial Amigos da Poli](https://www.amigosdapoli.com.br/)
