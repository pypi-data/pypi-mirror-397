""" Generic class for generalized polynomial chaos expansion (gPCE) model"""

import numpy as np
import pandas as pd
from .gpc_basis import GpcBasis
from sklearn.metrics import mean_squared_error
from scipy.sparse import csr_matrix
import copy
import shap

# ##########################################################################################
#                           GPC MODEL
#                ‘Generalized Polynomial Chaos Expansion’
# ##########################################################################################
class GpcModel:
    """ Generic class for generalized polynomial chaos expansion (gPCE) model

        Attributes
        ----------
        basis : GpcBasis
            gPCE basis functions
            
        Q : VariableSet
            VariableSet object defining the probabilistic variables

        u_alpha_i : numpy.array
            Coefficients of the gPCE model

        p : int
            Maximum total degree of the basis functions

        Methods
        -------
        __init__(Q, p=0, I="default", full_tensor=False, **kwargs)
            Initialize the gPCE model with given parameters
            
        __repr__()
            Return a string representation of the GpcModel object

        compute_coeffs_by_regression(q_k_j, u_k_i)
            Compute gPCE coefficients using regression method

        compute_coeffs_by_projection(q_k_j, u_k_i, w_k)
            Compute gPCE coefficients using projection method

        predict(q_k_j)
            Predict model response at given parameter points q_k_j

        train(q_train, y_train)
            Train the gPCE model using training data

        train_and_evaluate(q_train, y_train, q_val, y_val)
            Train the gPCE model and evaluate on validation data

        mean()
            Compute the mean of the gPCE model

        variance()
            Compute the variance of the gPCE model

        compute_partial_vars(model_obj, max_index=1)
            Compute partial variances and Sobol indices up to specified order

        get_shap_values(predict_fn, q, forced=False, explainer_type="kernelexplainer")
            Compute SHAP values for the gPCE model predictions

        to_jsonld(model_id='v0')
            Export the gPCE model metadata to JSON-LD format """
    
    def __init__(self, Q, p=0, I="default", full_tensor=False, **kwargs):
        """ Initialize the gPCE model with given parameters

            Parameters
            ----------
            Q : VariableSet
                VariableSet object defining the probabilistic variables

            p : int, optional
                Maximum total degree of the basis functions, by default 0

            I : str, optional
                Multiindex set defining the basis functions, by default "default"

            full_tensor : bool, optional
                If True, use full tensor product basis up to degree p, by default False"""
        
        self.basis = GpcBasis(Q, p=p, I="default", full_tensor=False)
        self.Q = Q
        self.u_alpha_i = []
        self.p = p

    def __repr__(self):
        """ Return a string representation of the GpcModel object

            Returns
            -------
            repr_string : str
                String representation of the GpcModel object showing its attributes and their values """
        
        attrs = vars(self)
        repr_string = ', '.join("%s: %s" % item for item in attrs.items())
        return repr_string

    def compute_coeffs_by_regression(self, q_k_j, u_k_i):
        """ Compute gPCE coefficients using regression method

            Parameters
            ----------
            q_k_j : array_like
                Input parameter samples

            u_k_i : array_like
                Responses corresponding to input samples"""
        
        xi_k_j = self.Q.params2germ(q_k_j)
        phi_k_alpha = self.basis.evaluate(xi_k_j)
        u_alpha_i = np.matmul(np.linalg.pinv(phi_k_alpha), u_k_i)
        self.u_alpha_i = u_alpha_i

    def compute_coeffs_by_projection(self, q_k_j, u_k_i, w_k):
        """ Compute gPCE coefficients using projection method
        
            Parameters
            ----------
            q_k_j : array_like
                Input parameter samples
                
            u_k_i : array_like
                Responses corresponding to input samples
                
            w_k : array_like
                Weights for the projection method"""
        

        xi_k_j = self.Q.params2germ(q_k_j)
        phi_k_alpha = self.basis.evaluate(xi_k_j)
        u_alpha_i = np.matmul(phi_k_alpha, np.diag(w_k), u_k_i)
        self.u_alpha_i = u_alpha_i
        
    def predict(self, q_k_j):
        """ Predict model response at given parameter points q_k_j

            Parameters
            ----------
            q_k_j : array_like
                Input parameter samples

            Returns
            -------
            u_k_i : numpy.array
                Predicted responses corresponding to input samples"""

        xi_k_j = self.Q.params2germ(q_k_j)
        phi_k_alpha = self.basis.evaluate(xi_k_j)
        u_k_i = np.matmul(phi_k_alpha, self.u_alpha_i)
        if u_k_i.ndim == 1:  # Check if the array is 1D
            u_k_i = u_k_i.reshape(1, -1)  # Reshape to (1, x)
        return u_k_i
    
    def train(self, q_train, y_train):
        """ Train the gPCE model using training data

            Parameters
            ----------
            q_train : array_like
                Training input parameter samples

            y_train : array_like
                Training responses corresponding to input samples 
                
            Returns
            -------
            mse : float
                Mean squared error on the training data """
        
        self.compute_coeffs_by_regression(q_train, y_train)
        y = self.predict(q_train)
        mse = mean_squared_error(y_train, y)
        print(f"Validation MSE: {mse:.4f}")
        return mse
    
    def train_and_evaluate(self, q_train, y_train, q_val, y_val):
        """ Train the gPCE model and evaluate on validation data

            Parameters
            ----------
            q_train : array_like
                Training input parameter samples

            y_train : array_like
                Training responses corresponding to input samples

            q_val : array_like
                Validation input parameter samples

            y_val : array_like
                Validation responses corresponding to input samples

            Returns
            -------
            mse_tr : float
                Mean squared error on the training data

            mse_vl : float
                Mean squared error on the validation data """
        
        self.compute_coeffs_by_regression(q_train, y_train)
        y_tr_pred = self.predict(q_train)
        y_vl_pred = self.predict(q_val)
        mse_tr = mean_squared_error(y_train, y_tr_pred)
        mse_vl = mean_squared_error(y_val, y_vl_pred)
        return mse_tr, mse_vl
    
    def mean(self):
        """ Compute the mean of the gPCE model

            Returns
            -------
            means : numpy.array
                Mean of the gPCE model """
        
        coeffs = self.u_alpha_i
        means = coeffs[0, :]
        return means
    
    def variance(self):
        """ Compute the variance of the gPCE model

            Returns
            -------
            variances : numpy.array
                Variance of the gPCE model """
        
        coeffs = self.u_alpha_i
        variances = np.sum(coeffs[1:, :]**2, axis=0)
        return variances
    
    def compute_partial_vars(self, model_obj, max_index=1):
        """ Compute partial variances and Sobol indices up to specified order

            Parameters
            ----------
            model_obj : GpcModel
                gPCE model object

            max_index : int, optional
                Maximum Sobol order to consider, by default 1

            Returns
            -------
            partial_var_df : pandas.DataFrame
                DataFrame of partial variances for each QoI and Sobol index

            sobol_index_df : pandas.DataFrame
                DataFrame of Sobol indices for each QoI and Sobol index

            total_var : numpy.array
                Total variance of each QoI """
        
        a_i_alpha = model_obj.model.u_alpha_i.T
        V_a_orig = model_obj.model.basis
        QoI_names = model_obj.QoI_names
        
        # Get the multiindex set and convert to a logical array
        V_a = copy.deepcopy(V_a_orig)
        I_a = V_a.I #210x6
        I_s = I_a.astype(bool) #210x6
        
        # Identify the alpha=0 term (mean) to exclude from total variance
        is_alpha0 = np.all(I_a == 0, axis=1)
        
        # Calculate total variance excluding alpha=0
        a_i_alpha_nonzero = a_i_alpha[:, ~is_alpha0]
        sqr_norm_nonzero = V_a_orig.norm(do_sqrt=False)[~is_alpha0]
        var_row_nonzero = np.multiply(a_i_alpha_nonzero**2, sqr_norm_nonzero.transpose())
        total_var = np.sum(var_row_nonzero, axis=1)[:, np.newaxis]

        # Get rid of indices with too high an order and the mean
        sobol_order = np.sum(I_s, axis=1)
        ind = (sobol_order > 0) & (sobol_order <= max_index)

        I_a = I_a[ind, :]
        I_s = I_s[ind, :]
        a_i_alpha = a_i_alpha[:, ind]
        V_a.I = I_a

        # Calculate variance of the a_i_alpha * F_alpha polynomials
        sqr_norm = V_a.norm(do_sqrt=False)
        var_row = np.multiply(a_i_alpha**2, sqr_norm.transpose())

        # Get unique rows from Sobol indices
        I_s, _, ind2 = np.unique(I_s, axis=0, return_index=True, return_inverse=True)
        M = V_a.size()[0]
        U = csr_matrix((np.ones(M), (np.arange(M), ind2)), shape=(M, len(I_s)))
        
        # Compute the partial variance
        partial_var = var_row @ U.toarray()

        # Sort partial variances by Sobol order
        order_criterion = np.column_stack([np.sum(I_s, axis=1), np.flip(I_s, axis=1)])
        sortind = np.lexsort([order_criterion[:, i] for i in reversed(range(order_criterion.shape[1]))])
        I_s = I_s[sortind]
        partial_var = partial_var[:, sortind]
        
        indexed_param_names = gpc_multiindex2param_names(I_s, self.Q.param_names())
        
        # Compute the Sobol indices
        sobol_index = np.divide(partial_var, total_var)
        
        partial_var_df = pd.DataFrame(partial_var, columns=indexed_param_names, index=QoI_names)
        sobol_index_df = pd.DataFrame(sobol_index, columns=indexed_param_names, index=QoI_names)
                
        return partial_var_df, sobol_index_df, total_var

    
    def get_shap_values(self, predict_fn, q, forced=False, explainer_type="kernelexplainer"):
        """ Compute SHAP values for the gPCE model predictions

            Parameters
            ----------
            predict_fn : function
                Prediction function of the gPCE model

            q : array_like
                Input parameter samples

            forced : bool, optional
                If True, force re-computation of SHAP values, by default False

            explainer_type : str, optional
                Type of SHAP explainer to use, by default "kernelexplainer"

            Returns
            -------
            shap_values : numpy.array
                SHAP values for the gPCE model predictions """
        
        if explainer_type == "kernelexplainer":
            if hasattr(self, 'explainer') == False or forced == True:
                explainer = shap.KernelExplainer(predict_fn, q)
                self.explainer = explainer
            shap_values = self.explainer(q)
        return shap_values
    
    def to_jsonld(self, model_id='v0'):
        """ Export the gPCE model metadata to JSON-LD format

            Parameters
            ----------
            model_id : str, optional
                Identifier for the model, by default 'v0'

            Returns
            -------
            jsonld : dict
                JSON-LD representation of the gPCE model metadata"""
        
        jsonld = {
                "@context": {
                    "mls": "https://ml-schema.github.io/documentation/mls.html",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
                },

                "@id": f"https://example.org/models/{model_id}",
                "@type": "mls:Model",
                "mls:implementsAlgorithm": {
                    "@id": 'https://en.wikipedia.org/wiki/Generalized_polynomial_chaos',
                    "@type": "mls:Algorithm",
                    "rdfs:label": "Generalized Polynomial Chaos",
                },

                "mls:hasHyperParameter": [
                    {
                        "@type": "mls:HyperParameterSetting",
                        "mls:hasParameterName": "p",
                        "mls:hasParameterValue": str(self.p)
                    }
                ],

                "mls:hasInput": [
                    {
                        "@type": "mls:Feature",
                        "mls:featureName": name,
                        "mls:hasDistribution": {
                            "@type": "mls:Distribution",
                            "mls:distributionType": dist.get_dist_type(),
                            "mls:params": str(dist.get_dist_params()),
                        }
                    }
                    for (name, dist) in self.Q.params.items()
                ]
            }
        
        return jsonld

