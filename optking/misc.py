import numpy as np
import logging

import qcelemental as qcel

from . import optExceptions


def delta(i, j):
    if i == j:
        return 1
    else:
        return 0


def isDqSymmetric(intcos, geom, Dq):
    logger = logging.getLogger(__name__)
    # TODO add symmetry check
    logger.debug('\tTODO add isDqSymmetric\n')
    return True


def symmetrizeXYZ(XYZ):
    logger = logging.getLogger(__name__)
    # TODO add symmetrize function
    logger.debug('\tTODO add symmetrize XYZ\n')
    return XYZ


# "Average" bond length given two periods
# Values below are from Lindh et al.
# Based on DZP RHF computations, I suggest: 1.38 1.9 2.53, and 1.9 2.87 3.40
def AverageRFromPeriods(perA, perB):
    if perA == 1:
        if perB == 1:
            return 1.35
        elif perB == 2:
            return 2.1
        else:
            return 2.53
    elif perA == 2:
        if perB == 1:
            return 2.1
        elif perB == 2:
            return 2.87
        else:
            return 3.40
    else:
        if perB == 1:
            return 2.53
        else:
            return 3.40


# Return Lindh alpha value from two periods
def HguessLindhAlpha(perA, perB):
    if perA == 1:
        if perB == 1:
            return 1.000
        else:
            return 0.3949
    else:
        if perB == 1:
            return 0.3949
        else:
            return 0.2800


# rho_ij = e^(alpha (r^2,ref - r^2))
def HguessLindhRho(ZA, ZB, RAB):
    perA = qcel.periodictable.to_period(ZA)
    perB = qcel.periodictable.to_period(ZB)

    alpha = HguessLindhAlpha(perA, perB)
    r_ref = AverageRFromPeriods(perA, perB)

    return np.exp(-alpha * (RAB * RAB - r_ref * r_ref))


def tokenizeInputString(inString):
    """
    params: string of integers corresponding to internal coordinates
    returns: a list of integers correspoding to an atom
    removes spaces or non integer characters from string of internal coordinates to be frozen
    """
    outString = inString.replace('(', '').replace(')', '')
    return outString.split()


def intList(inList):
    outList = [int(i) for i in inList]
    return outList


def intIntFloatList(inList):
    if len(inList) % 3 != 0:
        raise optExceptions.OptFail("List is not comprised of int-int-float elements")
    outList = []
    for i in range(0, len(inList), 3):
        outList.append(int(inList[i + 0]))
        outList.append(int(inList[i + 1]))
        outList.append(float(inList[i + 2]))
    return outList


def intIntIntFloatList(inList):
    if len(inList) % 4 != 0:
        raise optExceptions.OptFail(
            "List is not comprised of int-int-int-float elements")
    outList = []
    for i in range(0, len(inList), 4):
        outList.append(int(inList[i + 0]))
        outList.append(int(inList[i + 1]))
        outList.append(int(inList[i + 2]))
        outList.append(float(inList[i + 3]))
    return outList


def intIntIntIntFloatList(inList):
    if len(inList) % 5 != 0:
        raise optExceptions.OptFail(
            "List is not comprised of int-int-int-int-float elements")
    outList = []
    for i in range(0, len(inList), 5):
        outList.append(int(inList[i + 0]))
        outList.append(int(inList[i + 1]))
        outList.append(int(inList[i + 2]))
        outList.append(int(inList[i + 3]))
        outList.append(float(inList[i + 4]))
    return outList


def int_XYZ_list(inList):
    if len(inList) % 2 != 0:
        raise optExceptions.OptFail("int-XYZ list does not have even number of entries")
    outList = []
    for i in range(0, len(inList), 2):
        outList.append(int(inList[i + 0]))
        cart_string = str(inList[i + 1]).upper()
        if len(cart_string) > 3 or len(cart_string) < 1:
            raise optExceptions.OptFail("Could not decipher xyz coordinate string")
        for c in cart_string:
            if c not in ('X', 'Y', 'Z'):
                raise optExceptions.OptFail("Could not decipher xyz coordinate string")
        cart_string = sorted(cart_string)  # x , then y, then z
        outList.append(cart_string)
    return outList
