from quanti_fret.core import QtfException

import numpy as np
import scipy


def alex_fret(
    dd: np.ndarray, da: np.ndarray, gamma_m: float
) -> np.ndarray:
    """ Compute a FRET Efficiency map from 2 images: DD and DA.

    The equation solved is:

    .. math::

        E = \\frac{DA^{Corr}}{DA^{Corr} + DD * \\gamma^{M}}

    Args:
        dd (np.ndarray): DD.
        da (np.ndarray): DA corrected.
        gamma_m (float): :math:`\\gamma^{M}` value.

    Returns:
        np.ndarray: Fret efficiency map.
    """
    np.seterr(divide='ignore', invalid='ignore')
    E = 100 * da / (da + dd * gamma_m)
    np.seterr(divide='warn', invalid='warn')
    return E


def alex_stochio(
    dd: np.ndarray, da: np.ndarray, aa: np.ndarray,  gamma_m: float,
    beta_x: float
) -> np.ndarray:
    """ Compute a FRET Stochiometry map from 3 images: DD, DA and AA.

    The equation solved is:

    .. math::

        S =
        \\frac{DA^{Corr} + DD * \\gamma^{M}}
        {DA^{Corr} + DD*\\gamma^{M} + AA/\\beta^{X}}

    Args:
        dd (np.ndarray): DD.
        da (np.ndarray): DA corrected.
        aa (np.ndarray): AA.
        gamma_m (float): :math:`\\gamma^{M}` value.
        beta_x (float): :math:`\\beta^{X}` value.

    Returns:
        np.ndarray: Fret Stochiometry map.
    """
    np.seterr(divide='ignore', invalid='ignore')
    S = 100 * (da + dd*gamma_m) / (da + dd*gamma_m + aa/beta_x)
    np.seterr(divide='warn', invalid='warn')
    return S


def clean_mask(
    original_mask: np.ndarray,
    array: np.ndarray,
    array_with_infinite: np.ndarray,
    discard_low_percentile: float = 0.,
    discard_high_percentile: float = 100.,
) -> np.ndarray:
    """ Compute a new mask that keep the data clean and discard unwanted
    values.

    The new mask:

    * reject infinite values from ``array_with_infinite``.
    * reject pixels < 1 on the ``array``.
    * Discard the percentile of pixels (under and above the given value)
      from the intersection of the array and the clean mask.

    Args:
        original_mask (np.ndarray): Original mask to clean.
        array (np.ndarray): array used to apply the mask on.
        array_with_infinite (np.ndarray): array that may contain infinite
            values to discard.
        discard_low_percentile (float, optional): The percentile threshold
            below which values will be discarded, after applying the mask.
            Default is ``0.``.
        discard_high_percentile (float, optional): The percentile threshold
            above which values will be discarded, after applying the mask.
            Default is ``100.``.

    Returns:
        np.ndarray: The newly created mask.
    """
    # This allows us to work with arrays of every dimension. We want the
    # mask to be true, if a given condition on the array is true for every axis
    # of dimension greater than the one one the mask.
    # For example, we want the mask to be True if elements of array are > 1:
    # Mask = [True, False, True]
    # Array = [[1, 2, 3], [4, 5, 6]]
    # We want the result to be: [False, False, True]
    # If the mask is same dimension of array, comp_axis = ()
    # If the mask is N dimensions lower , comp_axis = (0, ..., N-1)
    # Without this, and a direct logical_and, the output mask would be
    # [[False, False, True], [True, False, True]]
    comp_axis = tuple(range(0, array.ndim - original_mask.ndim))

    # Reject infinite values
    array_finite = np.all(np.isfinite(array_with_infinite), axis=comp_axis)
    mask_clean = np.logical_and(array_finite, original_mask)

    # Reject pixels with values <= 1
    array_above_one = np.all(array > 1, axis=comp_axis)
    mask_clean = np.logical_and(array_above_one, mask_clean)

    # The new mask will reject the values below and above the given percentiles
    # of the intersection of the array with the previous new mask applied
    if discard_low_percentile > 0 or discard_high_percentile < 100:
        if discard_low_percentile > discard_high_percentile:
            err = f'Low percentile ({discard_low_percentile}) is higher than' \
                  f' high percentile ({discard_high_percentile})'
            raise QtfException(err)

        # Get intersection
        masked = np.where(mask_clean, array, np.nan)
        expand_axes = list(range(-masked.ndim, 0))
        # Compute min values if needed (or set it to -inf)
        if discard_low_percentile > 0:
            val_mins = np.nanpercentile(masked, discard_low_percentile,
                                        axis=(-2, -1))
            val_mins = np.expand_dims(val_mins, axis=expand_axes[1:])
        else:
            val_mins = np.expand_dims(-np.inf, axis=expand_axes)
        # Compute max values if needed (or set it to inf)
        if discard_high_percentile < 100:
            val_maxs = np.nanpercentile(masked, discard_high_percentile,
                                        axis=(-2, -1))
            val_maxs = np.expand_dims(val_maxs, axis=expand_axes[1:])
        else:
            val_maxs = np.expand_dims(np.inf, axis=expand_axes)
        # Reject min and max values
        masked_in_range = np.all((masked >= val_mins) & (masked <= val_maxs),
                                 axis=comp_axis)
        mask_clean = np.logical_and(masked_in_range, mask_clean)

    return mask_clean


