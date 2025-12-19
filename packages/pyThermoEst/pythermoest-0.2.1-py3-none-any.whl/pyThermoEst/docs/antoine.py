# import libs
import logging
from typing import List, Tuple, Optional, Literal
import numpy as np
from pythermodb_settings.models import Temperature, Pressure
from pathlib import Path
import pycuc
# local
from ..core import Antoine
from ..util import normalize_unit
from ..models.antoine import AntoineFitResult

# NOTE: set up logger
logger = logging.getLogger(__name__)


def estimate_coefficients(
    temperatures: List[Temperature],
    pressures: List[Pressure],
    *,
    base: Literal['log10', 'ln'] = "log10",
    fit_in_log_space: bool = True,
    weights: Optional[np.ndarray] = None,
    x0: Optional[Tuple[float, float, float]] = None,
    bounds: Optional[
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float]
        ]
    ] = None,
    max_nfev: int = 5000,
    validate: bool = True,
    min_margin_kelvin: float = 1.0,
    # robust options
    loss: Literal['linear', 'soft_l1', 'huber', 'cauchy', 'arctan'] = "linear",
    f_scale: Optional[float] = None,
) -> Optional[AntoineFitResult]:
    """
    Estimate Antoine coefficients from experimental data to fit the Antoine equation as follows:

        log10(P) = A - B / (T + C)   (if base is "log10")
        ln(P)   = A - B / (T + C)    (if base is "ln")

    Parameters
    ----------
    temperatures : List[Temperature]
        List of Temperature models containing temperature values and units.
    pressures : List[Pressure]
        List of Pressure models containing pressure values and units.
    base : str, optional
        Logarithm base used in the Antoine equation ('log10' or 'ln'), by default "log10".
    fit_in_log_space : bool, optional
        Whether to perform fitting in logarithmic space, by default True.
    weights : Optional[np.ndarray], optional
        Optional weights for each data point, by default None.
    x0 : Optional[Tuple[float, float, float]], optional
        Initial guess for coefficients (A, B, C), by default None.
    bounds : Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]], optional
        Bounds for coefficients (A, B, C), by default None.
    max_nfev : int, optional
        Maximum number of function evaluations for the optimizer, by default 5000.
    validate : bool, optional
        Whether to perform validation checks on the fitted coefficients, by default True.
    min_margin_kelvin : float, optional
            Minimum margin for (T + C) to avoid denominator issues (default 1.0 K).
    loss : str, Literal['linear', 'soft_l1', 'huber', 'cauchy', 'arctan'], optional
        Loss function for robust fitting: 'linear', 'soft_l1', 'huber', 'cauchy', 'arctan' (default 'linear').
    f_scale : Optional[float], optional
        Scaling parameter for robust loss (default None = auto).

    Returns
    -------
    Optional[AntoineFitResult]
        An AntoineFitResult model containing fitted coefficients and metrics, or None if estimation fails defined as:
        - A: float
            Fitted coefficient A.
        - B: float
            Fitted coefficient B.
        - C: float
            Fitted coefficient C.
        - base: str
            Logarithm base used in the Antoine equation.
        - p_unit: str
            Unit of pressure used.
        - T_unit_internal: str
            Internal unit of temperature used.
        - fit_in_log_space: bool
            Whether fitting was done in logarithmic space.
        - success: bool
            Whether the fitting was successful.
        - message: str
            Message regarding the fitting process.
        - cost: float
            Final cost value from the fitting.
        - rmse_logP: float
            Root Mean Square Error in log space.
        - mae_logP: float
            Mean Absolute Error in log space.
        - r2_logP: float
            R-squared value in log space.
        - rmse_P: float
            Root Mean Square Error in original pressure space.
        - mae_P: float
            Mean Absolute Error in original pressure space.
        - cov: Any
            Covariance matrix of the fitted parameters.
        - warnings: List[str]
            List of warnings generated during fitting.
        - Tmin_K: float
            Minimum temperature in Kelvin from the data.
        - Tmax_K: float
            Maximum temperature in Kelvin from the data.
        - loss: Any
            Loss function used.
        - f_scale: float
            Scaling parameter used for robust fitting.
    """
    try:
        # SECTION: Validate inputs
        # NOTE: check lengths
        if len(temperatures) != len(pressures):
            logger.error("Lengths of temperatures and pressures do not match.")
            return None

        # >> check types
        if not all(isinstance(t, Temperature) for t in temperatures):
            logger.error(
                "All items in temperatures must be of type Temperature."
            )
            return None

        if not all(isinstance(p, Pressure) for p in pressures):
            logger.error("All items in pressures must be of type Pressure.")
            return None

        # SECTION: Normalize units
        # NOTE: normalize temperatures to Kelvin
        norm_temperature = normalize_unit(
            data=temperatures,
            to_unit="K",
            valid_from=["C", "F", "K", "R"]
        )

        norm_pressures = normalize_unit(
            data=pressures,
            to_unit="Pa",
            valid_from=["Pa", "kPa", "bar", "atm", "psi"]
        )

        if not norm_temperature or not norm_pressures:
            logger.error("Normalization of units failed.")
            return None

        # SECTION: Extract values
        temp_values = norm_temperature.get('data', [])
        # >> to array
        temp_values = np.array(temp_values)

        pres_values = norm_pressures.get('data', [])
        # >> to array
        pres_values = np.array(pres_values)

        if len(temp_values) != len(pres_values):
            logger.error(
                "Normalized temperature and pressure data lengths do not match.")
            return None

        # SECTION: Estimate coefficients
        antoine_model = Antoine.fit_antoine(
            T_data=temp_values,
            P_data=pres_values,
            base=base,
            T_unit="K",
            p_unit="Pa",
            fit_in_log_space=fit_in_log_space,
            weights=weights,
            x0=x0,
            bounds=bounds,
            max_nfev=max_nfev,
            validate=validate,
            min_margin_kelvin=min_margin_kelvin,
            loss=loss,
            f_scale=f_scale,
        )

        # >> return result model
        return AntoineFitResult(**antoine_model)
    except Exception as e:
        logger.exception(
            f"An error occurred during coefficient estimation: {e}")
        return None


