__all__ = [
    "superop_evolve_dq",
    "steadystate_dq", 
    "steadystate_floquet_full_dq", 
    "nuc_norm_smooth",
]

import dynamiqs as dq
import jax.numpy as jnp
from jax import jit
from functools import partial
from dataclasses import replace
from typing import List, Tuple, Dict

def superop_evolve_dq(superop: dq.QArray, state: dq.QArray) -> dq.QArray:
    """
    Evolve a density matrix with a superoperator.
    """
    if not state.vectorized:
        state_vec = dq.vectorize(state)
    else:
        state_vec = state
    evolved_vec = superop @ state_vec
    return replace(dq.unvectorize(evolved_vec), dims=state.dims)

@partial(jit, static_argnames=("dim",))
def _steady_state_svd(L: jnp.ndarray, dim: int) -> jnp.ndarray:
    """
    Find steady state of Liouvillian L using SVD.
    Returns the vector v such that Lv ≈ 0.
    
    Parameters:
    -----------
    L : jnp.ndarray
        Liouvillian (dim^2 x dim^2)
    dim : int
        Hilbert space dimension (static argument)
        
    Returns:
    --------
    steady_state : jnp.ndarray
        Steady state density matrix (dim x dim)
    """
    # Compute SVD: L = U @ S @ Vh
    U, S, Vh = jnp.linalg.svd(L, full_matrices=False)
    
    # The steady state is the right singular vector 
    # corresponding to the smallest singular value (closest to 0)
    steady_state = Vh[-1, :].reshape(dim, dim)
    
    # Normalize to trace 1 (assuming vectorized density matrix)
    steady_state = steady_state / jnp.trace(steady_state)
    
    return steady_state


@partial(jit, static_argnames=("dim", "n_iter"))
def _steady_state_power(L: jnp.ndarray, dim: int, n_iter: int = 50) -> jnp.ndarray:
    """
    Find steady state of Liouvillian L using inverse power iteration.
    Returns the vector v such that Lv ≈ 0.
    
    This method is more stable for automatic differentiation than SVD,
    as it avoids extracting singular vectors.
    
    Parameters:
    -----------
    L : jnp.ndarray
        Liouvillian (dim^2 x dim^2)
    dim : int
        Hilbert space dimension (static argument)
    n_iter : int
        Number of power iterations (default: 50)
        
    Returns:
    --------
    steady_state : jnp.ndarray
        Steady state density matrix (dim x dim)
    """
    # Inverse power iteration to find smallest eigenvector
    # Start with uniform vector
    rho_vec = jnp.ones(dim * dim, dtype=L.dtype) / jnp.sqrt(dim * dim)
    
    # We want to find x such that L @ x ≈ 0
    # Use inverse iteration: x_{n+1} = (L†L + εI)^{-1} x_n
    L_dag_L = L.conj().T @ L
    eps = 1e-8
    
    # Iterate to find smallest eigenvector
    for _ in range(n_iter):
        rho_vec = jnp.linalg.solve(L_dag_L + eps * jnp.eye(dim*dim), rho_vec)
        rho_vec = rho_vec / jnp.linalg.norm(rho_vec)
    
    # Reshape to density matrix
    rho = rho_vec.reshape(dim, dim)
    
    # Make hermitian
    rho = (rho + rho.conj().T) / 2
    
    # Normalize to trace 1
    trace = jnp.trace(rho)
    rho = rho / (jnp.abs(trace) + 1e-10)
    
    # Make trace real and positive
    trace_phase = jnp.angle(jnp.trace(rho))
    rho = rho * jnp.exp(-1j * trace_phase)
    
    return rho


