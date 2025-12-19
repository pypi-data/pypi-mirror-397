# memPyGUTS

memPyGUTS is a python package for fitting GUTS models to survival data, from ecotoxicology experiments, developed at the Osnabrück University, Germany

## Description

The small package is currently capable of calibrating various General Unified Threshold model of Survival (GUTS,[1]) models to exposure-survival datasets using a frequentist Nelder-Mead approach. Uncertainties can be additionally assessed using a Bayesian Monte-Carlo-Marrcov-Chain method (MCMC). It is based on the epytox package by Raymond Nepstad (github.com/nepstad/epytox).
Additional models for GUTS mixture toxicity [2] and BufferGUTS models [3] for above-ground invertebrates are also implemented.

For state-of-the-art parameter estimation algorithms it is recommended to install mempyguts with the `[pymob]` optional dependency as detailed below. This installs a number of additional packages and software that are required to 

## Installation


### Using `pip` to install mempyguts from pypi

It is highly recommended to install mempyguts in a separate conda environmment (see Development version > Conda environment)

```bash
pip install mempyguts
```

For installing the `pymob` framework for extended capabilities

```bash
pip install mempyguts[pymob]
```

### Development version

#### Prerequisites

+ git https://git-scm.com/downloads
+ conda (miniconda3 recommended) https://docs.anaconda.com/miniconda/install/

#### Clone from gitlab

Clone the repository and change into the directory:

```bash
git clone https://gitlab.uni-osnabrueck.de/memuos/mempyguts.git
cd mempyguts
```

#### Conda environment

Create a conda environment with Python 3.11 and activate:

```bash
conda create -n mempyguts -c conda-forge python=3.11 pandoc graphviz
conda activate mempyguts
```

#### Editable install

Install the package into the activated environment with the package installer 
for python (pip) as an editable installation
```bash
pip install -e .[pymob]
```


## Usage

For usage of mempyguts, see the Jupyter notebook: `notebooks/demo.ipynb` 
For usage of mempyguts models with the `pymob` backend for performing parameter estimation, see `notebooks/demo_pymob.ipynb`


### Release notes & migration to guts_base 2.0

`guts_base` 2.0 provides a number of improvements, which are detailed in the following.
In general it now provides the following API methods

- `sim.estimate_parameters`: 
  Estimate the parameters of a model and auto-generate a report
- `sim.transform`: 
  Transform/inverse-transform a simulation in terms of exposure and time to 
  arbitrary scales
- `sim.estimate_background_mortality`: 
  Estimate the parameters of background-mortality module parameters separately 
  from the remaining parameters
- `point_estimate`: provide the MAP or mean value of the posterior 
- `evaluate`: 
  Run a single simulation with given parameters, initial conditions and 
  input values
- `draft_laboratory_experiment`: 
  Can be used to generate a treatment design and if required survival data 
  from a conditional binomial probability distribution
- `to_openguts`: 
  Export observations to openguts excel format

### stable API