def da_corrected(
    triplet: np.ndarray, alpha_bt: float, delta_de: float
) -> np.ndarray:
    """ Compute the DA value corrected from crosstalk using
    :math:`\\alpha^{BT}` and :math:`\\delta^{DE}`.

    Args:
        triplet (np.ndarray): (DD, DA, AA) triplet.
        alpha_bt (float): The :math:`\\alpha^{BT}` value.
        delta_de (float): The :math:`\\delta^{DE}` value.

    Returns:
        np.ndarray: the DA channel corrected.
    """
    return triplet[1] - alpha_bt*triplet[0] - delta_de*triplet[2]


def fit_confidence_index_q(
    E: np.ndarray, S: np.ndarray, aa: np.ndarray, R2: float
) -> float:
    """ Compute the fit confidence index Q.

    Args:
        E (np.ndarray): Fret.
        D (np.ndarray): Stochiometry.
        aa (np.ndarray): AA channel.
        R2 (float): coefficient of determination.

    Returns:
        float: Fit confidence index Q.
    """
    rho_aa_s, _ = scipy.stats.spearmanr(aa, S, axis=None)
    rho_aa_e, _ = scipy.stats.spearmanr(aa, E, axis=None)
    rho_s_e, _ = scipy.stats.spearmanr(S, E,  axis=None)

    Q = R2 - \
        (abs(rho_aa_s) + abs(rho_aa_e) + abs(rho_s_e)) / 3  # type: ignore

    return float(Q)


def gamma(gamma_channel: np.ndarray, da: np.ndarray) -> np.ndarray:
    """ Compute the gamma matrix.

    Gamma matrix is the DA channel divided by the gamma channel.

    Args:
        gamma_channel (np.ndarray): gamma channel.
        da (np.ndarray): DA channel.
    Returns:
        np.ndarray: the gamma matrix.
    """
    np.seterr(divide='ignore', invalid='ignore')
    gamma = da / gamma_channel
    np.seterr(divide='warn', invalid='warn')
    return gamma


