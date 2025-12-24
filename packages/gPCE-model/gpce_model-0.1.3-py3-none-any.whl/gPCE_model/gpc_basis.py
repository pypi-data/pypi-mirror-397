""" Generic class for generalized polynomial chaos basis functions"""

import numpy as np
from .multiindex import multiindex
import uncertain_variables as uv

class GpcBasis:
    """ Generic class for generalized polynomial chaos basis functions

        Attributes
        ----------
        m : int
            number of random variables
            
        syschars : str or list of str
            system character(s) of the gpc basis (e.g., 'H' for Hermite)

        p : int
            maximum total degree of the basis functions

        I : numpy.array
            multiindex set defining the basis functions

        Methods
        -------
        __init__(Q, p=0, I="default", full_tensor=False, **kwargs)
            Initialize the gpc basis with given parameters

        __repr__()
            Set how the gpc basis looks when printed

        size()
            Return the size of the multiindex set

        evaluate(xi, dual=False)
            Evaluate the gpc basis functions at given points xi

        norm(do_sqrt=True)
            Compute the norm of the basis functions """
    
    # ---------------------Initialization---------------------------------------------------
    def __init__(self, Q, p=0, I="default", full_tensor=False, **kwargs):
        """ Initialize the gpc basis with given parameters

            Parameters
            ----------
            Q : VariableSet
                VariableSet object defining the probabilistic variables

            p : int, optional
                Maximum total degree of the basis functions, by default 0

            I : str, optional
                Multiindex set defining the basis functions, by default "default"

            full_tensor : bool, optional
                If True, use full tensor product basis up to degree p, by default False """
        
        m = Q.num_params()
        self.m = m

        self.syschars = Q.get_gpc_syschars()
        self.p = p

        if I == "default":
            self.I = multiindex(self.m, p, full_tensor=full_tensor)
        else:
            self.I = I

    # ---------------------set how gpc looks when printed ---------------------------------------------------
    def __repr__(self):
        """ Return a string representation of the GpcBasis object

            Returns
            -------
            repr_string : str
                String representation of the GpcBasis object showing its attributes and their values """
        
        attrs = vars(self)
        repr_string = ', '.join("%s: %s" % item for item in attrs.items())
        return repr_string

    # ----------------------------------------- size --------------------------------------------------
    def size(self):
        """ Return the size of the multiindex set

            Returns
            -------
            size : tuple
                Size of the multiindex set I """
        
        size = self.I.shape
        return size

    # ----------------------------Evaluate basis functions ---------------------------------------------------
    def evaluate(self, xi, dual=False):
        """ Evaluate the gpc basis functions at given points xi

            Parameters
            ----------
            xi : array_like
                Points at which to evaluate the basis functions

            dual : bool, optional
                If True, evaluate dual basis functions, by default False

            Returns
            -------
            y_j_alpha : numpy.array
                Evaluated basis functions at points xi """
        
        syschars = self.syschars
        I = self.I
        m = self.m
        M = self.I.shape[0]
        if xi.ndim == 1:
            xi = xi.reshape(-1, 1)
        k = xi.shape[0]
        deg = max(self.I.flatten())

        p = np.zeros([k, m, deg + 2])
        p[:, :, 0] = np.zeros(xi.shape)
        p[:, :, 1] = np.ones(xi.shape)

        if len(syschars) == 1:
            polysys = uv.syschar_to_polysys(syschars)
            r = polysys.recur_coeff(deg)
            for d in range(deg):
                p[:, :, d + 2] = (r[d, 0] + xi * r[d, 1]) * p[:, :, d + 1] - r[d, 2] * p[:, :, d]
        else:
            for j, syschar in enumerate(syschars):
                polysys = uv.syschar_to_polysys(syschar)
                r = polysys.recur_coeff(deg)
                for d in range(deg):
                    p[:, j, d + 2] = (r[d, 0] + xi[:, j] * r[d, 1]) * p[:, j, d + 1] - r[d, 2] * p[:, j, d]

        y_j_alpha = np.ones([k, M])
        for j in range(m):
            y_j_alpha = y_j_alpha * p[:, j, I[:, j] + 1]

        if dual:
            nrm2 = self.norm(do_sqrt=False)
            y_j_alpha = (y_j_alpha / nrm2.reshape(-1, 1)).transpose()
        return y_j_alpha

    # ------------------------Compute the norm of the basis functions-----------------------
    def norm(self, do_sqrt=True):
        """ Compute the norm of the basis functions

            Parameters
            ----------
            do_sqrt : bool, optional
                If True, return the square root of the norm, by default True

            Returns
            -------
            norm_I : numpy.array
                Norm of the basis functions """
        
        syschars = self.syschars
        I = self.I
        m = self.m
        M = self.I.shape[0]

        if syschars == syschars.lower():
            norm_I = np.ones([M, 1])
            return norm_I

        if len(syschars) == 1:
            # max degree of univariate polynomials
            deg = max(self.I.flatten())
            polysys = uv.syschar_to_polysys(syschars)
            nrm = polysys.sqnorm(range(deg + 1))
            norm2_I = np.prod(nrm[I].reshape(I.shape), axis=1)

        else:
            norm2_I = np.ones([M])
            for j in range(m):
                deg = max(I[:, j])
                polysys = uv.syschar_to_polysys(syschars[j])
                nrm2 = polysys.sqnorm(np.arange(deg + 1))
                norm2_I = norm2_I * nrm2[I[:, j]]
        if do_sqrt:
            norm_I = np.sqrt(norm2_I)
        else:
            norm_I = norm2_I

        return norm_I

