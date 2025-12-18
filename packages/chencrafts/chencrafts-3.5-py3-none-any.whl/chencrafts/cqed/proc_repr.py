__all__ = [
    'pauli_basis',
    'pauli_col_vec_basis',
    'pauli_row_vec_basis',
    'nq_pauli_basis',
    'nq_pauli_col_vec_basis',
    'nq_pauli_row_vec_basis',
    'ij_col_vec_basis',
    'pauli_stru_const',
    'bloch_vec_by_op', 'op_by_bloch_vec',
    'to_orth_chi', 'orth_chi_to_choi', 
    'Stinespring_to_Kraus',
    'NqProcessProb',
]

import numpy as np
import qutip as qt
from typing import List, Tuple, Dict, Any, Mapping, Literal

    
# Pauli basis, but normalized according to Hilbert-Schmidt inner product
pauli_basis: List[qt.Qobj] = [
    qt.qeye(2) / np.sqrt(2), 
    qt.sigmax() / np.sqrt(2), 
    qt.sigmay() / np.sqrt(2), 
    qt.sigmaz() / np.sqrt(2)
] 

pauli_col_vec_basis: List[qt.Qobj] = [
    qt.operator_to_vector(pauli) for pauli in pauli_basis
]
pauli_row_vec_basis: List[qt.Qobj] = [
    qt.operator_to_vector(pauli.trans()) for pauli in pauli_basis
]

def nq_pauli_basis(n: int) -> List[qt.Qobj]:
    basis = []
    for idx in np.ndindex((4,) * n):
        basis.append(qt.tensor(*[pauli_basis[i] for i in idx]))
    return basis
        
def nq_pauli_col_vec_basis(n: int) -> List[qt.Qobj]:
    return [qt.operator_to_vector(pauli) for pauli in nq_pauli_basis(n)]

def nq_pauli_row_vec_basis(n: int) -> List[qt.Qobj]:
    return [qt.operator_to_vector(pauli.trans()) for pauli in nq_pauli_basis(n)]

# |i><j| basis
ij_col_vec_basis: List[qt.Qobj] = [
    qt.operator_to_vector(qt.basis(2, j) * qt.basis(2, i).dag()) 
    for i in range(2) for j in range(2)
]   # column stacking

