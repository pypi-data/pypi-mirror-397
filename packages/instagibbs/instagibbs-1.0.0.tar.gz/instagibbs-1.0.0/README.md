# instaGibbs

Instant Gibbs free energy estimation coupled to a HDX-MS database.

![Screenshot from instagibbs web application](assets/20250612_web_screenshot.png)

## Aim

The aim of this project is to provide a realiable and fast method to esitmate Linderstrøm-Lang Gibbs free energies (ΔG/ΔΔG) for HDX-MS data. Gibbs free energies are determined at the peptide level by area-under-the-curve (ΔG) and area-between-curves (ΔΔG). Peptide-level values can then be reduced to residue level by weighted averaging or linear least squares fitting, where the latter method can enhance residue-resolution by taking into account overlapping peptides. 

The main advantage of `instagibbs` is computational speed. Therefore, the method can be applied in batch to many datasets easily. For a dataset of 180 peptides spanning 872 residues, obtaining peptide-level ΔG values takes ~100 ms, and reduction to residue-level by ridge regression another 8 ms. For differential HDX (ΔΔG) computational times are 1.7 ms (peptide) and 7.4 ms (residue-level lasso regression). ΔG values are found by root finding in area comparison to a theoretical uptake curve and therefore takes longer to compute. ΔΔG values are from direct peptide to peptide area comparison and only requires trapezoidal integration. 


Output residue-level result from `instagibbs` provide an estimate of true underlying ΔG values, as with any method. Use and interpret results at your own risk. When in doubt, use weighted averaging, which is robust yet loses some resolution compared to regression methods. Lasso and ridge regression methods for obtaining ΔG or ΔΔG values can provide higher resolution but are subject to overfitting or false-positive detection of differences. Use higher regularization values to mitigate overfiitting and cross-reference results with peptide-level data. 


### Concepts

The idea of relating area-between-curves to ΔΔG originates from the Hamuro jasms paper:

Hamuro, Y. Quantitative Hydrogen/Deuterium Exchange Mass Spectrometry. J. Am. Soc. Mass Spectrom. (2021) [doi:10.1021/jasms.1c00216](doi:10.1021/jasms.1c00216).

In the implementation by `instagibbs`, areas are determined by trapezoidal integration over the available time window. D-uptake curves are not extrapolated to 0% or 100% D-uptake. As a consequence, the range of ΔG values that can be obtained is dependent on the time window (and temperature/pH) and ΔΔG values can be underestimated as a result of potential area differences outside of the time windows. 
However, these limitations are not specific to the method but a result of the principle that if something is not measured it cannot be resolved. To expand the ΔG range or resolve additional ΔΔG in differential HDX, the time window must be expanded. 

### Development Install

Install uv


Git clone

$ git clone https://github.com/Jhsmit/instagibbs.git

navigate to the folder

```
$ cd instagibbs
```

Make a virtual env

```
$ uv venv -p "3.12"
```

Activate the venv

```
$ .venv\Scripts\activate
```

Editable install the project

```
$ uv pip install -e .
```

download the database:
$ git clone https://github.com/Jhsmit/HDXMS-database.git

Then change the `database_dir` in `instagibbs/config/default.yaml` to point to your local copy of the database. 

### Run

`solara run instagibbs/web/app.py`