@partial(jit, static_argnames=("dim",))
def _steady_state_solve(L: jnp.ndarray, dim: int) -> jnp.ndarray:
    """
    Find steady state of Liouvillian L using direct linear solve with constraint.
    Returns the vector v such that Lv = 0 and Tr(v) = 1.
    
    This method is fast and has well-defined gradients. It solves the constrained
    system directly using a modified linear system.
    
    Parameters:
    -----------
    L : jnp.ndarray
        Liouvillian (dim^2 x dim^2)
    dim : int
        Hilbert space dimension (static argument)
        
    Returns:
    --------
    steady_state : jnp.ndarray
        Steady state density matrix (dim x dim)
    """
    # We want to solve: L @ ρ_vec = 0 with constraint Tr(ρ) = 1
    # 
    # Method: Replace one equation in L with the trace constraint
    # This makes the system non-singular and directly solvable
    # 
    # Modified system:
    #   L[:-1] @ ρ_vec = 0
    #   trace_constraint @ ρ_vec = 1
    
    dim_sq = dim * dim
    
    # Create trace constraint vector (picks out diagonal elements)
    trace_vec = jnp.zeros(dim_sq, dtype=L.dtype)
    for i in range(dim):
        trace_vec = trace_vec.at[i * dim + i].set(1.0)
    
    # Modify L: replace last row with trace constraint
    L_mod = L.at[-1, :].set(trace_vec)
    
    # Right-hand side: all zeros except last element = 1 (trace constraint)
    b = jnp.zeros(dim_sq, dtype=L.dtype)
    b = b.at[-1].set(1.0)
    
    # Solve the modified system
    rho_vec = jnp.linalg.solve(L_mod, b)
    
    # Reshape to density matrix
    rho = rho_vec.reshape(dim, dim)
    
    # Make hermitian (should already be close)
    rho = (rho + rho.conj().T) / 2
    
    # Renormalize trace to exactly 1 (numerical cleanup)
    trace = jnp.trace(rho)
    rho = rho / (trace + 1e-10)
    
    return rho


def steadystate_dq(
    H_0: dq.QArray, 
    c_ops: List[dq.QArray] = [],
    method: str = "solve",
    n_iter: int = 50,
) -> dq.QArray:
    """
    Find steady state of Liouvillian L.
    Returns the density matrix ρ such that L(ρ) = 0.
    
    Parameters
    ----------
    H_0 : dq.QArrayLike
        Static Hamiltonian or Liouvillian
    c_ops : list[dq.QArrayLike]
        List of collapse operators
    method : str, optional
        Method to use (default: "solve"):
        - "solve": Direct linear solve with trace constraint 
                   (fastest, stable gradients, best for most cases)
        - "power": Inverse power iteration 
                   (slower, very stable gradients, good for ill-conditioned systems)
        - "svd": Singular Value Decomposition 
                 (fast, unstable gradients for near-zero singular values)
    n_iter : int, optional
        Number of iterations for power method (default: 50, ignored for other methods)
        
    Returns:
    --------
    steady_state : dq.QArray
        Steady state density matrix
        
    Notes
    -----
    **Method comparison:**
    
    - "solve" (recommended): Directly solves L@ρ=0 with trace constraint. 
      Fast single linear solve, stable gradients via jnp.linalg.solve.
      
    - "power": Iterative method that converges to null space. More robust for
      difficult systems but slower (requires n_iter solves).
      
    - "svd": Traditional method but gradients can be numerically unstable when
      singular values are near zero (which is always the case for steady states).
    
    **For gradient-based optimization, use "solve" or "power".**
    
    Examples
    --------
    >>> # Basic usage
    >>> rho_ss = steadystate(H, c_ops)
    
    >>> # For gradient computation
    >>> rho_ss = steadystate(H, c_ops, method="solve")  # Recommended
    >>> val, grad = jax.value_and_grad(loss_fn)(params)
    
    >>> # For difficult/ill-conditioned systems
    >>> rho_ss = steadystate(H, c_ops, method="power", n_iter=100)
    """
    # check if H_0 is already a Liouvillian    
    dim_prod = int(jnp.prod(jnp.asarray(H_0.dims)))
    if H_0.vectorized:
        L = H_0
        assert len(c_ops) == 0, "c_ops must be empty if H_0 is a Liouvillian"
    else:
        L = dq.slindbladian(H_0, c_ops)
    
    # Choose method
    if method == "svd":
        rho = _steady_state_svd(L.to_jax(), dim_prod)
    elif method == "power":
        rho = _steady_state_power(L.to_jax(), dim_prod, n_iter)
    elif method == "solve":
        rho = _steady_state_solve(L.to_jax(), dim_prod)
    else:
        raise ValueError(f"Unknown method '{method}'. Choose 'svd', 'power', or 'solve'.")
        
    return dq.asqarray(rho, dims=L.dims).unit()

