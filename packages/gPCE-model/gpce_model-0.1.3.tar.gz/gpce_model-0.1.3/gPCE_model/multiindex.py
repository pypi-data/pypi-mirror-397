""" Generate multiindex set for polynomial chaos expansions """

import numpy as np

def multiindex(m, p, full_tensor=False):
    """ Generate multiindex set for polynomial chaos expansions 

        Parameters
        ----------
        m : int
            Number of variables

        p : int
            Maximum total degree of the basis functions

        full_tensor : bool, optional
            If True, use full tensor product basis up to degree p, by default False

        Returns
        -------
        I : numpy.array
            Multiindex set defining the basis functions """
    
    d = np.array(range(p + 1))
    M = np.meshgrid(*[d] * m)
    I = np.concatenate([i.flatten().reshape(-1, 1) for i in M], axis=1)

    if not full_tensor:
        I = I[np.sum(I, axis=1) <= p, :]
    I = np_sortrows(I, list(range(m - 1, 0, -1)))
    ind = np.argsort(np.sum(I, axis=1))
    I = I[ind, :]
    return I


class Descending:
    """ Class to indicate descending order for sorting 
    
        Attributes
        ----------
        column_index : int
            Index of the column to be sorted in descending order
            
        Methods
        -------
        __init__(column_index)
            Initialize the Descending object with the specified column index
            
        __int__()
            Return the column index when cast to integer """

    def __init__(self, column_index):
        """ Initialize the Descending object with the specified column index

            Parameters
            ----------
            column_index : int
                Index of the column to be sorted in descending order """
        
        self.column_index = column_index

    def __int__(self):
        """ Return the column index when cast to integer 
        
            Returns
            -------
            column_index : int
                Index of the column to be sorted in descending order """
        
        column_index = self.column_index
        return column_index


def np_sortrows(M, columns=None):
    """  Sort the rows of a 2D numpy array M based on specified columns.

        Parameters
        ----------
        M : numpy.array
            2D numpy array to be sorted

        columns : list, optional
            List of column indices to sort by. If an index is wrapped in a Descending object
            the corresponding column will be sorted in descending order. 
            If None or empty, all columns will be used in reversed order, by default None

        Raises
        ------
        ValueError
            If M is not a 2D numpy array

        Returns
        -------
        M_sorted : numpy.array
            Sorted 2D numpy array"""
    
    if len(M.shape) != 2:
        raise ValueError('M must be 2d numpy.array')
    if (columns is None) or len(columns)==0:  # no columns specified, use all in reversed order
        M_columns = tuple(M[:, c] for c in range(M.shape[1] - 1, -1, -1))
    else:
        M_columns = []
        for c in columns:
            M_c = M[:, int(c)]
            if isinstance(c, Descending):
                M_columns.append(M_c[::-1])
            else:
                M_columns.append(M_c)
        M_columns.reverse()

    return M[np.lexsort(M_columns), :]

def main():
    print(multiindex(3, 4))


if __name__ == "__main__":
    main()
