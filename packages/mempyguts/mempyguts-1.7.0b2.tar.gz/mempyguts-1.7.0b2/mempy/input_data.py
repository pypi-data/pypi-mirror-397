
'''
This file contains functions for handling input data, i.e. reading from files and converting to 
datastructures usable by this implementation.

Classes
----------
None

Functions
----------
multi_interp_treatment_generator()
    Creates interpolating treatment functions from exposure data.
create_datasets()
    Converts input-data to a form structured around the individual treatments.
read_exposure_survival()
    Reads a xlsx file with the exposure and survival data and converts it into useable datastructures.
get_xc()
    Extracts every exposure-function for a given treatment.
split_control_treatment_dataset():
    Splits a dataset into control and treatment datasets.
plot()
    Visualizes the Exposure- and Survival-data as imported by the input_data.read_exposure_survival()-function.
'''
import os
import re
import warnings
from typing import Optional, Dict, Tuple
import pint
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np
from mempy.utils import MempyError

ureg = pint.UnitRegistry()

def multi_interp_treatment_generator(treatments):
    '''
    Creates interpolating treatment functions from exposure data.
    
    Parameters
    ----------
    treatments: pandas.DataFrame
        DataFrame containing the exposure concentrations with the treatments as columns and the timepoints as rows.

    Returns
    ----------
    treatment_funcs: dict
        Dictionary with the treatment-names as keys and the corresponding functions as values. 
    '''
    treatment_funcs = {}
    for treat in treatments:
        t = treatments[treat].index
        conc = treatments[treat].values
        conc1 = conc[~np.isnan(conc)]
        t = t[~np.isnan(conc)]
        s = interpolate.InterpolatedUnivariateSpline(t, conc1, k=1)
        s.__name__ = f'treatment_{treat.lower()}'
        treatment_funcs[treat] = s
    return treatment_funcs


def create_datasets(exposure_funcs, survival_data, treatment_list=None):
    '''
    Converts input-data to a form structured around the individual treatments.

    Parameters
    ----------
    exposure_funcs: dictionary
        Dict of exposures and treatments containing functions representing the external concentrations.
    survival_data: pandas.Dataframe
        Pandas.DataFrame containing the survival for the treatments and timepoints.
    treatment_list: list, optional
        List of strings to name the treatments. If None, the headers of the survival_data-dataframe are used.

    Returns
    ----------
    datasets: list
        List of datasets containing tuples with all exposures and the corresponding survival per treatment.
        In the following Form:
        [
            (exposure_1_treatment_1, exposure_2_treatment_1, ... , exposure_n_treatment_1, survival_treatment_1),
            (exposure_1_treatment_2, exposure_2_treatment_2, ... , exposure_n_treatment_2, survival_treatment_2),
            ...
            (exposure_1_treatment_m, exposure_2_treatment_m, ... , exposure_n_treatment_m, survival_treatment_m)
        ]
    '''
    datasets = []
    if treatment_list == None:
        survival_columns = list(survival_data.keys())
    else:
        survival_columns = treatment_list
    for treatment in survival_columns:
        current_exposure = []
        for sub in exposure_funcs:
            current_exposure.append(exposure_funcs[sub][treatment])
        datasets.append((*current_exposure, survival_data[treatment].dropna()))
    return datasets
    

