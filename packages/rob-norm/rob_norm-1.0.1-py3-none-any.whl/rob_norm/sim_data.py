import numpy as np
import pandas as pd
from scipy.stats import invgamma


def sim_dat_fn(row_frac, col_frac, mu_up, mu_down, n, m, nu_fix=True, seed=None):
    """
    Simulate expression data.

    Original R function: sim.dat.fn in RobNorm (https://github.com/mwgrassgreen/RobNorm)

    Parameters:
        row_frac (float): fraction of rows (genes) with outlier signal.
        col_frac (float): fraction of columns (samples) with outlier signal.
        mu_up (float): up-shifted mean of outliers.
        mu_down (float): down-shifted mean of outliers.
        n (int): number of rows (genes).
        m (int): number of columns (samples).
        nu_fix (bool): if True, underlying nu (sample effect) is zero vector.
        seed (int | None): optional RNG seed.

    Returns:
        dict with keys:
            dat (pd.DataFrame): simulated data (genes x samples)
            mu_00 (np.ndarray): true gene means
            var_00 (np.ndarray): true gene variances
            nu_00 (np.ndarray): true sample effects
            sig_ind (pd.DataFrame): indicator matrix (1 if shifted)
    """
    rng = np.random.default_rng(seed)

    # gene-level mean and inverse-gamma variance
    mu_00 = rng.normal(0.0, 1.0, size=n)
    # Use scipy invgamma with shape=5, scale=2 to match R rinvgamma(n, 5, 2)
    var_00 = invgamma.rvs(a=5.0, scale=2.0, size=n, random_state=rng)

    # X.0: null matrix ~ N(mu_00, sqrt(var_00))
    # We want shape (n, m)
    X0 = rng.normal(loc=mu_00[:, None], scale=np.sqrt(
        var_00)[:, None], size=(n, m))

    if nu_fix:
        nu_00 = np.zeros(m)
    else:
        nu_00 = rng.normal(0.0, 1.0, size=m)
        # replace first 20% with shifted nu
        k = int(round(m * 0.2))
        nu_00[:k] = rng.normal(1.0, 1.0, size=k)

    B = np.ones((n, 1)) @ nu_00[None, :]

    S = np.zeros((n, m))
    if (row_frac * col_frac) > 0:
        bk_nm = int(round(n * row_frac * m * col_frac))
        if bk_nm > 0:
            a = rng.binomial(1, 0.8, size=1)[0]
            # first block: upper-left
            r_count = int(round(n * row_frac))
            c_count = int(round(m * col_frac))
            # fill block with either mu_up or 0 in sample of bk_nm
            if bk_nm > 0 and r_count > 0 and c_count > 0:
                vals = np.concatenate(
                    (np.repeat(mu_up, a * bk_nm),
                     np.repeat(0, bk_nm - a * bk_nm)))
                rng.shuffle(vals)
                vals = vals[: (r_count * c_count)]
                S[:r_count, :c_count] = vals.reshape((r_count, c_count))

            a2 = rng.binomial(1, 0.8, size=1)[0]
            if bk_nm > 0 and r_count > 0 and c_count > 0:
                vals = np.concatenate(
                    (np.repeat(mu_down, a2 * bk_nm),
                     np.repeat(0, bk_nm - a2 * bk_nm)))
                rng.shuffle(vals)
                vals = vals[: (r_count * c_count)]
                S[(n - r_count):n, (m - c_count):m] = vals.reshape((r_count, c_count))

    X = X0 + B + S

    # indicator
    S_ind = (S != 0).astype(int)

    rownames = [f"prt.{i+1}" for i in range(n)]
    colnames = [f"s{i+1}" for i in range(m)]

    df = pd.DataFrame(X, index=rownames, columns=colnames)
    ind_df = pd.DataFrame(S_ind, index=rownames, columns=colnames)

    return {"dat": df, "mu_00": mu_00, "var_00": var_00, "nu_00": nu_00, "sig_ind": ind_df}
