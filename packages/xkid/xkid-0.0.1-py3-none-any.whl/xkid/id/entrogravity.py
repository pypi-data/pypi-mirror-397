from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


@dataclass(frozen=True)
class EntrogravitySphericalParams:
    # model
    q: float
    D0: float
    D: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    eps: float = 1e-12

    # domain / resolution
    xmax: float = 1e6
    xmin: float = 10.0
    steps: int = 20000

    # initial conditions at xmax
    mu_inf: float = 0.0
    A_inf: float = 0.0
    rho_inf: float = 1e-6
    F_inf: float = 0.0
    phi_inf: float = 0.0

    # numerics / cap
    cap: bool = False
    rho_floor: float = 1e-15


@dataclass
class _State:
    mu: float
    A: float
    rho: float
    F: float
    phi: float


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def _rhs(x: float, y: _State, p: EntrogravitySphericalParams) -> Tuple[_State, Dict[str, float]]:
    """
    dy/dx plus derived values used for summary + chi.
    """
    if x <= 0.0:
        nan = float("nan")
        return _State(nan, nan, nan, nan, nan), {"err": 1.0}

    mu, A, rho, F = y.mu, y.A, y.rho, y.F
    rho_eff = max(rho, p.rho_floor)

    Delta = 1.0 - 2.0 * mu
    if Delta <= 0.0:
        nan = float("nan")
        return _State(nan, nan, nan, nan, nan), {"Delta": Delta, "err": 2.0}

    b = -0.5 * math.log(Delta)

    # phi' = (q/x^2) exp(b-A) / rho
    phi_prime = (p.q / (x * x)) * math.exp(b - A) / rho_eff

    denom = (x * x) * math.exp(A + b) * Delta
    if denom <= 0.0 or p.D0 <= 0.0:
        nan = float("nan")
        return _State(nan, nan, nan, nan, nan), {"Delta": Delta, "b": b, "denom": denom, "err": 3.0}

    # rho' from flux definition
    rho_prime = (F / denom - p.D * rho * phi_prime) / p.D0

    # sigma >= 0
    sigma = (
        p.alpha * rho * Delta * (phi_prime * phi_prime)
        + p.beta * (Delta * (rho_prime * rho_prime)) / (rho_eff + p.eps)
    )
    if sigma < 0.0 and sigma > -1e-30:
        sigma = 0.0

    eps = 0.5 * rho * Delta * (phi_prime * phi_prime)

    mu_prime = 4.0 * math.pi * (x * x) * eps - (mu / x)
    A_prime = (mu + 4.0 * math.pi * (x ** 3) * eps) / ((x * x) * Delta)

    F_prime = -(x * x) * math.exp(A + b) * sigma

    # b_x = mu'/Delta
    b_x = mu_prime / Delta

    dy = _State(mu_prime, A_prime, rho_prime, F_prime, phi_prime)
    d = {
        "Delta": Delta,
        "b": b,
        "phi_prime": phi_prime,
        "rho_prime": rho_prime,
        "sigma": sigma,
        "eps": eps,
        "mu_prime": mu_prime,
        "A_prime": A_prime,
        "b_x": b_x,
        "err": 0.0,
    }
    return dy, d


def _rk4_step(x: float, y: _State, h: float, p: EntrogravitySphericalParams) -> Tuple[_State, Dict[str, float]]:
    k1, d1 = _rhs(x, y, p)

    y2 = _State(
        y.mu + 0.5 * h * k1.mu,
        y.A + 0.5 * h * k1.A,
        y.rho + 0.5 * h * k1.rho,
        y.F + 0.5 * h * k1.F,
        y.phi + 0.5 * h * k1.phi,
    )
    k2, _ = _rhs(x + 0.5 * h, y2, p)

    y3 = _State(
        y.mu + 0.5 * h * k2.mu,
        y.A + 0.5 * h * k2.A,
        y.rho + 0.5 * h * k2.rho,
        y.F + 0.5 * h * k2.F,
        y.phi + 0.5 * h * k2.phi,
    )
    k3, _ = _rhs(x + 0.5 * h, y3, p)

    y4 = _State(
        y.mu + h * k3.mu,
        y.A + h * k3.A,
        y.rho + h * k3.rho,
        y.F + h * k3.F,
        y.phi + h * k3.phi,
    )
    k4, _ = _rhs(x + h, y4, p)

    y_next = _State(
        y.mu + (h / 6.0) * (k1.mu + 2.0 * k2.mu + 2.0 * k3.mu + k4.mu),
        y.A + (h / 6.0) * (k1.A + 2.0 * k2.A + 2.0 * k3.A + k4.A),
        y.rho + (h / 6.0) * (k1.rho + 2.0 * k2.rho + 2.0 * k3.rho + k4.rho),
        y.F + (h / 6.0) * (k1.F + 2.0 * k2.F + 2.0 * k3.F + k4.F),
        y.phi + (h / 6.0) * (k1.phi + 2.0 * k2.phi + 2.0 * k3.phi + k4.phi),
    )
    return y_next, d1


