# import libs
from __future__ import annotations
import logging
import pandas as pd
import numpy as np
import math
from typing import Optional, Tuple, Dict, Any, List
from scipy.optimize import least_squares
from pathlib import Path
import pycuc
# local

# NOTE: set up logger
logger = logging.getLogger(__name__)


class Antoine:
    """
    Pure component vapor pressure model using Antoine equation as follows:

    - VaPr(T) = 10^(A - B/(T + C))
    - VaPr(T) = exp(A - B/(T + C))
    """

    def __init__(self):
        """
        Initialize with vapor pressure and derivative functions.
        """
        pass

    @staticmethod
    def fit_antoine(
        T_data: np.ndarray,
        P_data: np.ndarray,
        *,
        base: str = "log10",
        T_unit: str = "K",
        p_unit: str = "Pa",
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
    ) -> Dict[str, Any]:
        """
        Fit Antoine coefficients (A,B,C) to experimental VaPr(T) data.

        - Supports T in K or °C via T_unit.
        - Supports P in Pa or bar via p_unit.
        - Recommended: fit_in_log_space=True.
        - Robust fitting supported via loss + f_scale.

        Parameters
        ----------
        T_data : np.ndarray
            Array of temperature data points.
        P_data : np.ndarray
            Array of vapor pressure data points.
        base : str, optional
            Logarithm base for Antoine equation: 'log10' or 'ln' (default 'log10').
        T_unit : str, optional
            Unit of temperature data: 'K' or 'C' (default 'K').
        p_unit : str, optional
            Unit of pressure data: 'Pa' or 'bar' (default 'Pa').
        fit_in_log_space : bool, optional
            If True, fit in log space; else fit in pressure space (default True).
        weights : Optional[np.ndarray], optional
            Optional weights for each data point (default None = equal weights).
        x0 : Optional[Tuple[float, float, float]], optional
            Initial guess for (A, B, C) (default None = auto guess).
        bounds : Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]], optional
                Bounds for (A, B, C) (default None = wide bounds).
        max_nfev : int, optional
            Maximum number of function evaluations (default 5000).
        validate : bool, optional
            If True, perform fit validation checks (default True).
        min_margin_kelvin : float, optional
            Minimum margin for (T + C) to avoid denominator issues (default 1.0 K).
        loss : str, optional
            Loss function for robust fitting: 'linear', 'soft_l1', 'huber', 'cauchy', 'arctan' (default 'linear').
        f_scale : Optional[float], optional
            Scaling parameter for robust loss (default None = auto).

        Returns
        -------
        Dict[str, Any]
            Returns a fit report dict with coefficients, metrics, warnings, and solver info.
        """
        # SECTION: Input validation and conversion
        # NOTE: Convert inputs to arrays
        T = np.asarray(T_data, dtype=float).ravel()
        P = np.asarray(P_data, dtype=float).ravel()

        # Check sizes
        if T.size != P.size or T.size < 3:
            logger.error(
                "T_data and P_data must have same length and at least 3 points.")
            return {}

        # NOTE: Normalize string inputs
        T_unit = T_unit.lower()
        base = base.lower()
        p_unit = p_unit.lower()
        loss = loss.lower()

        # >> Convert temperature to K
        if T_unit in ("k", "kelvin"):
            T_k = T
        elif T_unit in ("c", "degc", "celsius", "°c"):
            T_k = T + 273.15
        else:
            logger.error("T_unit must be 'K' or 'C'.")
            return {}

        # >> Convert pressure to Pa
        if p_unit == "pa":
            P_pa = P
        elif p_unit == "bar":
            P_pa = P * 1e5
        elif p_unit == "kpa":
            P_pa = P * 1e3
        elif p_unit == "atm":
            P_pa = P * 101325.0
        elif p_unit == "psi":
            P_pa = P * 6894.76
        else:
            logger.error("p_unit must be 'Pa' or 'bar'.")
            return {}

        # >> Check pressures > 0
        if np.any(P_pa <= 0):
            logger.error("All pressures must be > 0 for Antoine fitting.")
            return {}

        # NOTE: Choose log target
        if base == "log10":
            y = np.log10(P_pa)
        elif base == "ln":
            y = np.log(P_pa)
        else:
            logger.error("base must be 'log10' or 'ln'.")
            return {}

        # NOTE: weights (sqrt form)
        if weights is None:
            w = np.ones_like(T_k)
        else:
            w_raw = np.asarray(weights, dtype=float).ravel()
            if w_raw.size != T_k.size:
                logger.error("weights must have same length as data.")
                return {}

            # Ensure non-negative weights
            w = np.sqrt(np.clip(w_raw, 0.0, np.inf))

        # SECTION: Define model and residuals
        def model_log(params: np.ndarray) -> np.ndarray:
            A_, B_, C_ = params
            return A_ - B_ / (T_k + C_)

        # NOTE: Define residuals
        if fit_in_log_space:
            def residuals(params: np.ndarray) -> np.ndarray:
                return w * (model_log(params) - y)
        else:
            if base == "log10":
                def Pmodel(params: np.ndarray) -> np.ndarray:
                    return 10.0 ** model_log(params)
            else:
                def Pmodel(params: np.ndarray) -> np.ndarray:
                    return np.exp(model_log(params))

            def residuals(params: np.ndarray) -> np.ndarray:
                return w * (Pmodel(params) - P_pa)

        # NOTE: Initial guess
        if x0 is None:
            C0 = -50.0
            if np.min(T_k + C0) <= min_margin_kelvin:
                # ! C0 too low, adjust
                C0 = -np.min(T_k) + 10.0

            # ! A0: mean logP
            A0 = float(np.mean(y))

            # ! B0: from rough slope
            m, _b = np.polyfit(1.0 / T_k, y, 1)

            Tmean = float(np.mean(T_k))
            ratio = (float(np.mean(T_k + C0)) / Tmean) ** 2
            B0 = float(abs(m) * ratio)

            # >> sanity check B0
            if not np.isfinite(B0) or B0 <= 1e-6:
                B0 = 2000.0

            # ! > assemble x0
            x0 = (A0, B0, C0)

        # >> Convert x0 to array
        x0_array = np.asarray(x0, dtype=float)

        # NOTE: Default bounds
        if bounds is None:
            bounds = ((-200.0, 1e-6, -1e4), (200.0, 1e7, 1e4))

        # NOTE: Auto f_scale for robust loss if not provided
        if f_scale is None:
            if loss != "linear":
                f_scale = 0.02 if fit_in_log_space else max(
                    1.0, float(np.median(P_pa) * 0.02))
            else:
                f_scale = 1.0

        # SECTION: Perform least squares fitting
        res = least_squares(
            residuals,
            x0=x0_array,
            bounds=bounds,
            max_nfev=max_nfev,
            loss=loss,
            f_scale=float(f_scale),
        )

        # NOTE: Extract fitted parameters
        A, B, C = map(float, res.x)

        # NOTE: Predictions and metrics
        y_hat = A - B / (T_k + C)
        if base == "log10":
            P_hat = 10.0 ** y_hat
        else:
            P_hat = np.exp(y_hat)

        log_res = y_hat - y

        # NOTE: Metrics
        rmse_log = float(np.sqrt(np.mean(log_res ** 2)))
        mae_log = float(np.mean(np.abs(log_res)))

        P_res = P_hat - P_pa
        rmse_P = float(np.sqrt(np.mean(P_res ** 2)))
        mae_P = float(np.mean(np.abs(P_res)))

        y_mean = float(np.mean(y))
        ss_res = float(np.sum((y - y_hat) ** 2))
        ss_tot = float(np.sum((y - y_mean) ** 2))
        r2_log = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")

        # NOTE: Covariance estimate (approx)
        cov = None
        try:
            J = res.jac
            dof = max(1, T_k.size - 3)
            s2 = 2.0 * float(res.cost) / dof
            cov = (s2 * np.linalg.inv(J.T @ J)).tolist()
        except Exception:
            cov = None

        # SECTION: Validation checks
        warnings: List[str] = []
        if validate:
            denom_min = float(np.min(T_k + C))
            if denom_min <= min_margin_kelvin:
                warnings.append(
                    f"Risky fit: min(T + C) = {denom_min:.6g} K (<= {min_margin_kelvin} K). "
                    "Denominator near zero can make the fit unstable."
                )

            idx = np.argsort(T_k)
            if np.any(np.diff(P_hat[idx]) <= 0):
                warnings.append(
                    "Non-physical trend: fitted VaPr(T) is not strictly increasing over the data range.")

            if B < 10.0:
                warnings.append(
                    "Unusually small B; data range may be too narrow or units may be inconsistent.")
            if B > 1e6:
                warnings.append(
                    "Very large B; check units and outliers in experimental data.")

        # SECTION: Return fit report
        return {
            "A": A,
            "B": B,
            "C": C,
            "base": base,
            "p_unit": "Pa",
            "T_unit_internal": "K",
            "fit_in_log_space": bool(fit_in_log_space),
            "success": bool(res.success),
            "message": str(res.message),
            "cost": float(res.cost),
            "rmse_logP": rmse_log,
            "mae_logP": mae_log,
            "r2_logP": r2_log,
            "rmse_P": rmse_P,
            "mae_P": mae_P,
            "cov": cov,
            "warnings": warnings,
            "Tmin_K": float(np.min(T_k)),
            "Tmax_K": float(np.max(T_k)),
            # robust metadata
            "loss": loss,
            "f_scale": float(f_scale),
        }

    @staticmethod
    def _robust_weight(loss: str, z: float) -> float:
        """
        Approx IRLS-like weight for standardized residual z = r / f_scale.

        Parameters
        ----------
        loss : str
            Loss function: 'linear', 'soft_l1', 'huber', 'cauchy', 'arctan'.
        z : float
            Standardized residual.

        Returns
        -------
        float
            Robust weight for the given standardized residual.
        """
        a = abs(z)
        loss = loss.lower()

        if loss == "linear":
            return 1.0
        if loss == "soft_l1":
            return 1.0 / math.sqrt(1.0 + z * z)
        if loss == "huber":
            return 1.0 if a <= 1.0 else 1.0 / a
        if loss == "cauchy":
            return 1.0 / (1.0 + z * z)
        if loss == "arctan":
            return 1.0 / (1.0 + z * z)

        return 1.0

    @classmethod
    def outlier_report(
        cls,
        T_data: np.ndarray,
        P_data: np.ndarray,
        fit_report: Dict[str, Any],
        *,
        T_unit: str = "K",
        p_unit: str = "Pa",
        top_n: int = 10,
        residual_domain: str = "log",  # "log" or "P"
    ) -> List[Dict[str, Any]]:
        """
        Rank points by robust down-weighting and standardized residual magnitude.

        Parameters
        ----------
        T_data : np.ndarray
            Array of temperature data points.
        P_data : np.ndarray
            Array of vapor pressure data points.
        fit_report : Dict[str, Any]
            Fit report dict from fit_antoine().
        T_unit : str, optional
            Unit of temperature data: 'K' or 'C' (default 'K').
        p_unit : str, optional
            Unit of pressure data: 'Pa' or 'bar' (default 'Pa').
        top_n : int, optional
            Number of top outliers to report (default 10).
        residual_domain : str, optional
            Domain for residuals: 'log' or 'P' (default 'log').

        Returns
        -------
        List[Dict[str, Any]]
            Returns a list of dicts with:
            - index,
            - T_K,
            - P_input_Pa,
            - P_fit_Pa,
            - residual,
            - standardized_residual,
            - robust_weight
        """
        residual_domain = residual_domain.lower()

        T = np.asarray(T_data, dtype=float).ravel()
        P = np.asarray(P_data, dtype=float).ravel()

        if T_unit.lower() in ("c", "degc", "celsius", "°c"):
            T_k = T + 273.15
        else:
            T_k = T

        if p_unit.lower() == "bar":
            P_pa = P * 1e5
        elif p_unit.lower() == "pa":
            P_pa = P
        elif p_unit.lower() == "kpa":
            P_pa = P * 1e3
        elif p_unit.lower() == "atm":
            P_pa = P * 101325.0
        elif p_unit.lower() == "psi":
            P_pa = P * 6894.76
        else:
            P_pa = P

        A, B, C = float(fit_report["A"]), float(
            fit_report["B"]), float(fit_report["C"])
        base = str(fit_report.get("base", "log10")).lower()
        loss = str(fit_report.get("loss", "linear")).lower()
        f_scale = float(fit_report.get("f_scale", 1.0))

        y_hat = A - B / (T_k + C)
        if base == "log10":
            y = np.log10(P_pa)
            P_hat = 10.0 ** y_hat
        else:
            y = np.log(P_pa)
            P_hat = np.exp(y_hat)

        if residual_domain == "log":
            r = y_hat - y
        elif residual_domain == "p":
            r = P_hat - P_pa
        else:
            logger.error("residual_domain must be 'log' or 'P'.")
            return []

        # Standardized residuals
        z = r / f_scale if f_scale > 0 else np.zeros_like(r, dtype=float)
        w_rob = np.array(
            [cls._robust_weight(loss, zi) for zi in z],
            dtype=float
        )

        # Sort: smallest weight first, then largest standardized residual
        order = np.argsort(w_rob + 1e-12)  # primary by weight
        # refine within same-ish weights by |z|
        # secondary by abs(z), descending
        order = order[np.argsort(np.abs(z[order]))[::-1]]
        order = order[: min(top_n, order.size)]

        out: List[Dict[str, Any]] = []
        for i in order:
            out.append(
                {
                    "index": int(i),
                    "T_K": float(T_k[i]),
                    "P_input_Pa": float(P_pa[i]),
                    "P_fit_Pa": float(P_hat[i]),
                    "residual": float(r[i]),
                    "standardized_residual": float(z[i]),
                    "robust_weight": float(w_rob[i]),
                }
            )
        return out

    @staticmethod
    def load_experimental_data(
        experimental_data: str | Path,
        T_unit: str,
        P_unit: str,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load experimental data from CSV file, then convert to arrays. The CSV file must contain 'Temperature' and 'Pressure' columns. Temperature and pressure units are specified via T_unit and P_unit, the defaults being 'K' and 'Pa' respectively.

        Parameters
        ----------
        experimental_data : str | Path
            Path to CSV file with 'Temperature' and 'Pressure' columns.
        T_unit : str
            Unit of temperature data: 'K' or 'C'.
        P_unit : str
            Unit of pressure data: 'Pa' or 'bar'.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Arrays of temperatures and pressures.
        """
        try:
            # SECTION: Load data
            df = pd.read_csv(experimental_data)

            # NOTE: Validate columns
            df_columns_lower = [col.strip().lower() for col in df.columns]

            # >> check columns
            if 'temperature' not in df_columns_lower or 'pressure' not in df_columns_lower:
                logger.error(
                    "CSV file must contain 'Temperature' and 'Pressure' columns.")
                return np.array([]), np.array([])
            # >> get actual column names
            temp_col = df.columns[df_columns_lower.index('temperature')]
            pres_col = df.columns[df_columns_lower.index('pressure')]

            # >> check data types
            if df[temp_col].dtype not in [np.float64, np.float32, np.int64, np.int32]:
                logger.error(
                    "'Temperature' column must contain numeric data.")
                return np.array([]), np.array([])

            if df[pres_col].dtype not in [np.float64, np.float32, np.int64, np.int32]:
                logger.error(
                    "'Pressure' column must contain numeric data.")
                return np.array([]), np.array([])

            # NOTE: >> to arrays
            temperatures = df[temp_col]
            # >> Unit conversions
            temperatures = [
                pycuc.convert_from_to(
                    float(T_val),
                    from_unit=T_unit,
                    to_unit='K'
                ) for T_val in temperatures
            ]

            pressures = df[pres_col]
            pressures = [
                pycuc.convert_from_to(
                    float(P_val),
                    from_unit=P_unit,
                    to_unit='Pa'
                ) for P_val in pressures
            ]

            # SECTION: to arrays
            pressures = np.array(pressures, dtype=float)
            temperatures = np.array(temperatures, dtype=float)

            return temperatures, pressures
        except Exception as e:
            logger.exception(
                f"Failed to load experimental data: {e}")
            return np.array([]), np.array([])

    @staticmethod
    def calc(
        T_value: float,
        T_unit: str,
        A: float,
        B: float,
        C: float,
        base: str = "log10",
    ) -> Optional[Dict[str, float]]:
        """
        Calculate vapor pressure at given temperature using Antoine equation.

        Parameters
        ----------
        T_value : float
            Temperature value.
        T_unit : str
            Unit of temperature: 'K' or 'C'.
        A : float
            Antoine coefficient A.
        B : float
            Antoine coefficient B.
        C : float
            Antoine coefficient C.
        base : str, optional
            Logarithm base: 'log10' or 'ln' (default 'log10').

        Returns
        -------
        Optional[Dict[str, float]]
            Dict with 'temperature' in Kelvin and 'vapor_pressure' in Pa entries, or None on failure.
        """
        try:
            # >> Convert T to K
            if T_unit.lower() in ("k", "kelvin"):
                T_k = T_value
            elif T_unit.lower() in ("c", "degc", "celsius", "°c"):
                T_k = T_value + 273.15
            else:
                logger.error("T_unit must be 'K' or 'C'.")
                return None

            # >> Calculate logP
            if base.lower() == "log10":
                logP = A - B / (T_k + C)
                P_pa = 10.0 ** logP
            elif base.lower() == "ln":
                logP = A - B / (T_k + C)
                P_pa = np.exp(logP)
            else:
                logger.error("base must be 'log10' or 'ln'.")
                return None

            return {
                "temperature": T_k,
                "vapor_pressure": P_pa
            }
        except Exception as e:
            logger.exception(f"Failed to calculate vapor pressure: {e}")
            return None