def estimate_coefficients_from_experimental_data(
    experimental_data: str | Path,
    *,
    temperature_unit: Literal['K', 'C', 'F', 'R'] = 'K',
    pressure_unit: Literal['Pa', 'kPa', 'bar', 'atm', 'psi'] = 'Pa',
    base: str = "log10",
    fit_in_log_space: bool = True,
    weights: Optional[np.ndarray] = None,
    x0: Optional[Tuple[float, float, float]] = None,
    bounds: Optional[
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float]
        ]
    ] = None,
    max_nfev: int = 5000,
    validate: bool = True,
    min_margin_kelvin: float = 1.0,
    # robust options
    loss: str = "linear",
    f_scale: Optional[float] = None,
) -> Optional[AntoineFitResult]:
    """
    Estimate Antoine coefficients from experimental data to fit the Antoine equation as follows:

        log10(P) = A - B / (T + C)   (if base is "log10")
        ln(P)   = A - B / (T + C)    (if base is "ln")

    Parameters
    ----------
    experimental_data : str | Path
        Path to experimental data file (CSV, JSON, etc.) containing temperature and pressure data.
    base : str, optional
        Logarithm base used in the Antoine equation ('log10' or 'ln'), by default "log10".
    fit_in_log_space : bool, optional
        Whether to perform fitting in logarithmic space, by default True.
    weights : Optional[np.ndarray], optional
        Optional weights for each data point, by default None.
    x0 : Optional[Tuple[float, float, float]], optional
        Initial guess for coefficients (A, B, C), by default None.
    bounds : Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]], optional
        Bounds for coefficients (A, B, C), by default None.
    max_nfev : int, optional
        Maximum number of function evaluations for the optimizer, by default 5000.
    validate : bool, optional
        Whether to perform validation checks on the fitted coefficients, by default True.
    min_margin_kelvin : float, optional
        Minimum margin in Kelvin to ensure valid temperature range, by default 1.0.
    loss : str, optional
        Loss function for robust fitting, by default "linear".
    f_scale : Optional[float], optional
        Scale parameter for robust fitting, by default None.

    Returns
    -------
    Optional[AntoineFitResult]
        An AntoineFitResult model containing fitted coefficients and metrics, or None if estimation fails defined as:
        - A: float
            Fitted coefficient A.
        - B: float
            Fitted coefficient B.
        - C: float
            Fitted coefficient C.
        - base: str
            Logarithm base used in the Antoine equation.
        - p_unit: str
            Unit of pressure used.
        - T_unit_internal: str
            Internal unit of temperature used.
        - fit_in_log_space: bool
            Whether fitting was done in logarithmic space.
        - success: bool
            Whether the fitting was successful.
        - message: str
            Message regarding the fitting process.
        - cost: float
            Final cost value from the fitting.
        - rmse_logP: float
            Root Mean Square Error in log space.
        - mae_logP: float
            Mean Absolute Error in log space.
        - r2_logP: float
            R-squared value in log space.
        - rmse_P: float
            Root Mean Square Error in original pressure space.
        - mae_P: float
            Mean Absolute Error in original pressure space.
        - cov: Any
            Covariance matrix of the fitted parameters.
        - warnings: List[str]
            List of warnings generated during fitting.
        - Tmin_K: float
            Minimum temperature in Kelvin from the data.
        - Tmax_K: float
            Maximum temperature in Kelvin from the data.
        - loss: Any
            Loss function used.
        - f_scale: float
            Scaling parameter used for robust fitting.
    """
    try:
        # SECTION: Check inputs
        # >> check file existence
        data_path = Path(experimental_data)

        if not data_path.exists() or not data_path.is_file():
            logger.error(
                f"Experimental data file does not exist: {experimental_data}")
            return None

        # SECTION: Load experimental data by Antoine class method
        # >> load data
        # ! temperature in K, pressure in bar
        T_data, P_data = Antoine.load_experimental_data(
            experimental_data=data_path,
            T_unit=temperature_unit,
            P_unit=pressure_unit,
        )

        if T_data is None or P_data is None:
            logger.error(
                "Failed to load experimental data from the provided file.")
            return None

        # SECTION: Estimate coefficients
        antoine_model = Antoine.fit_antoine(
            T_data=T_data,
            P_data=P_data,
            base=base,
            T_unit="K",
            p_unit="Pa",
            fit_in_log_space=fit_in_log_space,
            weights=weights,
            x0=x0,
            bounds=bounds,
            max_nfev=max_nfev,
            validate=validate,
            min_margin_kelvin=min_margin_kelvin,
            loss=loss,
            f_scale=f_scale,
        )

        # >> return result model
        return AntoineFitResult(**antoine_model)
    except Exception as e:
        logger.exception(
            f"An error occurred during coefficient estimation from experimental data: {e}")
        return None