def _chi_from_row(
    x: float,
    Delta: float,
    b: float,
    A_x: float,
    b_x: float,
    A_xx: float,
) -> float:
    """
    chi = K*lP^4 (dimensionless). Uses the post-pass A_xx estimate.
    """
    if x <= 0.0 or Delta <= 0.0:
        return float("nan")
    if any(math.isnan(v) for v in (b, A_x, b_x, A_xx)):
        return float("nan")

    exp2b = math.exp(2.0 * b)
    term1 = (A_xx + A_x * A_x - A_x * b_x)
    term1 = term1 * term1
    term2 = 2.0 * (A_x * A_x + b_x * b_x) / (x * x)
    term3 = ((exp2b - 1.0) ** 2) / (x ** 4)
    return 4.0 * math.exp(-4.0 * b) * (term1 + term2 + term3)


def run_entrogravity_spherical(p: EntrogravitySphericalParams) -> Dict[str, float]:
    """
    Deterministic solve + summary reduction.

    Returns only a compact summary (used for ID payload), not the full trace.
    """
    if p.steps <= 0:
        raise ValueError("steps must be > 0")
    if p.xmax <= p.xmin:
        raise ValueError("require xmax > xmin")
    if p.xmin <= 0.0:
        raise ValueError("require xmin > 0")
    if p.D0 <= 0.0:
        raise ValueError("require D0 > 0")
    if p.q <= 0.0:
        # we allow q=0, but then phi' = 0 -> trivial; still deterministic
        pass
    if p.rho_floor <= 0.0:
        raise ValueError("require rho_floor > 0")
    if p.eps <= 0.0:
        raise ValueError("require eps > 0")
    if p.D < 0.0 or p.alpha < 0.0 or p.beta < 0.0:
        raise ValueError("require D, alpha, beta >= 0")

    h = (p.xmin - p.xmax) / float(p.steps)  # inward (negative)
    x = p.xmax
    y = _State(p.mu_inf, p.A_inf, p.rho_inf, p.F_inf, p.phi_inf)

    # we store minimal arrays needed for post-pass chi:
    xs: List[float] = []
    A_primes: List[float] = []
    rows: List[Dict[str, float]] = []

    x_sigma: Optional[float] = None
    hit_horizon: Optional[float] = None

    for i in range(p.steps + 1):
        if p.cap:
            y.rho = _clamp(y.rho, 0.0, 1.0)

        dy, d = _rhs(x, y, p)
        Delta = float(d.get("Delta", float("nan")))

        if p.cap and x_sigma is None and y.rho >= 1.0:
            x_sigma = x

        if hit_horizon is None and isinstance(Delta, float) and Delta <= 0.0:
            hit_horizon = x

        # record for chi post-pass
        xs.append(x)
        A_primes.append(float(d.get("A_prime", float("nan"))))
        rows.append(
            {
                "x": x,
                "Delta": Delta,
                "b": float(d.get("b", float("nan"))),
                "A_x": float(d.get("A_prime", float("nan"))),
                "b_x": float(d.get("b_x", float("nan"))),
            }
        )

        if i == p.steps:
            break
        if (isinstance(Delta, float) and Delta <= 0.0) or any(
            math.isnan(v) for v in (y.mu, y.A, y.rho, y.F, y.phi)
        ):
            break

        y_next, _ = _rk4_step(x, y, h, p)
        if p.cap:
            y_next.rho = _clamp(y_next.rho, 0.0, 1.0)

        x = x + h
        y = y_next

    # post-pass A_xx
    n = len(rows)
    A_xx: List[float] = [float("nan")] * n
    if n >= 2:
        for i in range(n):
            if i == 0:
                dx = xs[1] - xs[0]
                A_xx[i] = (A_primes[1] - A_primes[0]) / dx if dx != 0.0 else float("nan")
            elif i == n - 1:
                dx = xs[n - 1] - xs[n - 2]
                A_xx[i] = (A_primes[n - 1] - A_primes[n - 2]) / dx if dx != 0.0 else float("nan")
            else:
                dx = xs[i + 1] - xs[i - 1]
                A_xx[i] = (A_primes[i + 1] - A_primes[i - 1]) / dx if dx != 0.0 else float("nan")

    chis: List[float] = []
    for i in range(n):
        r = rows[i]
        chi = _chi_from_row(
            x=float(r["x"]),
            Delta=float(r["Delta"]),
            b=float(r["b"]),
            A_x=float(r["A_x"]),
            b_x=float(r["b_x"]),
            A_xx=float(A_xx[i]),
        )
        if not math.isnan(chi):
            chis.append(chi)

    chi_min = min(chis) if chis else float("nan")
    chi_max = max(chis) if chis else float("nan")
    chi_at_xmin = chis[-1] if chis else float("nan")

    return {
        "trace_len": float(n),
        "x_sigma": float("nan") if x_sigma is None else float(x_sigma),
        "hit_horizon": float("nan") if hit_horizon is None else float(hit_horizon),
        "chi_min": chi_min,
        "chi_max": chi_max,
        "chi_at_xmin": chi_at_xmin,
    }
