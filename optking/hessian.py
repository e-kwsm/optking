import logging

import numpy as np
import qcelemental as qcel

from .bend import Bend
from .printTools import print_mat_string
from .stre import Stre
from .tors import Tors


def show(H, oMolsys):
    """Print the Hessian in common spectroscopic units of [aJ/Ang^2], [aJ/deg^2] or [aJ/(Ang deg)]"""
    logger = logging.getLogger(__name__)

    factors = np.zeros(oMolsys.num_intcos)
    cnt = -1
    for F in oMolsys._fragments:
        for I in F.intcos:
            cnt += 1
            factors[cnt] = I.q_show_factor
    for DI in oMolsys._dimer_intcos:
        for I in DI._pseudofrag._intcos:
            cnt += 1
            factors[cnt] = I.q_show_factor

    factors_inv = np.divide(1.0, factors)
    scaled_H = np.einsum("i,ij,j->ij", factors_inv, H, factors_inv)
    scaled_H *= qcel.constants.hartree2aJ
    logger.info("Hessian in [aJ/Ang^2], [aJ/deg^2], etc.\n" + print_mat_string(scaled_H))


# def guess(intcos, geom, Z, connectivity=None, guessType="SIMPLE"):
def guess(oMolsys, connectivity=None, guessType="SIMPLE"):
    """Generates diagonal empirical Hessian in a.u.

    Parameters
    ----------
    intcos : list of Stre, Bend, Tors
    geom : ndarray
        cartesian geometry
    connectivity : ndarray, optional
        connectivity matrix
    guessType: str, optional
        the default is SIMPLE. other options: FISCHER, LINDH_SIMPLE, SCHLEGEL

    Notes
    -----
    such as
      Schlegel, Theor. Chim. Acta, 66, 333 (1984) and
      Fischer and Almlof, J. Phys. Chem., 96, 9770 (1992).
    """

    diag = []
    for F in oMolsys._fragments:
        if F.num_intcos:
            geom = F.geom
            Z = F.Z
            connectivity = F.connectivity_from_distances()
            for intco in F._intcos:
                diag.append(intco.diagonal_hessian_guess(geom, Z, connectivity, guessType))

    # Since the reference points might not even be at atomic positions, let's not worry
    # about implementing various options for the diagonal Hessian guess.
    for DI in oMolsys._dimer_intcos:
        for intco in DI._pseudo_frag._intcos:
            if type(intco) == Stre:
                h = 0.007
                # if (Opt_params.interfragment_distance_inverse) H[cnt][cnt] *= pow(rAB,4);
            elif type(intco) == Bend:
                h = 0.003
            elif type(intco) == Tors:
                h = 0.001
            else:
                h = 0.111
            diag.append(h)

    H = np.diagflat(np.asarray(diag))
    return H
