import numpy as np
import logging
from printTools import printMatString
import physconst as pc
# from bend import *


def show(H, intcos):
    """ print the Hessian in common spectroscopic units of aJ/Ang^2, aJ/deg^2 or aJ/(Ang deg)
    """
    logger = logging.getLogger(__name__)
    Hscaled = np.zeros(H.shape, H.dtype)
    for i, row in enumerate(intcos):
        for j, col in enumerate(intcos):
            Hscaled[i, j] = H[i, j] * pc.hartree2aJ / row.qShowFactor / col.qShowFactor
    logger.info("Hessian in aJ/Ang^2, etc.\n" + printMatString(Hscaled))


def guess(intcos, geom, Z, connectivity=False, guessType="SIMPLE"):
    """ Generates diagonal empirical Hessians in a.u. such as
      Schlegel, Theor. Chim. Acta, 66, 333 (1984) and
      Fischer and Almlof, J. Phys. Chem., 96, 9770 (1992).
    """
    dim = len(intcos)

    H = np.zeros((dim, dim), float)
    for i, intco in enumerate(intcos):
        H[i, i] = intco.diagonalHessianGuess(geom, Z, connectivity, guessType)

    return H


def convert_json_hess_to_matrix(H, Natom):
    return H.reshape(3 * Natom, 3 * Natom)
