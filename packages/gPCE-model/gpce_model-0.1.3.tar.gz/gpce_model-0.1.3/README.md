# gPCE_model

[![DOI](https://zenodo.org/badge/1113758403.svg)](https://doi.org/10.5281/zenodo.17966291)

A Python package implementing generalized Polynomial Chaos Expansion (gPCE) for uncertainty quantification and surrogate modeling. The software is built on Elmar Zander's [sglib](https://github.com/ezander/sglib) approach.

- Website: [https://buildchain.ilab.sztaki.hu/](https://buildchain.ilab.sztaki.hu/)
- Source code: [https://github.com/TRACE-Structures/gPCE_model](https://github.com/TRACE-Structures/gPCE_model)
- Bug reports: [https://github.com/TRACE-Structures/gPCE_model/issues](https://github.com/TRACE-Structures/gPCE_model/issues)

## Overview

The `gPCE_model` package provides a complete framework for building and using generalized Polynomial Chaos Expansion (gPCE) surrogate models. These models efficiently approximate computational expensive simulations while quantifying uncertainty in the outputs. The implementation supports various polynomial systems, multi-index generation, and comprehensive uncertainty analysis including Sobol sensitivity indices.

## Installation

```bash
pip install gPCE-model
```

## Features

- **Generalized Polynomial Chaos Expansion**: Build surrogate models using orthogonal polynomial bases
- **Multiple Training Methods**: 
  - Regression-based coefficient computation
  - Projection-based coefficient computation
- **Multi-index Management**: Flexible basis construction with total degree or full tensor product
- **Uncertainty Quantification**:
  - Mean and variance computation
  - Sobol sensitivity indices (partial variances)
  - SHAP value integration for interpretability
- **Orthogonal Polynomial Support**: Works with various polynomial systems (Hermite, Legendre, Jacobi, etc.)
- **Model Export**: JSON-LD metadata export for interoperability

## Core Components

### GpcModel Class

The main class for generalized polynomial chaos expansion models.

**Key Attributes:**
- `basis`: GpcBasis object containing basis functions
- `Q`: VariableSet defining probabilistic input variables
- `u_alpha_i`: Coefficients of the gPCE expansion
- `p`: Maximum polynomial degree

**Key Methods:**
- `compute_coeffs_by_regression(q_k_j, u_k_i)`: Train using least squares regression
- `compute_coeffs_by_projection(q_k_j, u_k_i, w_k)`: Train using quadrature projection
- `predict(q_k_j)`: Predict output at new input points
- `mean()`: Compute mean of the gPCE model
- `variance()`: Compute variance of the gPCE model
- `compute_partial_vars(model_obj, max_index=1)`: Compute Sobol sensitivity indices

### GpcBasis Class

Manages the polynomial basis functions for gPCE.

**Key Attributes:**
- `m`: Number of random variables
- `syschars`: System characters defining polynomial types
- `p`: Maximum polynomial degree
- `I`: Multi-index set defining basis functions

**Key Methods:**
- `evaluate(xi, dual=False)`: Evaluate basis functions at given points
- `norm(do_sqrt=True)`: Compute norm of basis functions
- `size()`: Get size of the multi-index set

### Multi-index Functions

Functions for generating and managing multi-index sets.

- `multiindex(m, p, full_tensor=False)`: Generate multi-index set for m variables and degree p
- `np_sortrows(M, columns=None)`: Sort rows of 2D array by specified columns

## Authors and acknowledgment

The code is developed by András Urbanics, Bence Popovics, Emese Vastag, Elmar Zander and Noémi Friedman in the TRACE-Structures group.

This work has been funded by the European Commission Horizon Europe Innovation Action project 101092052 [BUILDCHAIN](https://buildchain-project.eu/)

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0-only). See the [LICENSE](https://github.com/TRACE-Structures/gPCE_model/tree/main?tab=GPL-3.0-1-ov-file) file for details.

## Related Projects

- [uncertain_variables](https://github.com/TRACE-Structures/uncertain_variables/): Probabilistic variable management
- [digital_twinning](https://github.com/TRACE-Structures/gPCE_model/): Digital Twinning

## Support

For questions or issues, please refer to the project repository or contact the development team.
