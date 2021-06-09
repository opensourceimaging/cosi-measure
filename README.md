# COSI Measure
Cost effective open source imaging (COSI) is a collaborative initiative currently building an affordable low field open source magnetic resonance imaging (MRI) scanner. Along this path, affordable and customizable open source tools are required. 

COSI Measure is an open source multipurpose 3-axis robot operating in a large volume, that can be equipped with e.g. field mapping probes for static or dynamic field measurements (electromagnetic, temperature etc.). Submillimeter fidelity and reproducibility/backlash performance were evaluated experimentally. It can be potentially upgraded to be used as a CNC, for 3D printing or other applications, that require reproducible submillimeter movements.

![Photograph of COSI Measure](/Publications/cosi_measure_photo.jpg)

## System specifications:
* Dimension: (80x90x105)cm³
* Working volume: (53x53x64)cm³
* Precision: positioning error <1mm
* Speed: 37mm/s
* Max load: 21kg
* Applied force: 896N (91kg)
* Standalone system: Beagle Bone Black, ARM Contex-A8 1GHz, 512MB DDR3, Programmable real-time unit subsystem
* Inductive limit switches
* Emergency stop
* Open Source Software GUI (python)
* Estimated material costs: ~2000€

More photos and videos can be found on opensourceimaging.org: https://www.opensourceimaging.org/project/cosi-measure/


## (Re)builds & contacts

General contact:
Name | Email | Institution | COSI Measure Applications
-----|-----|-----|-----|
Lukas Winter | lukas.winter@ptb.de | Physikalisch-Technische Bundesanstalt (PTB), Berlin, Germany | Magnetic field mapping of MR magnets, implant safety measurements, RF field mapping of RF coils using time-domain H- and E-field sensors, Measurements within an MR scanner, 3D printing

![COSI Measure Builds](/Publications/cosi_measure_builds.jpg)

(Known) builds
Name | Email | Institution | COSI Measure Applications
-----|-----|-----|-----|
Haopeng Han | haopeng.han@mdc-berlin.de | Max-Delbrück Center for Molecular Medicine, Berlin, Germany | Temperature and RF field mapping of RF coils
Tom O'Reilly | t.o_reilly@lumc.nl | Leiden University Medical Center (LUMC), Leiden, Netherlands | Magnetic field mapping of low field MR magnets
Benjamin Menküc | benjamin.menkuec@fh-dortmund.de | University of Applied Sciences, Dortmund, Germany | Magnetic field mapping of low field MR magnets
Mark Bason | M.Bason@sussex.ac.uk | Quantum Systems and Devices, University of Sussex, Falmer, England | Magnetic field measurements
Wolfgang Kilian | Wolfgang.Kilian@ptb.de | Physikalisch-Technische Bundesanstalt (PTB), Berlin, Germany | 3D printing of phantoms


## Contributors (alphabetical order)
Nils Allek
Mark Bason
Haopeng Han
Amjad Kasabashy
Wolfgang Kilian
Benjamin Menküc
Tom O'Reilly
David Shiers
Berk Silemek
Karl Stupic
Lukas Winter

____________________________________________________
If you find COSI Measure useful in your work, please cite this paper:

H. Han, R. Moritz, E. Oberacker, H. Waiczies, T. Niendorf and L. Winter, "Open 
Source 3D Multipurpose Measurement System with Submillimetre Fidelity and First
Application in Magnetic Resonance", Scientific Reports, 7:13452, 2017

www.nature.com/articles/s41598-017-13824-z 