def read_exposure_survival(
    path, 
    file_name, 
    exposure_name="Exposure", 
    survival_name="Survival", 
    info_name="Info", 
    with_info_dict=False, 
    with_raw_exposure_data=False, 
    visualize=False,
    na_values=["NA", "N/A", "N.A.", "na", "n/a", "n.a."],
):
    
    """
    Reads a xlsx file with the exposure and survival data and converts it into useable datastructures.
    
    Parameters
    --------
    path : str
        Path to the file
    file_name : str
        File name of the xlsx file with the survival and exposure data
    exposure_name : str, default='Exposure'
        Name of the datasheet(s) containing the exposure data
    survival_name : str, default='Survival'
        Name of the datasheet containing the survival data
    info_name : str, default='Info'
        Name of the datasheet containing additional informations
    with_info_dict : bool, default=False
        If True the information datasheet is extracted and converted into a dictionary
    with_raw_exposure_data : bool, default=False
        If the raw exposure data should be returned
    visualize : bool, default=False
        If True the imported data is visualized in two plots
    
    Returns
    --------
    exposure_funcs : dict 
        Dictionairy containing the exposure functions
    survival_data : DataFrame
        Pandas DataFrame containing the treatments as columns and times as index
    num_expos : int
        Number of different expositions that the organisms are subject to. This will be one in the standard guts models but e.g. the number of substances
        used in the exposure when considering a guts-mixtures model.
    info_dict : dict, optional
        Contents of the info datasheet, only returned if 'with_info_dict'=True
    """
    file = pd.ExcelFile(os.path.join(path, file_name))
    exposure_sheets = [exp for exp in file.sheet_names if exposure_name in str(exp)]
    num_expos = len(exposure_sheets)
    if num_expos < 1:
        raise ValueError(f'No sheet named {exposure_name} in the Excel file')
    else:
        exposure_funcs = {}
        raw_exposure_data = {}
        for exposure_sheet in exposure_sheets:
            exposure_data = file.parse(sheet_name=exposure_sheet,index_col=0, na_values=na_values)
            raw_exposure_data.update({exposure_sheet: exposure_data})
            
            # maybe this needs to be done after collecting all sheets and removing nan treatments
            exposure_funcs[exposure_sheet] = multi_interp_treatment_generator(exposure_data)

    survival_data = file.parse(sheet_name=survival_name,index_col=0)

    assert_identical_column_names(
        exposure_data=raw_exposure_data, 
        survival_data=survival_data
    )

    test_for_increasing_survival(survival_data=survival_data)

    if visualize:
        plot(exposure_funcs, survival_data)
    
    return_data = [exposure_funcs, survival_data, num_expos]

    if with_info_dict:
        df_info = file.parse( header=None, sheet_name=info_name)
        info_array = df_info.to_numpy()
        info_dict = {info[0]:info[1:] for info in info_array}
        return_data += [info_dict]

    if with_raw_exposure_data:
        return_data += [raw_exposure_data]

    return tuple(return_data)


def test_for_nans_in_exposure_data(exposure_data):
    # this needs to check all exposure sheets for nans, and eliminate these rows 
    # from all other datasets
    # problem: How to identify nans as nans. Perhaps this needs to be done manually.
    pass



def test_for_increasing_survival(survival_data):
    increasing_ids = survival_data.diff().max() > 0

    has_increasing_survival = False
    messages = []
    for _id, is_increasing in increasing_ids.items():
        if is_increasing:
            has_increasing_survival = True
            increasing_time = survival_data.loc[:, _id].diff() > 0
            increasing_time = survival_data.index[increasing_time]

            change_list = []
            for time_at in increasing_time:
                loc_increase = survival_data.index.get_loc(time_at)
                time_before = survival_data.index[loc_increase - 1]
                time_after = survival_data.index[loc_increase + 1]

                value_at = survival_data.loc[time_at, _id]
                value_before = survival_data.loc[time_before, _id]
                value_after = survival_data.loc[time_after, _id]

                msg_detail = "{tbe}:{vbe}->{tat}:{vat}->{taf}:{vaf}".format(
                    tbe=time_before, vbe=value_before,
                    tat=time_at, vat=value_at, 
                    taf=time_after, vaf=value_after
                )
                change_list.append(msg_detail)

            details = [f"{d}" for v, d in zip(increasing_time.values, change_list)]
            msg = f"id={_id} has increasing survival at [{survival_data.index.name}:survival]={details}"
            messages.append(msg)
            print(msg)

    if has_increasing_survival:
        raise MempyError(
            "Survival data contain increasing values over time. " +
            "Survival data with increasing values (from e.g. independent populations " +
            "without repeated observations) need a standard binomial error distribution, " +
            "which is currently not implemented. " +
            "Are you sure you mean to have increasing survival in your dataset?"+
            "The following ids have increasing survival values: \n - " + 
            "\n - ".join(messages)
        )

def read_excel_file(
    path: str, 
    sheet_name_prefix: str, 
    convert_time_to: Optional[str] = None
) -> Tuple[Dict[str, pd.DataFrame], pint.Unit]: 
    """Reads a file and extracts the column name and time unit from the first column
    if needed converts the time unit to a different unit.

    Parameters
    ----------

    sheet_name_prefix : str
        The name of the sheet or a common prefix for multiple sheets

    convert_time_to : Optional[str]
        Unit to convert the time vector to. Works only if the column has a time unit given
        in parentheses. E.g time [d], or time (seconds), or time [hours]. Any common time
        denotion works (see the documentation of pint: https://pint.readthedocs.io/en/stable/)
    """
    file = pd.ExcelFile(path)
    sheets = [
        name for name in file.sheet_names 
        if name.startswith(sheet_name_prefix)
    ]

    _data = {}
    for sheet in sheets:
        df = file.parse(sheet_name=sheet)

        time_name, time_unit = extract_value_from_brackets(df.columns[0])
        if time_unit is not None:
            parsed_time_unit = ureg(time_unit)
        else:
            warnings.warn(
                "No time unit found in the first column. You're playing a dangerous game. " +
                "Better be explicit and indicate the time unit (e.g. 'time [d]' or 'time [seconds]')"
            )

        df = df.rename(columns={df.columns[0]: time_name})
        df = df.set_index(time_name)

        if convert_time_to is not None:
            converted_time_unit = parsed_time_unit.to(convert_time_to)
            df.index = df.index * converted_time_unit.magnitude
        else:
            converted_time_unit = parsed_time_unit

        _data.update({sheet: df})

    return _data, converted_time_unit.units