def gamma_xm(
    dd: np.ndarray, da: np.ndarray, aa: np.ndarray
) -> tuple[float, float, float, float]:
    """ Compute :math:`\\beta^{X}` and  :math:`\\gamma^{M}` that are solving
    the following equation:

    .. math::

        \\beta^{X} * DA + \\beta^{X} * \\gamma^{A} * DD = AA * \\frac{1 - S}{S}

    With **S** equals to 0.5.

    To solve it, we use the normal equation that gives us :math:`\\gamma^{X}`
    and :math:`\\beta^{X} *  \\gamma^{M}`.

    Args:
        dd (np.ndarray): DD.
        da (np.ndarray): DA corrected.
        aa (np.ndarray): AA.

    Returns:
        tuple[float, float, float, float]:
            GammaX, GammaM, redchi2, R2.
    """
    # TODO: !!It is no longer recommended to use this class (matrix), even for
    # linear algebra.
    # Instead use regular arrays. The class may be removed in the future
    X = np.transpose(np.vstack((dd, da)))
    Y = np.transpose(aa)

    X_inv = np.matmul(
        np.linalg.inv(np.matmul(np.transpose(X), X)),
        np.transpose(X)
    )
    beta = np.matmul(X_inv, Y)
    beta_x = beta[1]
    gamma_m = beta[0] / beta[1]

    errors = Y - np.matmul(X, beta)

    chi_2 = np.sum((errors * errors) / Y)
    redchi_2 = chi_2 / (len(X) - 2)
    # residual = np.linalg.norm(errors) #to obtain the residuals
    R2 = 1 - (sum(errors * errors) / sum((Y - np.mean(Y))**2))
    return beta_x, gamma_m, redchi_2, R2


def substract_background(
    array: np.ndarray, background: float | tuple[float, float, float]
) -> np.ndarray:
    """ Substract a background to a numpy array, and clip at 0 the negative
    values.

    Args:
        array (np.ndarray): Array to remove the background of.
        background (float): background value to substract.

    Returns:
        np.ndarray: The array with the background substracted.
    """
    bckg_array = np.array(background)
    # To work with Triplets or single channels
    bckg_array = np.expand_dims(bckg_array, axis=(-2, -1))
    new_array = array - bckg_array
    new_array[new_array < 0] = 0
    return new_array


def weighted_gaussian_filter(
    E: np.ndarray, S: np.ndarray, target_S, sigma_S, sigma_gauss,
    weights_threshold
) -> np.ndarray:
    """ Apply a weighted gaussian filter to the FRET efficiency maps.

    The idea is to filter the FRET efficiency using the Stoichiometry. Indeed
    Stoichiometry brings information about the confidence. So we use it to
    define a confidence index matrix. This matrix goes through a gaussian
    filter and is then used to adjust FRET efficiency and keep only relevant
    values.

    Args:
        E (np.ndarray): Raw Fret efficiency maps.
        S (np.ndarray): Raw stoichiometry maps.
        target_S (float): Mean value of the gaussian distribution of the
            stochiometry.
        sigma_S (float): standard deviation of the gaussian distribution of
            the stochiometry.
        sigma_gauss (float): standard deviation of the gaussian kernel for
            filtering.
        weights_threshold (float): threshold for the local "quality of the
            data".  discard if
            ``mean(local weight in the window) < weights_threshold``.

    Returns:
        np.ndarray: Filtered FRET map.
    """

    Ew = np.zeros(np.shape(E))
    E = np.nan_to_num(E)

    # create the weights from the stoichiometry
    W = np.exp(-(S/100 - target_S)**2 / (2 * sigma_S**2))
    W = np.nan_to_num(W)

    # Create gaussian kernel
    # TODO: #to take into account non integer sigmaGauss sigmaGauss+1
    kernel_len = 2 * int(sigma_gauss + 1.5) + 1
    g_kernel = scipy.signal.windows.gaussian(kernel_len, std=sigma_gauss)
    # TODO: Check if reshape is needed
    g_kernel_1d = g_kernel.reshape(kernel_len, 1)
    G = np.outer(g_kernel_1d, g_kernel_1d)
    G = G/G.sum()

    # As proposed by Bastien Arnal and implemented with Irene Wang:
    # Gaussian filtering of W
    W_g = scipy.signal.fftconvolve(W, G, mode='same')
    # Gaussian filtering of W.E
    WE_g = scipy.signal.fftconvolve(np.nan_to_num(W*E), G, mode='same')
    # Threshold on the local weight
    Ew = np.where(W_g < weights_threshold, np.zeros(np.shape(E)), WE_g) / W_g
    Ew = np.nan_to_num(Ew)

    return Ew
