"""
stock-options-python: Fast option pricing Greeks calculations.

This module provides functions for calculating option Greeks using:
- Black-Scholes model (European options): bs_* functions
- Bjerksund-Stensland model (American options): am_* functions

Example:
    >>> import stock_options_python as sop
    >>>
    >>> # Calculate Black-Scholes delta for a call option
    >>> delta = sop.bs_delta(s=100, k=105, t=0.5, r=0.05, sigma=0.2, option_type='call')
    >>> print(f"Delta: {delta:.4f}")
    >>>
    >>> # Calculate all Greeks at once
    >>> greeks = sop.bs_greeks(s=100, k=105, t=0.5, r=0.05, sigma=0.2, option_type='call')
    >>> print(greeks)
"""

from .stock_options_python import (
    # Black-Scholes (European options)
    bs_delta,
    bs_gamma,
    bs_theta,
    bs_vega,
    bs_rho,
    bs_greeks,
    # Bjerksund-Stensland (American options)
    am_price,
    am_delta,
    am_gamma,
    am_theta,
    am_vega,
    am_rho,
    am_greeks,
    # Classes
    PyGreeks,
)

__all__ = [
    # Black-Scholes
    "bs_delta",
    "bs_gamma",
    "bs_theta",
    "bs_vega",
    "bs_rho",
    "bs_greeks",
    # Bjerksund-Stensland
    "am_price",
    "am_delta",
    "am_gamma",
    "am_theta",
    "am_vega",
    "am_rho",
    "am_greeks",
    # Classes
    "PyGreeks",
]

__version__ = "0.1.0"