def steadystate_floquet_full_dq(
    H_0: dq.QArray, 
    c_ops: List[dq.QArray], 
    Op_t: dq.QArray,
    w_d: float, 
    n_it: int = 3,
) -> Dict[int, dq.QArray]:
    """
    Calculates the effective steady state for a driven
     system with a time-dependent cosinusoidal term:

    .. math::

        \\mathcal{\\hat{H}}(t) = \\hat{H}_0 +
         \\mathcal{\\hat{O}} \\cos(\\omega_d t)

    Parameters
    ----------
    H_0 : :obj:`.Qobj`
        A Hamiltonian or Liouvillian operator.

    c_ops : list
        A list of collapse operators.

    Op_t : :obj:`.Qobj`
        The the interaction operator which is multiplied by the cosine

    w_d : float, default: 1.0
        The frequency of the drive

    n_it : int, default: 3
        The number of iterations for the solver

    Returns
    -------
    rho_dict : Dict[int, dq.QArray]
        A dictionary of the steady-state density matrices for each Fourier
        component. The full time-periodic steady state is given by:
        rho(t) = sum_{n=-inf}^{inf} rho_n exp(i n w_d t)
    
    Notes
    -----
    See: Sze Meng Tan,
    https://painterlab.caltech.edu/wp-content/uploads/2019/06/qe_quantum_optics_toolbox.pdf,
    Section (16)
    """
    # Create Liouvillians
    L_0 = dq.slindbladian(H_0, c_ops)
    L_m = 0.5 * dq.slindbladian(Op_t, [])
    L_p = 0.5 * dq.slindbladian(Op_t, [])
    
    L_0_jax, L_m_jax, L_p_jax = (
        L_0.to_jax(), L_m.to_jax(), L_p.to_jax()
    )
    S_jax = jnp.zeros_like(L_0_jax)
    T_jax = jnp.zeros_like(L_0_jax)
    Id_jax = jnp.eye(L_0.shape[0], dtype=L_0.dtype)

    # convert to jax arrays for the loop
    S_jax_dict = {n_it + 1: S_jax}
    T_jax_dict = {-(n_it + 1): T_jax}
    for n in range(n_it, 0, -1):
        # for S
        L_S = L_0_jax - 1j * n * w_d * Id_jax + L_m_jax @ S_jax_dict[n+1]
        S_jax_new = -jnp.linalg.solve(L_S, L_p_jax)
        S_jax_dict[n] = S_jax_new
        
        # for T
        L_T = L_0_jax + 1j * n * w_d * Id_jax + L_p_jax @ T_jax_dict[-n-1]
        T_jax_new = -jnp.linalg.solve(L_T, L_m_jax)
        T_jax_dict[-n] = T_jax_new
    
    M_subs_jax = L_0_jax + L_m_jax @ S_jax_dict[1] + L_p_jax @ T_jax_dict[-1]
    M_subs = replace(dq.asqarray(M_subs_jax), dims=H_0.dims, vectorized=True)
    rho_0 = replace(steadystate_dq(M_subs), dims=H_0.dims)

    rho_dict = {0: rho_0}

    S_dict = {n: replace(dq.asqarray(S_jax_dict[n]), dims=L_0.dims, vectorized=True) for n in range(1, n_it + 2)}
    T_dict = {n: replace(dq.asqarray(T_jax_dict[n]), dims=L_0.dims, vectorized=True) for n in range(-n_it-1, 0)}

    for n in range(1, n_it + 2):
        rho_dict[n] = superop_evolve_dq(S_dict[n], rho_dict[n-1])
        rho_dict[-n] = superop_evolve_dq(T_dict[-n], rho_dict[-n+1])
            
    return rho_dict

def nuc_norm_smooth(rho: dq.QArray, eps: float = 1e-8) -> float:
    """
    Smoothed nuclear norm. This avoids the gradient singularity at zero.
    """
    rho_jax = rho.to_jax()
    # Add small identity for numerical stability
    dim = rho_jax.shape[0]
    diff_reg = rho_jax + eps * jnp.eye(dim) / dim
    return jnp.linalg.norm(diff_reg, ord="nuc")
