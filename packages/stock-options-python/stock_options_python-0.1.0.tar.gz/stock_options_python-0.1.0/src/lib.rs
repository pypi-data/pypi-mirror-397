use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use stock_options::{black_scholes, bjerksund_stensland, OptionType, Greeks};

/// Convert string to OptionType
fn parse_option_type(option_type: &str) -> PyResult<OptionType> {
    match option_type.to_lowercase().as_str() {
        "call" | "c" => Ok(OptionType::Call),
        "put" | "p" => Ok(OptionType::Put),
        _ => Err(PyErr::new::<PyValueError, _>("Invalid option type. Use 'call' or 'put'."))
    }
}

/// Container for all option Greeks returned to Python
#[pyclass]
#[derive(Clone)]
struct PyGreeks {
    #[pyo3(get)]
    delta: f64,
    #[pyo3(get)]
    gamma: f64,
    #[pyo3(get)]
    theta: f64,
    #[pyo3(get)]
    vega: f64,
    #[pyo3(get)]
    rho: f64,
}

#[pymethods]
impl PyGreeks {
    fn __repr__(&self) -> String {
        format!(
            "Greeks(delta={:.6}, gamma={:.6}, theta={:.6}, vega={:.6}, rho={:.6})",
            self.delta, self.gamma, self.theta, self.vega, self.rho
        )
    }
}

impl From<Greeks> for PyGreeks {
    fn from(g: Greeks) -> Self {
        PyGreeks {
            delta: g.delta,
            gamma: g.gamma,
            theta: g.theta,
            vega: g.vega,
            rho: g.rho,
        }
    }
}

// ============================================================================
// Black-Scholes Functions (European Options)
// ============================================================================

/// Calculate the delta of a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate (e.g., 0.05 for 5%)
///     sigma: Volatility of the underlying asset (e.g., 0.2 for 20%)
///     q: Dividend yield (e.g., 0.01 for 1%)
///     option_type: 'call' or 'put'
///
/// Returns:
///     The delta of the option
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn bs_delta(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    black_scholes::delta(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the gamma of a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///
/// Returns:
///     The gamma of the option (same for calls and puts)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0))]
fn bs_gamma(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64) -> PyResult<f64> {
    black_scholes::gamma(s, k, t, r, sigma, q)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the theta of a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The theta of the option (per day)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn bs_theta(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    black_scholes::theta(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the vega of a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///
/// Returns:
///     The vega of the option (same for calls and puts)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0))]
fn bs_vega(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64) -> PyResult<f64> {
    black_scholes::vega(s, k, t, r, sigma, q)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the rho of a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The rho of the option (per 1% change in interest rate)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn bs_rho(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    black_scholes::rho(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate all Greeks for a European option using Black-Scholes.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     A Greeks object with delta, gamma, theta, vega, and rho
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn bs_greeks(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<PyGreeks> {
    let opt_type = parse_option_type(option_type)?;
    black_scholes::all_greeks(s, k, t, r, sigma, q, opt_type)
        .map(PyGreeks::from)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

// ============================================================================
// Bjerksund-Stensland Functions (American Options)
// ============================================================================

/// Calculate the price of an American option using Bjerksund-Stensland 2002.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The price of the American option
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_price(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::price(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the delta of an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The delta of the American option
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_delta(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::delta(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the gamma of an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The gamma of the American option
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_gamma(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::gamma(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the theta of an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The theta of the American option (per day)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_theta(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::theta(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the vega of an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The vega of the American option
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_vega(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::vega(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate the rho of an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     The rho of the American option (per 1% change in interest rate)
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_rho(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<f64> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::rho(s, k, t, r, sigma, q, opt_type)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Calculate all Greeks for an American option using Bjerksund-Stensland.
///
/// Args:
///     s: Current price of the underlying asset
///     k: Strike price of the option
///     t: Time to expiration in years
///     r: Risk-free interest rate
///     sigma: Volatility of the underlying asset
///     q: Dividend yield
///     option_type: 'call' or 'put'
///
/// Returns:
///     A Greeks object with delta, gamma, theta, vega, and rho
#[pyfunction]
#[pyo3(signature = (s, k, t, r, sigma, q=0.0, option_type="call"))]
fn am_greeks(s: f64, k: f64, t: f64, r: f64, sigma: f64, q: f64, option_type: &str) -> PyResult<PyGreeks> {
    let opt_type = parse_option_type(option_type)?;
    bjerksund_stensland::all_greeks(s, k, t, r, sigma, q, opt_type)
        .map(PyGreeks::from)
        .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))
}

/// Python module for option pricing Greeks calculations.
///
/// This module provides functions for calculating option Greeks using:
/// - Black-Scholes model (European options): bs_* functions
/// - Bjerksund-Stensland model (American options): am_* functions
#[pymodule]
fn stock_options_python(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Black-Scholes (European)
    m.add_function(wrap_pyfunction!(bs_delta, m)?)?;
    m.add_function(wrap_pyfunction!(bs_gamma, m)?)?;
    m.add_function(wrap_pyfunction!(bs_theta, m)?)?;
    m.add_function(wrap_pyfunction!(bs_vega, m)?)?;
    m.add_function(wrap_pyfunction!(bs_rho, m)?)?;
    m.add_function(wrap_pyfunction!(bs_greeks, m)?)?;

    // Bjerksund-Stensland (American)
    m.add_function(wrap_pyfunction!(am_price, m)?)?;
    m.add_function(wrap_pyfunction!(am_delta, m)?)?;
    m.add_function(wrap_pyfunction!(am_gamma, m)?)?;
    m.add_function(wrap_pyfunction!(am_theta, m)?)?;
    m.add_function(wrap_pyfunction!(am_vega, m)?)?;
    m.add_function(wrap_pyfunction!(am_rho, m)?)?;
    m.add_function(wrap_pyfunction!(am_greeks, m)?)?;

    m.add_class::<PyGreeks>()?;

    Ok(())
}