# structure constant, determines the multiplication of Pauli operators
# \sigma_a \sigma_b = f_{abc} \sigma_c
# Given the Pauli operators are orthonormal, we can get f_{abc} by
# f_{abc} = \text{tr} (\sigma_a \sigma_b \sigma_c^\dagger)
pauli_stru_const = np.array([
    [
        [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j]
    ],
    [
        [0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
        [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 0.+0.j, 0.+1.j],
        [0.+0.j, 0.+0.j, 0.-1.j, 0.+0.j]
    ],
    [
        [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j],
        [0.+0.j, 0.+0.j, 0.+0.j, 0.-1.j],
        [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
        [0.+0.j, 0.+1.j, 0.+0.j, 0.+0.j]
    ],
    [
        [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j],
        [0.+0.j, 0.+0.j, 0.+1.j, 0.+0.j],
        [0.+0.j, 0.-1.j, 0.+0.j, 0.+0.j],
        [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j]
    ]
]) / np.sqrt(2)

def bloch_vec_by_op(op: qt.Qobj) -> np.ndarray:
    """
    Given an 2^n *2^n operator, return its Bloch vector representation
    """
    dims = op.dims[0]
    len_qubits = len(dims)
    assert all(dim == 2 for dim in dims), "Only support multi-qubit tensor product operators."
    basis = nq_pauli_basis(len_qubits)
    return np.array([(pauli.dag() * op).tr() for pauli in basis], dtype=complex)

def op_by_bloch_vec(bloch_vec: np.ndarray) -> qt.Qobj:
    """
    Given a Bloch vector, return the corresponding 2^n *2^n operator
    """
    total_dim = bloch_vec.shape[0]
    num_q = int(np.log2(total_dim))
    assert np.abs(num_q % 1) < 1e-8, "The dimension of the bloch vector should be a power of 2."
    basis = nq_pauli_basis(num_q)
    return sum([bloch * pauli for bloch, pauli in zip(bloch_vec, basis)])

def to_orth_chi(
    superop: qt.Qobj, 
    basis: np.ndarray | List | None = None
) -> qt.Qobj:
    """
    Given a superoperator, return its orthogonal chi representation.
    
    Note that it is simply scaled from qt.to_chi(), it seems that qt.to_chi() 
    only uses the Pauli row vector basis, with a different scaling factor.
    """
    choi = qt.to_choi(superop)
    proc_orth_chi = np.zeros(choi.shape, dtype=complex)
    
    if basis is None:
        dims = choi.dims[0][0]
        num_q = len(dims)
        basis = nq_pauli_col_vec_basis(num_q)
    else:
        assert len(basis) == choi.shape[0], "The number of basis should be the same as the dimension of the Choi matrix."
    
    for i, pauli_i in enumerate(basis):
        for j, pauli_j in enumerate(basis):
            proc_orth_chi[i, j] = (pauli_i.dag() * choi * pauli_j)
    return qt.Qobj(proc_orth_chi, dims=choi.dims, superrep='orth_chi')

def orth_chi_to_choi(
    chi: qt.Qobj, 
    basis: np.ndarray | List | None = None
) -> qt.Qobj:
    """
    Given an orthogonal chi representation of a superoperator, return the 
    corresponding Choi matrix.
    """
    assert chi.superrep == 'orth_chi'
    choi = qt.Qobj(np.zeros(chi.shape, dtype=complex), dims=chi.dims, superrep='choi')
    if basis is None:
        dims = chi.dims[0][0]
        num_q = len(dims)
        basis = nq_pauli_row_vec_basis(num_q)
    else:
        assert len(basis) == chi.shape[0], "The number of basis should be the same as the dimension of the Chi matrix."
    for i, pauli_i in enumerate(basis):
        for j, pauli_j in enumerate(basis):
            choi += (pauli_i * pauli_j.dag() * chi[i, j])
    return choi


def _construct_env_state(
    dims: List[int] | Tuple[int, ...],
    env_indices: List[int] | Tuple[int, ...],
    env_state_label: List[int] | Tuple[int, ...],
) -> qt.Qobj:
    """
    Construct the environment state vector, tensor product with the system
    identity operator.
    
    Parameters
    ----------
    dims: List[int]
        the dimensions of the composite Hilbert space
    env_indices: List[int]
        the indices of the environment in the composite Hilbert space
    env_state_label: List[int]
        the state of the environment
    """
    ingredients = []
    for idx, dim in enumerate(dims):
        if idx in env_indices:
            ingredients.append(qt.basis(dim, env_state_label[env_indices.index(idx)]))
        else:
            ingredients.append(qt.qeye(dim))
    return qt.tensor(*ingredients)
    
def Stinespring_to_Kraus(
    sys_env_prop: qt.Qobj,
    sys_indices: int | List[int],
    env_state_label: int | List[int] | Tuple[int, ...] | None = None,
):
    """
    Convert a system-environment unitary to a list of Kraus operators. It's like
    a partial trace of the propagator.
    
    sys_prop(rho) = Tr_env[sys_env_prop * (rho x env_state) * sys_env_prop.dag()]
    
    Parameters
    ----------
    sys_env_prop: qt.Qobj
        the propagator acting on the composite Hilbert space of system + environment.
    sys_indices: int | List[int]
        the indices of the system in the composite Hilbert space
    env_state_label: qt.Qobj | int | List[int] | Tuple[int, ...] | None = None
        the state of the environment. If None, the environment is set to be the 
        ground state.
        
    Returns
    -------
    List[qt.Qobj]
        a list of Kraus operators
    """
    dims: List[int] = sys_env_prop.dims[0]
    
    if isinstance(sys_indices, int):
        sys_indices = [sys_indices]
    all_indices = list(range(len(dims)))
    env_indices = [idx for idx in all_indices if idx not in sys_indices]
    
    env_dims = [dims[idx] for idx in env_indices]
    
    # construct the state of the environment when doing partial trace
    if env_state_label is None:
        env_state_label = [0] * len(env_indices)
    if isinstance(env_state_label, int):
        env_state_label = [env_state_label]
    env_state_vec = _construct_env_state(
        dims = dims,
        env_indices = env_indices,
        env_state_label = env_state_label,
    )
    
    # construct an orthonormal basis for the environment
    env_basis = []
    for state_label in np.ndindex(tuple(env_dims)):
        env_basis.append(_construct_env_state(
            dims = dims,
            env_indices = env_indices,
            env_state_label = state_label,
        ))
        
    # calculate the Kraus operators
    kraus_ops = [
        basis.dag() * sys_env_prop * env_state_vec 
        for basis in env_basis
    ]
    
    return kraus_ops 


class NqProcessProb:
    """
    Represent a multi-qubit operator (usually a unitary) into a bloch 
    vector, and categorize the matrix elements by:
    
    - identity process: I
    - single qubit processes: 
        - control qubit rotation (XYZ), 
        - target qubit rotation (XYZ), 
        - spectator qubit(s) rotation (XYZ), 
    - 2-qubit process: 
        - control-target 
        - control-spectator(s)
        - target-spectator(s)
    - rest (3-qubit and above processes)
    - leakage
    
    Parameters
    ----------
    process: qt.Qobj
        the multi-qubit operator (usually a unitary)
    spectator_indices: List[int] = []
        the indices of the spectator qubits. Their mutual two
        
    """
    identity: float
    leakage: float
    _single_qubit_procs: Dict[int, Dict[str, float]]
    _two_qubit_procs: Dict[Tuple[int, int], Dict[str, float]]
    _rest_procs: Dict[str, float]
    
    def __init__(
        self,
        process: qt.Qobj,
        spectator_indices: List[int] = [],
        order_by_prob: bool = True,
        store_prob_amplitude: bool = False,
    ):
        dims = process.dims[0]
        self.num_q = len(dims)
        assert all(dim == 2 for dim in dims), "Only support multi-qubit tensor product operators."
        
        self.process = process
        self.bloch_vec = bloch_vec_by_op(process)
        self.spectator_indices = spectator_indices
        self.order_by_prob = order_by_prob
        self.store_prob_amplitude = store_prob_amplitude
        
        self._categorize()
        
    @property
    def data_qubit_indices(self) -> List[int]:
        return [
            idx for idx in range(self.num_q) 
            if idx not in self.spectator_indices
        ]
        
    @staticmethod
    def _nonzero_indices_and_values(int_tuple: Tuple[int, ...]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        return tuple(zip(
            *[[i, val] for i, val in enumerate(int_tuple) if val != 0],
        ))  # type: ignore
            
    def _categorize(self):
        if not self.store_prob_amplitude:
            data = np.abs(self.bloch_vec)**2 / (2**self.num_q)
        else:
            data = self.bloch_vec / np.sqrt(2**self.num_q)
        
        self._single_qubit_procs = {
            idx: {} for idx in range(self.num_q)
        }
        self._two_qubit_procs = {
            (idx1, idx2): {} 
            for idx1 in range(self.num_q) 
            for idx2 in range(idx1 + 1, self.num_q)
        }
        self._rest_procs = {}
        
        pauli_names = "IXYZ"
        for multi_pauli_idx, prob in enumerate(data):
            
            # unraveled_idx stores the pauli operator indices for each qubit
            pauli_idx_by_qubit = np.unravel_index(multi_pauli_idx, (4,) * self.num_q)
            
            if pauli_idx_by_qubit.count(0) == self.num_q:
                # identity process
                self.identity = prob
                continue
            
            elif pauli_idx_by_qubit.count(0) == self.num_q - 1:
                # single qubit processes
                qubit_idx, pauli_idx = self._nonzero_indices_and_values(pauli_idx_by_qubit)
                proc_name = pauli_names[pauli_idx[0]]
                self._single_qubit_procs[qubit_idx[0]][proc_name] = prob
                continue
            
            elif pauli_idx_by_qubit.count(0) == self.num_q - 2:
                # two qubit processes
                qubit_indices, pauli_idx = self._nonzero_indices_and_values(pauli_idx_by_qubit)
                proc_name = pauli_names[pauli_idx[0]] + pauli_names[pauli_idx[1]]
                self._two_qubit_procs[qubit_indices][proc_name] = prob
                continue
            
            # rest processes
            proc_name = "".join(pauli_names[idx] for idx in pauli_idx_by_qubit)
            self._rest_procs[proc_name] = prob
        
        self.leakage = 1 - np.sum(data)
        
        if self.order_by_prob:
            self._single_qubit_procs = {
                idx: self._order_dict_by_value(procs)
                for idx, procs in self._single_qubit_procs.items()
            }
            self._two_qubit_procs = {
                idx: self._order_dict_by_value(procs)
                for idx, procs in self._two_qubit_procs.items()
            }
            self._rest_procs = self._order_dict_by_value(self._rest_procs)
            
    def single_qubit_procs(
        self, include: Literal["both", "spec", "data"] = "data"
    ) -> Dict[int, Dict[str, float]]:
        """
        A dictionary of single qubit processes.
        
        Parameters
        ----------
        include: Literal["both", "spec", "data"]
            the indices of the qubits to include.
            
        Returns
        -------
        Dict[int, Dict[str, float]]
            a dictionary of single qubit processes.
        """
        if include == "data":
            qubit_indices = self.data_qubit_indices
        elif include == "spec":
            qubit_indices = self.spectator_indices
        elif include == "both":
            qubit_indices = list(range(self.num_q))
        else:
            raise ValueError(f"Invalid include value: {include}")
        
        return {
            idx: procs for idx, procs in self._single_qubit_procs.items()
            if idx in qubit_indices
        }
        
    def two_qubit_procs(
        self, include: Literal["both", "spec", "data"] = "data"
    ) -> Dict[Tuple[int, int], Dict[str, float]]:
        """
        A dictionary of two qubit processes.
        
        Parameters
        ----------
        include: Literal["both", "spec", "data"]
            the indices of the qubits to include. Note that when include = 
            "spec", processes involving ANY ONE of the spectator qubits are 
            included; when include = "data", processes involving BOTH data 
            qubits are included.
            
        Returns
        -------
        Dict[Tuple[int, int], Dict[str, float]]
            a dictionary of two qubit processes.
        """
        two_qubit_indices = list(self._two_qubit_procs.keys())
        if include == "data":
            data_qubit_indices = self.data_qubit_indices
            two_qubit_indices = [
                (idx1, idx2) for idx1, idx2 in two_qubit_indices
                if idx1 in data_qubit_indices and idx2 in data_qubit_indices
            ]
        elif include == "spec":
            spectator_indices = self.spectator_indices
            two_qubit_indices = [
                (idx1, idx2) for idx1, idx2 in two_qubit_indices
                if idx1 in spectator_indices or idx2 in spectator_indices
            ]
        elif include == "both":
            pass
        else:
            raise ValueError(f"Invalid include value: {include}")
        
        return {
            (idx1, idx2): procs for (idx1, idx2), procs in self._two_qubit_procs.items()
            if (idx1, idx2) in two_qubit_indices
        }
        
    def rest_procs(
        self, include_spec: bool = True
    ) -> Dict[int | Tuple[int, int] | str, Dict[str, float] | float]:
        """
        A dictionary of rest processes, including 
        - processes involving more than two qubits
        - when include_spec = True, single or two qubit processes involving ANY ONE of the spectator qubit(s)
        
        Parameters
        ----------
        include: Literal["both", "spec", "data"]
            the indices of the qubits to include. In the two qubit processes, 
            
        Returns
        -------
        Dict[int | Tuple[int, int] | str, Dict[str, float] | float]
            a dictionary of rest processes.
        """
        if not include_spec:
            return self._rest_procs # type: ignore
        
        rest_procs = self._rest_procs.copy()
        single_qubit_procs = self.single_qubit_procs(include="spec")
        two_qubit_procs = self.two_qubit_procs(include="spec")
        
        return single_qubit_procs | two_qubit_procs | rest_procs
            
    def _order_dict_by_value(self, d: Dict[str, float]) -> Dict[str, float]:
        return dict(sorted(
            d.items(), 
            key=lambda item: np.abs(item[1]), 
            reverse=True)
        )
        
    def single_qubit_procs_prob(self, include: Literal["both", "spec", "data"] = "data"):
        """
        The probability of single qubit processes.
        
        Parameters
        ----------
        include: Literal["both", "spec", "data"]
            the indices of the qubits to include.
            
        Returns
        -------
        float
            the probability of single qubit processes.
        """
        values = np.array([list(d.values()) for d in self.single_qubit_procs(include).values()])
        if self.store_prob_amplitude:
            return np.sum(values**2)
        else:
            return np.sum(values)
        
    def two_qubit_procs_prob(self, include: Literal["both", "spec", "data"] = "data"):
        """
        The probability of two qubit processes.
        
        Parameters
        ----------
        include: Literal["both", "spec", "data"]
            the indices of the qubits to include.
            
        Returns
        -------
        float
            the probability of two qubit processes.
        """
        values = np.array([list(d.values()) for d in self.two_qubit_procs(include).values()])
        if self.store_prob_amplitude:
            return np.sum(values**2)
        else:
            return np.sum(values)
        
    def rest_procs_prob(self, include_spec: bool = True):
        """
        The probability of rest processes.
        
        Parameters
        ----------
        include_spec: bool
            whether to include processes involving spectator qubits.
            
        Returns
        -------
        float
            the probability of rest processes.
        """
        total_prob = 0
        for value in self.rest_procs(include_spec).values():
            if isinstance(value, dict):
                values = np.array(list(value.values()))
                if self.store_prob_amplitude:
                    total_prob += np.sum(values**2)
                else:
                    total_prob += np.sum(values)
            else:
                if self.store_prob_amplitude:
                    total_prob += np.abs(value)**2
                else:
                    total_prob += value
        return total_prob
        
    def _dict_items_to_str(
        self, 
        d: Mapping[Any, float | Dict], 
        prefix: str = "\t"
    ) -> str:
        str_list = []
        for key, value in d.items():
            if isinstance(value, dict):
                value = "\n" + self._dict_items_to_str(value, prefix*2)
            elif isinstance(value, float | complex):
                value = f"{value:.3e}"
            else:
                raise ValueError(f"Invalid value type: {type(value)}")
            str_list.append(f"{prefix}{key}: {value}")
        return "\n".join(str_list)

    def __str__(self):
        return f"""NqProcessProb (num_q={self.num_q}, store_prob_amplitude={self.store_prob_amplitude}):
- Identity: {self.identity:.3e}
- Leakage: {self.leakage:.3e}
- Single qubit processes: {self.single_qubit_procs_prob("data"):.3e}
{self._dict_items_to_str(self.single_qubit_procs("data"))}
- Two qubit processes: {self.two_qubit_procs_prob("data"):.3e}
{self._dict_items_to_str(self.two_qubit_procs("data"))}
- Rest processes: {self.rest_procs_prob(True):.3e}
{self._dict_items_to_str(self.rest_procs(True))}
"""

    def __repr__(self):
        return self.__str__()