Most importantly a **tested API method to estimate the parameters of GUTS models** is provided. Take a look at the docstring of `GutsBase.estimate_parameters`. Previously it was required to manually assemble pymob components, which was error prone. With the stable API, the most important config options are exposed, while any other configurations can still be accessed and changed via the `sim.config` attribute. This
API is now also used in the [mempyguts-fitting-templates](https://gitlab.uni-osnabrueck.de/memuos/mempyguts-fitting-template) repository.

**Below is a usage example:**

Start by generating a simulated experiment. Instead of simulating an experiment, you could read data in the Openguts format as pandas dataframes or use the mempyguts api (`mempy.input_data).


```py
from mempy.model import RED_SD
from guts_base import PymobSimulator
experiment = PymobSimulator.draft_laboratory_experiment(
    treatments={"C": 0.0, "T1": 1, "T2": 5, "T3": 50, "T4": 100},
    simulate_survival=True,
)
```

Next the `from_model_and_dataset` classmethod is used to construct a GutsBase simulation

```py
survival_data = experiment.survival.to_pandas().T
exposure_data = {"A": experiment.exposure.to_pandas().T}
sim = PymobSimulator.from_model_and_dataset(
    model=RED_SD(),
    exposure_data=exposure,
    survival_data=survival,
    output_directory="results/test"
)
```

Finally we call estimate_parameters to estimate the model parameters and assemble
a report

```py
sim.estimate_parameters()
```

### Separate estimation of background mortality parameters

`GutsBase` provides a possibility to automatically estimate background mortality parameters with the method `GutsBase.estimate_background_mortality`. For this it needs the information, which parameters are background parameters. This is done by marking the parameters in the `params_info` dict.

For e.g. `RED_SD`:

```python
class RED_SD(...):
    def __init__(...):
        # inject at the end
        self.params_info["hb"]["module"] = "background-mortality"
        
```
This needs to be done for all parameters that are involved in estimating the background mortality.
They will then be picked up in the `GutsBase.estimate_background_mortality` method and
seperately estimated from all other parameters on the control treatments. By default,
all other parameters obtain the 'tktd' module. This can of course be explicitly changed.
Currently only the exact keyworkd 'background-mortality' has an effect.

### Units

`GutsBase` now provides an interface to specify the units of the parameters in the model, so that units can be provided directly in the report. `GutsBase` can infer the exact units of the parameters if the dimensionality of the parameters and input units are provided. This is handled by the new `guts_base.sim.units` module. Similarly to the
new `"module"` key, units will be specified in the `params_info` dict with a new `"unit"` key. 

```python
class RED_SD(...):
    def __init__(...):
        # inject at the end
        self.params_info["hb"]["unit"] = "1/d"
        
```

Units are auto-parsed with the python [pint package](https://pint.readthedocs.io/en/stable/), this means pretty much any unit specification will just work. If you use "1/day" or "1/d" or "1/days", will be converted to the standard quantity "1/d". For output formatting you can specify formatting options via the `config.guts_base.unit_format_pint` setting.

**Providing default time units**: Time units can be provided in the index name of the datasets (dataframes) that are used to construct the GutsBase object using the `PymobSimulator.from_model_and_dataset` classmethod. It can be specified with standard day formats in square brackets in the survival and exposure sheets. E.g. "time [d]" or "time [hours]". Note that the unit must be the same in all sheets that are used for the simulation. If time units are not provided, GutsBase falls back to the default time unit specified in `config.guts_base.unit_time`, which is by default day.

Exposure units are currently not read from the provided datasets. They must be provided manually, which is possible by accessing the `config.guts_base.unit_input` setting. Here, a dictionary is specified which holds a unit for each exposure path. Unequal units of exposure paths is possible and the units of the required weights parameters will be used, based on the relation between input units.

The units can be specified in the `from_model_and_dataset` constructor. Note that 
**units specified in the data sheets will always take precedent over the units specified in the constructor**. 

```python
sim = PymobSimulator.from_model_and_dataset(
    model=RED_SD(),
    exposure_data=exposure,
    survival_data=survival,
    unit_time="hour",
    unit_input={"Exposure": "ng/µL"},
    output_directory="results/test"
)
```

In future releases the specified dimensionality of the units will be used to automatically provide simulation transforms, which will aid the automated calibration of exposure datasets of vastly different exposure scales with standard priors. In addition, dimensionality specification will be used to auto-transform parameters to match any desired target unit. Finally parsing units from the dictionary keys in the exposure_data will be possible, which means that exposure units can be specified in the Openguts excel files so that they are self contained with minimal documentation.


### Transforms

guts_base 2.0 also provides possibilities for transforming simulations. These EXPERIMENTAL feature is well documented in the docstring of `GutsBase.transform`

If transforms are used to scale the exposure unit to the unit interval by providing the
maximum exposure value. Please make sure you adapt the priors beforehand, especially the 'm' prior! E.g.:

```python
sim.config.model_parameters.m.prior = "lognorm(scale=0.01,m=3)"

max_expo = float(sim.observations.exposure.max().values)
sim.estimate_parameters(
    transform_scalings={"time_factor": 1.0, "x_in_factor": max_expo}
)
```

Why is that necessary, in the REDUCED GUTS models, damage takes the unit of exposure. This means, that the threshold ($m$) of the GUTS model will also be most likely between zero and one (unless data are provided with no mortality, but then again, the fit well be garbage anyways). This is all also detailed in the documentation of `GutsBase.transform`.


### Other API methods

- `point_estimate`: provide the MAP or mean value of the posterior 
- `evaluate`: Run a single simulation with given parameters, initial conditions and input values
- `draft_laboratory_experiment`: Can be used to generate a treatment design and if required survival data from a conditional binomial probability distribution
- `to_openguts`: Export observations to openguts excel format

### other important pymob methods

- `export`: Export a simulation to disk including the most relevant components
- `from_directory`: To load a simulation from disk

There are many more. See the documentation for more info.

## Resources

Many other ressources are available to help you with mempyguts, guts_base and pymob. 
Please look at these ressources to understand the correct usage of this software.

- Survival Modelling Workshop: https://gitlab.uni-osnabrueck.de/fschunck/survival_modelling_workshop
- Examples for fitting parameters with GUTS models in different environments (HPC, Gitlab-Runner): https://gitlab.uni-osnabrueck.de/memuos/mempyguts-fitting-template
- Pymob (https://github.com/flo-schu/pymob) is a performant library, that supports parameter estimation with various backends for mulitdimensional problems. Documentation: https://pymob.readthedocs.io/en/latest/
- `guts_base` is an interface to connect Pymob functionality with `mempyguts` models: https://gitlab.uni-osnabrueck.de/fschunck/guts_base

## References

[1] Jager, T., Albert, C., Preuss, T. G., & Ashauer, R. (2011). General
        unified threshold model of survival - A toxicokinetic-toxicodynamic
        framework for ecotoxicology. Environmental Science and Technology, 45(7),
        2529–2540. 

[2] Bart, S., Jager, T., Robinson, A., Lahive, E., Spurgeon, D. J., & Ashauer, R. (2021). Predicting Mixture Effects over Time with Toxicokinetic–Toxicodynamic Models (GUTS): Assumptions, Experimental Testing, and Predictive Power. Environmental Science & Technology, 55(4), 2430–2439. https://doi.org/10.1021/acs.est.0c05282

[3] Bürger, L. U., & Focks, A. (2025). From water to land—Usage of Generalized Unified Threshold models of Survival (GUTS) in an above-ground terrestrial context exemplified by honeybee survival data. Environmental Toxicology and Chemistry, 44(2), 589–598. https://doi.org/10.1093/etojnl/vgae058


