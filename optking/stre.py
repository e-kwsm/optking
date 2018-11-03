import logging

import numpy as np
import qcelemental as qcel

from . import optExceptions
from . import v3d
from .misc import delta, HguessLindhRho
from .simple import Simple


class Stre(Simple):
    """ stretching coordinate between two atoms

    Parameters
    ----------
    a : int
        atom 1 (zero indexing)
    b : int
        atom 2 (zero indexing)
    frozen : boolean, optional
        set stretch as frozen
    fixedEqVal : float
        value to fix stretch at
    inverse : boolean
        identifies 1/R coordinate

    """
    def __init__(self, a, b, frozen=False, fixedEqVal=None, inverse=False):

        self._inverse = inverse  # bool - is really 1/R coordinate?

        if a < b:
            atoms = (a, b)
        else:
            atoms = (b, a)

        Simple.__init__(self, atoms, frozen, fixedEqVal)

    def __str__(self):
        if self.frozen:
            s = '*'
        else:
            s = ' '

        if self.inverse:
            s += '1/R'
        else:
            s += 'R'

        s += "(%d,%d)" % (self.A + 1, self.B + 1)
        if self.fixedEqVal:
            s += "[%.4f]" % (self.fixedEqVal * self.qShowFactor)
        return s

    def __eq__(self, other):
        if self.atoms != other.atoms:
            return False
        elif not isinstance(other, Stre):
            return False
        elif self.inverse != other.inverse:
            return False
        else:
            return True

    @property
    def inverse(self):
        return self._inverse

    @inverse.setter
    def inverse(self, setval):
        self._inverse = bool(setval)

    def q(self, geom):
        return v3d.dist(geom[self.A], geom[self.B])

    def qShow(self, geom):
        return self.qShowFactor * self.q(geom)

    @property
    def qShowFactor(self):
        return qcel.constants.bohr2angstroms

    @property
    def fShowFactor(self):
        return qcel.constants.hartree2aJ / qcel.constants.bohr2angstroms

    # If mini == False, dqdx is 1x(3*number of atoms in fragment).
    # if mini == True, dqdx is 1x6.
    def DqDx(self, geom, dqdx, mini=False):
        try:
            eAB = v3d.eAB(geom[self.A], geom[self.B])  # A->B
        except optExceptions.AlgFail as error:
            raise optExceptions.AlgFail("Stre.DqDx: could not normalize s vector") from error

        if mini:
            startA = 0
            startB = 3
        else:
            startA = 3 * self.A
            startB = 3 * self.B

        dqdx[startA:startA + 3] = -1 * eAB[0:3]
        dqdx[startB:startB + 3] = eAB[0:3]

        if self._inverse:
            val = self.q(geom)
            dqdx[startA:startA + 3] *= -1.0 * val * val  # -(1/R)^2 * (dR/da)
            dqdx[startB:startB + 3] *= -1.0 * val * val


    # Return derivative B matrix elements.  Matrix is cart X cart and passed in.
    def Dq2Dx2(self, geom, dq2dx2):
        try:
            eAB = v3d.eAB(geom[self.A], geom[self.B])  # A->B
        except optExceptions.AlgFail:
            raise optExceptions.AlgFail("Stre.Dq2Dx2: could not normalize s vector") from error

        if not self._inverse:
            length = self.q(geom)

            for a in range(2):
                for a_xyz in range(3):
                    for b in range(2):
                        for b_xyz in range(3):
                            tval = (
                                eAB[a_xyz] * eAB[b_xyz] - delta(a_xyz, b_xyz)) / length
                            if a == b:
                                tval *= -1.0
                            dq2dx2[3*self.atoms[a]+a_xyz,
                                   3*self.atoms[b]+b_xyz] = tval

        else:  # using 1/R
            val = self.q(geom)

            dqdx = np.zeros((3 * len(self.atoms)), float)
            self.DqDx(geom, dqdx, mini=True)  # returned matrix is 1x6 for stre

            for a in range(a):
                for a_xyz in range(3):
                    for b in range(b):
                        for b_xyz in range(3):
                            dq2dx2[3*self.atoms[a]+a_xyz, 3*self.atoms[b]+b_xyz] \
                                = 2.0 / val * dqdx[3*a+a_xyz] * dqdx[3*b+b_xyz]

        return

    def diagonalHessianGuess(self, geom, Z, connectivity=False, guessType="SIMPLE"):
        """ Generates diagonal empirical Hessians in a.u. such as
        Schlegel, Theor. Chim. Acta, 66, 333 (1984) and
        Fischer and Almlof, J. Phys. Chem., 96, 9770 (1992).
        """
        logger = logging.getLogger(__name__)
        if guessType == "SIMPLE":
            return 0.5

        if guessType == "SCHLEGEL":
            R = v3d.dist(geom[self.A], geom[self.B])
            PerA = qcel.periodictable.to_period(Z[self.A])
            PerB = qcel.periodictable.to_period(Z[self.B])

            AA = 1.734
            if PerA == 1:
                if PerB == 1:
                    BB = -0.244
                elif PerB == 2:
                    BB = 0.352
                else:
                    BB = 0.660
            elif PerA == 2:
                if PerB == 1:
                    BB = 0.352
                elif PerB == 2:
                    BB = 1.085
                else:
                    BB = 1.522
            else:
                if PerB == 1:
                    BB = 0.660
                elif PerB == 2:
                    BB = 1.522
                else:
                    BB = 2.068

            F = AA / ((R - BB) * (R - BB) * (R - BB))
            return F

        elif guessType == "FISCHER":
            Rcov = qcel.covalentradii.get(Z[self.A]) + qcel.covalentradii.get(Z[self.B])
            R = v3d.dist(geom[self.A], geom[self.B])
            AA = 0.3601
            BB = 1.944
            return AA * (np.exp(-BB * (R - Rcov)))

        elif guessType == "LINDH_SIMPLE":
            R = v3d.dist(geom[self.A], geom[self.B])
            k_r = 0.45
            return k_r * HguessLindhRho(Z[self.A], Z[self.B], R)

        else:
            logger.warning("Hessian guess encountered unknown coordinate type.\n")
            return 1.0


class HBond(Stre):
    def __str__(self):
        if self.frozen:
            s = '*'
        else:
            s = ' '

        if self.inverse:
            s += '1/H'
        else:
            s += 'H'

        s += "(%d,%d)" % (self.A + 1, self.B + 1)
        if self.fixedEqVal:
            s += "[%.4f]" % self.fixedEqVal
        return s

    # overrides Stre eq in comparisons, regardless of order
    def __eq__(self, other):
        if self.atoms != other.atoms:
            return False
        elif not isinstance(other, HBond):
            return False
        elif self.inverse != other.inverse:
            return False
        else:
            return True

    def diagonalHessianGuess(self, geom, Z, connectivity, guessType):
        """ Generates diagonal empirical Hessians in a.u. such as
        Schlegel, Theor. Chim. Acta, 66, 333 (1984) and
        Fischer and Almlof, J. Phys. Chem., 96, 9770 (1992).
        """
        logger = logging.getLogger(__name__)
        if guessType == "SIMPLE":
            return 0.1
        else:
            logger.warning("Hessian guess encountered unknown coordinate type.\n")
            return 1.0
