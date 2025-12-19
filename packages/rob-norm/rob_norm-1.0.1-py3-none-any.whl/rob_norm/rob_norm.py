import numpy as np
import pandas as pd


def rob_norm(X_0, gamma_0=0.5, tol=1e-4, step=200):
    """
    Robustly normalize expression data.

    Original R function: RobNorm in RobNorm (https://github.com/mwgrassgreen/RobNorm)

    Parameters:
        X_0 (pd.DataFrame or np.ndarray): The expression matrix in log scale.
        gamma_0 (float): The density exponent parameter gamma, in practice, taking gamma_0 = 0.5 or 1.
        tol (float): The tolerance for interations (default: 1e-4).
        step (int): The step limit (default: 200).

    Returns:
        dict with keys:
            norm_data (pd.DataFrame): Normalized expression data.
            id_norm (list): Indices of rows used for normalization.
            stand_s (pd.Series): Standard sample constructed from medians.
            nu_est (np.ndarray): Estimated sample effects.
            mu_est (np.ndarray): Estimated gene means.
            sigma2_est (np.ndarray): Estimated gene variances.
            w_mx (np.ndarray): Final weights matrix.
            divergence (np.ndarray): Divergence values over iterations.
            para_diff (np.ndarray): Parameter differences over iterations.
    """

    # Ensure input is a DataFrame to handle indices/columns easily
    if not isinstance(X_0, pd.DataFrame):
        # Create default index/columns if numpy array provided
        X_0 = pd.DataFrame(X_0)

    # --- Step 1: Filter rows ---
    # Select rows non-missing in at least half of the samples
    # R: rowSums(!is.na(X.0)) >= (ncol(X.0)/2)
    valid_counts = X_0.notna().sum(axis=1)
    id_norm = X_0.index[valid_counts >= (X_0.shape[1] / 2)].tolist()

    X_1 = X_0.loc[id_norm].copy()

    # --- Step 2: Construct standard samples ---
    # R: apply(X.1, 1, median)
    # Using nanmedian to match R's behavior if NAs are present in valid rows
    x_stand = np.nanmedian(X_1.values, axis=1)

    # Construct X matrix: [x.stand, X.1]
    # In R, cbind adds x.stand as the first column
    X_matrix = np.column_stack((x_stand, X_1.values))

    I, J = X_matrix.shape

    # --- Step 3: Initialize parameters ---
    # Nu.0: median of columns (X - x.stand)
    # Note: x.stand is column 0 of X_matrix
    diff_stand = X_matrix - x_stand[:, None]
    Nu_0 = np.nanmedian(diff_stand, axis=0)

    # Mu.0: mean of rows (X - Nu.0)
    # We broadcast Nu_0 across rows
    X_minus_Nu = X_matrix - Nu_0[None, :]
    Mu_0 = np.nanmean(X_minus_Nu, axis=1)

    # sigma2.0: mean of squared residuals
    # Residuals = X - Nu - Mu
    residuals_sq = (X_minus_Nu - Mu_0[:, None])**2
    sigma2_0 = np.nanmean(residuals_sq, axis=1)

    # --- Step 4: Initial Weights Calculation ---
    # mean.0.mx = Mu.0 outer 1 + 1 outer Nu.0
    mean_0_mx = Mu_0[:, None] + Nu_0[None, :]

    # var.0.mx = sigma2.0 outer 1
    var_0_mx = sigma2_0[:, None] * np.ones((1, J))

    # den.0 = dnorm(...)
    # Gaussian PDF: (1 / sqrt(2*pi*sigma^2)) * exp(-(x-mu)^2 / (2*sigma^2))
    # We use numpy math for speed over scipy.stats
    den_0 = (1.0 / np.sqrt(2 * np.pi * var_0_mx)) * \
        np.exp(-((X_matrix - mean_0_mx)**2) / (2 * var_0_mx))

    dum = den_0 ** gamma_0

    # Handle NaNs in density (propagating from NAs in data)
    dum[np.isnan(den_0)] = np.nan

    # Normalize weights (w.mx)
    row_sums_dum = np.nansum(dum, axis=1)
    w_mx = dum / row_sums_dum[:, None]
    w_size = row_sums_dum

    # --- Step 5: Initial Divergence ---
    # Formula components
    term1_num = (gamma_0 + 1) * np.nansum(w_mx *
                                          (X_matrix - mean_0_mx)**2, axis=1)
    term1 = term1_num / sigma2_0
    term2 = np.log(2 * np.pi * sigma2_0 / (gamma_0 + 1))

    divergence_0 = np.sum(w_size * (term1 + term2))

    # --- Iterations ---
    para_diff_int = []
    divergence_int = [divergence_0]
    iteration = 0
    flag = False

    while not flag:
        # Update Mu and Sigma^2
        # Mu.new calculation
        X_minus_Nu = X_matrix - Nu_0[None, :]
        Mu_new = np.nansum(X_minus_Nu * w_mx, axis=1)

        # Sigma2.new calculation
        # Residuals using Mu_new
        res_sq = (X_minus_Nu - Mu_new[:, None])**2
        sigma2_new = np.nansum(res_sq * w_mx, axis=1) * (1 + gamma_0)

        # Check for singularity (trapped locally)
        if np.nanmin(sigma2_new) < 1e-10:
            raise ValueError("The pre-chosen gamma is large, please choose a smaller nonnegative gamma.")

        # Update Nu
        # weight.nu calculation
        # Broadcast (w.size / (sigma2 / (1+gamma))) across columns
        factor = (w_size / (sigma2_new / (1 + gamma_0)))[:, None]
        weight_nu = w_mx * factor

        # Nu.new calculation
        num = np.nansum(weight_nu * (X_matrix - Mu_new[:, None]), axis=0)
        den = np.nansum(weight_nu, axis=0)
        Nu_new = num / den

        # Adjust Mu and Nu (Identifiability constraint: Nu[0] must be 0)
        # In R: Mu.new = Mu.new + Nu.new[1] (Note: R index 1 is Python index 0)
        # In R: Nu.new = Nu.new - Nu.new[1]
        offset = Nu_new[0]
        Mu_new = Mu_new + offset
        Nu_new = Nu_new - offset

        # Parameter difference
        diff_mu = np.nansum(np.abs(Mu_new - Mu_0))
        diff_nu = np.nansum(np.abs(Nu_new - Nu_0))
        diff_sigma = np.nansum(np.abs(sigma2_new - sigma2_0))
        para_diff_new = diff_mu + diff_nu + diff_sigma
        para_diff_int.append(para_diff_new)

        # Update Divergence
        mean_new_mx = Mu_new[:, None] + Nu_new[None, :]
        term1_num = (gamma_0 + 1) * np.nansum(w_mx *
                                              (X_matrix - mean_new_mx)**2, axis=1)
        term1 = term1_num / sigma2_new
        term2 = np.log(2 * np.pi * sigma2_new / (gamma_0 + 1))

        divergence_new = np.nansum(w_size * (term1 + term2))
        divergence_int.append(divergence_new)

        iteration += 1

        # Check convergence
        flag = (para_diff_new < tol) or (iteration >= step)

        if flag:
            break

        # Prepare for next iteration
        Mu_0 = Mu_new
        Nu_0 = Nu_new
        sigma2_0 = sigma2_new

        # Re-calculate weights for next loop
        mean_0_mx = Mu_0[:, None] + Nu_0[None, :]
        var_0_mx = sigma2_0[:, None] * np.ones((1, J))

        den_0 = (1.0 / np.sqrt(2 * np.pi * var_0_mx)) * \
            np.exp(-((X_matrix - mean_0_mx)**2) / (2 * var_0_mx))

        dum = den_0 ** gamma_0
        dum[np.isnan(den_0)] = np.nan
        row_sums_dum = np.nansum(dum, axis=1)
        w_mx = dum / row_sums_dum[:, None]
        w_size = row_sums_dum

    # --- Finalize Output ---
    # nu.rob.est = Nu.0[-1] in R means remove the first element
    nu_rob_est = Nu_0[1:]

    # Align nu_rob_est with columns of X_0
    X_0_rob = X_0 - nu_rob_est[None, :]

    return {
        "norm_data": X_0_rob,
        "id_norm": id_norm,
        "stand_s": pd.Series(x_stand, index=id_norm),
        "nu_est": nu_rob_est,
        "mu_est": Mu_0,
        "sigma2_est": sigma2_0,
        "w_mx": w_mx,
        "divergence": np.array(divergence_int),
        "para_diff": np.array(para_diff_int)
    }