def extract_value_from_brackets(text):
    """
    Extracts the value inside square or normal brackets from a string.

    Args:
        text: The input string.

    Returns:
        The value inside the brackets, or None if no brackets are found.
    """
    match_square = re.search(r"\[(.*?)\]", text)  #The regex here is the key part
    match_normal = re.search(r"\((.*?)\)", text)  #The regex here is the key part
    if match_square:
        bracket = match_square.group(1)  # group(1) captures the content inside the parentheses
        # Remove bracket and content, then trim spaces
        _text = text.replace(match_square.group(0), "").replace(" ","")
        return _text, bracket
    elif match_normal:
        bracket = match_normal.group(1)  # group(1) captures the content inside the parentheses
        _text = text.replace(match_normal.group(0), "").replace(" ","")
        return _text, bracket
    else:
        return text.strip(), None

def assert_identical_column_names(exposure_data, survival_data):
    """This function compares only the names of the columns (treatments)
    It does not compare identity of the time column names
    """
    columns = {}
    for key, df in exposure_data.items():
        c = df.columns.values
        columns.update({key: c})

    c = survival_data.columns.values
    columns.update({"Survival": c})

    column_df = pd.DataFrame(columns)
    column_df['matching'] = column_df.eq(column_df.iloc[:, 0], axis=0).all(1)

    if all(column_df["matching"]):
        return
    else:
        raise MempyError(
            "Mismatch in column names detected between survival and exposure sheets.\n" +
            "All columns in the spreadsheets are listed below. Please fix the non-matching " +
            "column names (indicated as matching->False):"+
            "\n\n" +
            str(column_df)
        )

def get_xc(treatment, exposure_funcs):
    '''
    Extracts every exposure-function for a given treatment.

    Parameters
    ----------
    treatment: String
        Name of the treatment to be handled.
    exposure_funcs: dict
        Dictionary of the exposures and treamtents containing the exposure-functions.
    
    Returns
    ----------
    xc: Tuple
        Tuple containing all exposure-functions for the given treatment.
    '''
    xc_list = []
    for exposure in exposure_funcs:
        xc_list.append(exposure_funcs[exposure][treatment])
    xc = tuple(xc_list)
    return xc


def split_control_treatment_dataset(datasets):
    """
    Splits a dataset into control and treatment datasets

    Parameters
    ----------
    datasets: dict
        A dictionary of all datasets that should be categorized.

    Returns
    ----------
    control_datasets: dict
        A dictionary containing the control datasets
    treat_datasets: dict
        A dictionary containing all other datasets
    """
    control_datasets = []
    treat_datasets = []
    for dataset in datasets:
        if "control" in dataset[-1].name.lower().strip():
            control_datasets.append(dataset)
        else:
            treat_datasets.append(dataset)

    return control_datasets, treat_datasets 


def plot(exposure_funcs, survival_data):
    """
    Visualizes the Exposure- and Survival-data as imported by the input_data.read_exposure_survival()-function.

    Parameters
    ----------
    exposure_funcs: dict
        Dictionary of functions representing the time dependant external exposure to be visualized
    survival_data: pandas.DataFrame
        Table of survival-data to be visualized
    """
    fig, ax = plt.subplots()
    times = survival_data.index
    for col in survival_data.columns:
        ax.plot(times, survival_data[col], label = col)
    ax.legend()
    ax.set(xlabel='Time', ylabel='Survival', title='Observed survival per treatment over Time')
    plt.show()

    fig, ax = plt.subplots()
    for substance in exposure_funcs.keys():
        for treatment in exposure_funcs[substance].keys():
            times = np.linspace(exposure_funcs[substance][treatment].get_knots()[0],exposure_funcs[substance][treatment].get_knots()[-1], 1000)
            ax.plot(times, exposure_funcs[substance][treatment](times), label = treatment)
    ax.legend()
    ax.set(xlabel='Time', ylabel='Concentration', title='Exposure-Concentrations/Treatments over Time')
    plt.show()
