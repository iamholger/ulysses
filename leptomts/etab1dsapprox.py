import leptomts
import numpy as np
from odeintw import odeintw


from numba import jit
@jit
def fast_RHS(y0, d, w1, n1eq, epstt,epsmm,epsee,c1t,c1m,c1e):
    N1      = y0[0]
    Ntt     = y0[1]
    Nmm     = y0[2]
    Nee     = y0[3]
    c1tc    = np.conjugate(c1t)
    c1mc    = np.conjugate(c1m)
    c1ec    = np.conjugate(c1e)
    rhs1 =      -d*(N1-n1eq)

    rhs2 = epstt*d*(N1-n1eq)-0.5*w1*(2*c1t*c1tc*Ntt)
    rhs3 = epsmm*d*(N1-n1eq)-0.5*w1*(2*c1m*c1mc*Nmm)
    rhs4 = epsee*d*(N1-n1eq)-0.5*w1*(2*c1e*c1ec*Nee)

    return [rhs1, rhs2, rhs3, rhs4]

class EtaB_1DS_Approx(leptomts.LeptoCalc):

    def RHS(self, y0,z,epstt,epsmm,epsee,c1t,c1m,c1e,k):

        if z != self._currx or z == self.xmin:
            self._d       = np.real(self.D1(k,z))
            self._w1      = np.real(self.W1(k,z))
            self._n1eq    = self.N1Eq(z)
            self._currx=z

        return fast_RHS(y0, self._d, self._w1, self._n1eq, epstt,epsmm,epsee,c1t,c1m,c1e)

    @property
    def EtaB(self):
        #Define fixed quantities for BEs
        epstt = np.real(self.epsilonab(2,2))
        epsmm = np.real(self.epsilonab(1,1))
        epsee = np.real(self.epsilonab(0,0))

        c1t   =                 self.c1a(2)
        c1m   =                 self.c1a(1)
        c1e   =                 self.c1a(0)

        xs      = np.linspace(self.xmin, self.xmax, self.xsteps) # TODO is this not already set?
        k       = np.real(self.k1)
        y0      = np.array([0+0j,0+0j,0+0j,0+0j], dtype=np.complex128)

        params  = np.array([epstt,epsmm,epsee,c1t,c1m,c1e,k], dtype=np.complex128)

        ys      = odeintw(self.RHS, y0, self.xs, args = tuple(params))
        nb      = self.sphalfact*(ys[-1,1]+ys[-1,2]+ys[-1,3])

        pd = np.empty((self.xsteps, 4))
        pd[:,      0] = self.xs
        pd[:,[1,2,3]] = np.real(ys[:, [1,2,3]])

        return np.real(nb), pd