# ##########################################################################################
#                           UTILS
# ##########################################################################################

def gpc_multiindex2param_names(I_s, param_names):
    """ Translates a multi-index set to a list of indexed parameter names.

        Parameters
        ----------
        I_s : array_like
            Multi-index set (rows are indices, columns correspond to dimensions).
        
        param_names : list of str 
            List of parameter names.

        Returns
        -------
        indexed_param_names : list of str
            List of indexed parameter names. """
    
    indexed_param_names = [None] * I_s.shape[0]  # Initialize output list
    max_d = np.max(np.sum(I_s, axis=1))  # Maximum Sobol order
    min_d = np.min(np.sum(I_s, axis=1))  # Minimum Sobol order

    ind_start = 0
    for i in range(min_d, max_d + 1):
        # Extract rows corresponding to the current degree (i)
        I_s_i = I_s[np.sum(I_s, axis=1) == i, :]
        l_i = I_s_i.shape[0]

        # Find indices where I_s_i equals 1
        indr, indc = np.where(I_s[np.sum(I_s, axis=1) == i, :] == 1)

        # Sort and reshape indices into groups
        IND = np.column_stack((indr, indc))
        IND = IND[np.argsort(IND[:, 0])]
        IND = IND[:, 1].reshape((l_i, i))  # Extract column indices

        # Map indices to parameter names
        param_names_i = ["".join([param_names[idx] for idx in row]) for row in IND]

        # Add spaces between parameter names if degree > 1
        if i != 1:
            p_names_i = []
            for row in IND:
                p_names_i.append(" ".join(param_names[idx] for idx in row))
            indexed_param_names[ind_start:ind_start + l_i] = p_names_i
        else:
            indexed_param_names[ind_start:ind_start + l_i] = param_names_i

        ind_start += l_i
    return indexed_param_names