def calc_vapor_pressure(
    temperature: Temperature,
    A: float,
    B: float,
    C: float,
    *,
    base: Literal['log10', 'ln'] = 'log10',
    pressure_unit: Literal['Pa', 'kPa', 'bar', 'atm', 'psi'] = 'Pa',
) -> Optional[Pressure]:
    """
    Calculate vapor pressure using the Antoine equation given temperature and Antoine coefficients. The Antoine equation is defined as:

        log10(P) = A - B / (T + C)   (if base is "log10")
        ln(P)   = A - B / (T + C)    (if base is "ln")

    Finally, the vapor pressure is returned in the specified pressure unit as:

        P = 10^(A - B / (T + C))   (if base is "log10")
        P = exp(A - B / (T + C))    (if base is "ln")

    Parameters
    ----------
    temperature : Temperature
        Temperature model containing value and unit.
    A : float
        Antoine coefficient A.
    B : float
        Antoine coefficient B.
    C : float
        Antoine coefficient C.
    base : str, optional
        Logarithm base used in the Antoine equation ('log10' or 'ln'), by default 'log10'.
    pressure_unit : str, optional
        Desired unit for the output pressure ('Pa', 'kPa', 'bar', 'atm', 'psi'), by default 'Pa'.

    Returns
    -------
    Optional[Pressure]
        Calculated saturation pressure as a Pressure model in Pa, or None if calculation fails.
    """
    try:
        # SECTION: Normalize temperature to Kelvin
        norm_temperature = normalize_unit(
            data=[temperature],
            to_unit="K",
            valid_from=["C", "F", "K", "R"]
        )

        if not norm_temperature:
            logger.error("Normalization of temperature unit failed.")
            return Pressure(value=np.nan, unit="Pa")

        T_k = norm_temperature.get('data', [])[0]

        # SECTION: Calculate saturation pressure
        res_calc = Antoine.calc(
            T_value=T_k,
            T_unit="K",
            A=A,
            B=B,
            C=C,
            base=base,
        )

        # >> check result
        if res_calc is None:
            logger.error("Antoine calculation returned None.")
            return None

        res = Pressure(value=res_calc['vapor_pressure'], unit="Pa")

        # NOTE: convert to desired pressure unit
        if pressure_unit != "Pa":
            res_ = pycuc.convert_from_to(
                value=res.value,
                from_unit="Pa",
                to_unit=pressure_unit,
            )
            # res
            return Pressure(value=res_, unit=pressure_unit)

        return res
    except Exception as e:
        logger.exception(f"An error occurred during pressure calculation: {e}")
        return None
