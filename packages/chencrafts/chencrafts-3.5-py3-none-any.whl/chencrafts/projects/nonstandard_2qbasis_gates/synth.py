__all__ = [
    'OneLayerSynth',
    'OneLayerSynthKAK',
]

import numpy as np
import qutip as qt
from chencrafts.cqed.qt_helper import old_leakage_amount
from chencrafts.projects.nonstandard_2qbasis_gates.kak import KAK2Q
from typing import List, Tuple

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False 


class SynthBase:
    def __init__(
        self, 
        original_U: np.ndarray | qt.Qobj, 
        target_U: np.ndarray | qt.Qobj,
    ):
        """
        Initialize the synthesis class.
        
        Parameters
        ----------
        original_U: np.ndarray | qt.Qobj
            The original 2-qubit gate.
        target_U: np.ndarray | qt.Qobj
            The target 2-qubit gate.
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is a optional dependency for block_diag module."
                "Please install it via 'pip install torch' or 'conda install "
                "pytorch torchvision -c pytorch'."
            )
        
        self.original_U = (
            original_U if isinstance(original_U, np.ndarray) 
            else original_U.full()
        )
        self.target_U = (
            target_U if isinstance(target_U, np.ndarray) 
            else target_U.full()
        )
        self.leakage = old_leakage_amount(qt.Qobj(self.original_U))

    @staticmethod
    def _stack_tensor(nd_list: List) -> "torch.Tensor":
        """
        Stack a nD list of 0D torch tensor into a nD torch tensor.
        
        Typical usage:
        >>> stack_tensor([
            [alpha, beta],
            [gamma, delta],
        ])
        >>> tensor([
            [alpha, beta],
            [gamma, delta],
        ])
        where alpha, beta, gamma, delta are 0D torch tensor.
        """
        # recursively stack the tensor
        if not isinstance(nd_list[0], list):
            # we are at the last dimension
            return torch.stack(nd_list)
        
        tensor = torch.stack(
            [
                SynthBase._stack_tensor(l) for l in nd_list
            ],
            dim=0
        )
        
        return tensor
    
    @staticmethod
    def _su2_matrix(theta: "torch.Tensor", phi: "torch.Tensor", lam: "torch.Tensor") -> "torch.Tensor":
        """
        Generate the most general SU(2) matrix for a single qubit.
        
        [
            [cos(theta/2) * exp(1j * (phi + lam) / 2), -sin(theta/2) * exp(1j * (phi - lam) / 2)],
            [sin(theta/2) * exp(-1j * (phi - lam) / 2), cos(theta/2) * exp(-1j * (phi + lam) / 2)]
        ]
        
        This is the most general SU(2) matrix parameterization with 3 real parameters.
        
        Parameters
        ----------
        theta: torch.Tensor
            The rotation angle parameter (0 to π).
        phi: torch.Tensor
            The azimuthal angle parameter (0 to 2π).
        lam: torch.Tensor
            The additional phase parameter (0 to 2π).
            
        Returns
        -------
        torch.Tensor
            The SU(2) matrix.
        """
        cos_theta = torch.cos(theta / 2)
        sin_theta = torch.sin(theta / 2)
        exp_phi_plus_lam = torch.exp(1j * (phi + lam) / 2)
        exp_phi_minus_lam = torch.exp(1j * (phi - lam) / 2)
        return SynthBase._stack_tensor([
            [cos_theta * exp_phi_plus_lam, -sin_theta * exp_phi_minus_lam],
            [sin_theta * torch.conj(exp_phi_minus_lam), cos_theta * torch.conj(exp_phi_plus_lam)]
        ])

    @staticmethod
    def _kron_multi(*matrices: List["torch.Tensor"]) -> "torch.Tensor":
        """
        Compute the Kronecker product of multiple matrices.
        
        Parameters
        ----------
        *matrices: List[torch.Tensor]
            The matrices to be Kronecker producted.
            
        Returns
        -------
        torch.Tensor
            The Kronecker product of the matrices.
        """
        result = matrices[0]
        for matrix in matrices[1:]:
            result = torch.kron(result, matrix)
        return result

    @staticmethod
    def _su2_matrix_kron(
        theta: "torch.Tensor", 
        phi: "torch.Tensor", 
        lam: "torch.Tensor",
        num_qubits: int, 
        which_qubit: int,
    ) -> "torch.Tensor":
        """
        Generate the most general SU(2) matrix for a single qubit in the Kronecker product 
        basis of multi-qubit system.
        
        [
            [cos(theta/2) * exp(1j * (phi + lam) / 2), -sin(theta/2) * exp(1j * (phi - lam) / 2)],
            [sin(theta/2) * exp(-1j * (phi - lam) / 2), cos(theta/2) * exp(-1j * (phi + lam) / 2)]
        ]
        
        Parameters
        ----------
        theta: torch.Tensor
            The rotation angle parameter.
        phi: torch.Tensor
            The azimuthal angle parameter.
        lam: torch.Tensor
            The additional phase parameter.
        num_qubits: int
            The number of qubits.
        which_qubit: int
            The index of the qubit to apply the SU(2) matrix to.
            
        Returns
        -------
        torch.Tensor
            The SU(2) matrix for the qubit.
        """
        I = torch.eye(2, dtype=torch.complex128)
        I_list = [I] * num_qubits
        U = SynthBase._su2_matrix(theta, phi, lam)
        I_list[which_qubit] = U
        return SynthBase._kron_multi(*I_list)
    
    @staticmethod
    def _process_fidelity(
        oprt: "torch.Tensor", 
        tgt: "torch.Tensor",
    ) -> "torch.Tensor":
        """
        Compute the process fidelity between two matrices.
        
        Parameters
        ----------
        oprt: torch.Tensor
            The operator matrix.
        tgt: torch.Tensor
            The target matrix.
            
        Returns
        -------
        torch.Tensor
            The process fidelity.
        """
        d = oprt.shape[0]
        return torch.abs(torch.trace(oprt @ tgt.T.conj())) ** 2 / d ** 2


class OneLayerSynth(SynthBase):
    params: np.ndarray
    leakage: float
    
    def __init__(
        self, 
        original_U: np.ndarray | qt.Qobj, 
        target_U: np.ndarray | qt.Qobj,
        params: np.ndarray | None = None,
        qubit_pair: Tuple[int, int] = (0, 1),
        num_qubits: int = 2,
    ):
        """
        Synthesize a new 2-qubit gate from a given 2-qubit gate with 4 
        single qubit gates.
        
        new_U = L1 @ L2 @ original_U @ R2 @ R1
        
        Parameters
        ----------
        original_U: jnp.ndarray
            The 2-qubit gate to be synthesized.
        target_U: np.ndarray | qt.Qobj
            The target 2-qubit gate.
        params: np.ndarray | None
            The length-12 array for gates R1, R2, L1, L2, with each 
            being a theta, phi, lambda triplet. By default, it is zeros. After run()
            is called, it will be overwritten by the optimized parameters.
        qubit_pair: Tuple[int, int] = (0, 1)
            The qubit pair to be synthesized.
        num_qubits: int = 2
            The number of qubits (assume we are looking at a multi-qubit 
            system).
        """
        super().__init__(original_U, target_U)
        self.qA, self.qB = qubit_pair
        self.num_qubits = num_qubits
        if params is None:
            self.params = np.zeros(12, dtype=np.float64)
        else:
            self.params = params
            
    def _R1(self, params: "torch.Tensor", tensor: bool = False) -> "torch.Tensor":
        if tensor:
            return OneLayerSynth._su2_matrix_kron(
                params[0], params[1], params[2], self.num_qubits, self.qA
            )
        else:
            return OneLayerSynth._su2_matrix(params[0], params[1], params[2])
    
    def _R2(self, params: "torch.Tensor", tensor: bool = False) -> "torch.Tensor":
        if tensor:
            return OneLayerSynth._su2_matrix_kron(
                params[3], params[4], params[5], self.num_qubits, self.qB
            )
        else:
            return OneLayerSynth._su2_matrix(params[3], params[4], params[5])
    
    def _L1(self, params: "torch.Tensor", tensor: bool = False) -> "torch.Tensor":
        if tensor:
            return OneLayerSynth._su2_matrix_kron(
                params[6], params[7], params[8], self.num_qubits, self.qA
            )
        else:
            return OneLayerSynth._su2_matrix(params[6], params[7], params[8])
    
    def _L2(self, params: "torch.Tensor", tensor: bool = False) -> "torch.Tensor":
        if tensor:
            return OneLayerSynth._su2_matrix_kron(
                params[9], params[10], params[11], self.num_qubits, self.qB
            )
        else:
            return OneLayerSynth._su2_matrix(params[9], params[10], params[11])
        
    def _synth_1layer(
        self,
        params: "torch.Tensor", 
        original_U: "torch.Tensor",
    ):
        """
        Synthesize the 1-layer gate using KAK decomposition structure.
        
        Computes: L1 @ L2 @ original_U @ R2 @ R1
        
        Parameters
        ----------
        params: torch.Tensor
            The parameters for all the single qubit gates (R1, R2, L1, L2).
        original_U: torch.Tensor
            The original 2-qubit gate.
            
        Returns
        -------
        torch.Tensor
            The synthesized 2-qubit gate.
        """
        R1 = self._R1(params, tensor=True)
        R2 = self._R2(params, tensor=True)
        L1 = self._L1(params, tensor=True)
        L2 = self._L2(params, tensor=True)
        return L1 @ L2 @ original_U @ R2 @ R1

    def _cost_1layer(
        self,
        params: "torch.Tensor", 
        original_U: "torch.Tensor",
        target_U: "torch.Tensor",
    ):
        """
        Compute the cost function for the 1-layer gate, which is 1 - process_fidelity.
        
        Parameters
        ----------
        params: torch.Tensor
            The parameters for all the single qubit gates.
        original_U: torch.Tensor
            The original 2-qubit gate.
        target_U: torch.Tensor
            The target 2-qubit gate.
            
        Returns
        -------
        torch.Tensor
            The cost function = 1 - process_fidelity.
        """
        new_U = self._synth_1layer(params, original_U)
        return 1 - self._process_fidelity(new_U, target_U)
    
    def run(
        self,
        num_iter: int = 1000,
        tol: float = 1e-6,
        lr: float = 0.01,
        randomize_init: bool = False,
        random_seed: int | None = None,
    ):
        """
        Synthesize the 1-layer gate starting from initial parameters.
        
        Parameters
        ----------
        num_iter: int
            The number of iterations for the optimization.
        tol: float
            The tolerance for the optimization.
        lr: float
            The learning rate for the optimization.
        randomize_init: bool
            If True, initialize parameters randomly. If False, start from zeros.
        random_seed: int | None
            Random seed for reproducible random initialization. If None, uses
            current random state.
            
        Returns
        -------
        np.ndarray
            The parameters for all the single qubit gates.
        """
        orig_U_tensor = torch.tensor(self.original_U, dtype=torch.complex128)
        target_U_tensor = torch.tensor(self.target_U, dtype=torch.complex128)
        
        # Initialize parameters
        if randomize_init:
            # Set random seed if provided
            if random_seed is not None:
                torch.manual_seed(random_seed)
            
            # Initialize parameters randomly
            # theta: [0, π], phi: [0, 2π], lambda: [0, 2π]
            init_params = torch.zeros(12, dtype=torch.float64, requires_grad=True)
            with torch.no_grad():
                # Every 3rd parameter starting from 0 is theta (0 to π)
                init_params[0::3] = torch.rand(4) * np.pi
                # Every 3rd parameter starting from 1 is phi (0 to 2π)  
                init_params[1::3] = torch.rand(4) * 2 * np.pi
                # Every 3rd parameter starting from 2 is lambda (0 to 2π)
                init_params[2::3] = torch.rand(4) * 2 * np.pi
            init_params.requires_grad_(True)
        else:
            # Initialize with zeros (original behavior)
            init_params = torch.zeros(12, dtype=torch.float64, requires_grad=True)
        
        optimizer = torch.optim.Adam([init_params], lr=lr)
        
        # optimization loop
        for _ in range(num_iter):
            optimizer.zero_grad()
            loss = self._cost_1layer(init_params, orig_U_tensor, target_U_tensor)
            loss.backward()
            optimizer.step()
            
            if loss.item() < tol:
                break
            
        self.params = init_params.detach().numpy()
        
        return self.params
    
    def R1(self, tensor = False):
        return self._R1(
            torch.tensor(self.params, dtype=torch.float64), tensor=tensor
        ).detach().numpy()
    
    def R2(self, tensor = False):
        return self._R2(
            torch.tensor(self.params, dtype=torch.float64), tensor=tensor
        ).detach().numpy()
    
    def L1(self, tensor = False):
        return self._L1(
            torch.tensor(self.params, dtype=torch.float64), tensor=tensor
        ).detach().numpy()
    
    def L2(self, tensor = False):
        return self._L2(
            torch.tensor(self.params, dtype=torch.float64), tensor=tensor
        ).detach().numpy()
    
    @property
    def synth_U(self):
        """
        The synthesized 2-qubit gate.
        """
        result = self._synth_1layer(
            torch.tensor(self.params, dtype=torch.complex128), 
            torch.tensor(self.original_U, dtype=torch.complex128)
        )
        return result.detach().numpy()
    
    @property
    def original_fidelity(self):
        """
        The process fidelity between the original gate and the target gate.
        """
        return self._process_fidelity(
            torch.tensor(self.original_U, dtype=torch.complex128), 
            torch.tensor(self.target_U, dtype=torch.complex128)
        ).item()
    
    @property
    def synth_fidelity(self):
        """
        The process fidelity between the synthesized gate and the target gate.
        """
        return self._process_fidelity(
            torch.tensor(self.synth_U, dtype=torch.complex128), 
            torch.tensor(self.target_U, dtype=torch.complex128)
        ).item()
        
        
class OneLayerSynthKAK(SynthBase):
    """
    Alternative 1-layer synthesis using direct KAK decomposition matching.
    
    This class performs synthesis by directly comparing the KAK decompositions
    of the original and target unitaries and computing the required local
    unitaries analytically.
    
    For original_U = L_orig @ CAN_orig @ R_orig and target_U = L_tgt @ CAN_tgt @ R_tgt,
    we want to find local unitaries such that:
    L @ original_U @ R = target_U
    
    This gives us: L @ (L_orig @ CAN_orig @ R_orig) @ R = L_tgt @ CAN_tgt @ R_tgt
    
    If CAN_orig = CAN_tgt (same canonical gate), then:
    L @ L_orig = L_tgt  =>  L = L_tgt @ L_orig†
    R_orig @ R = R_tgt  =>  R = R_orig† @ R_tgt
    """
    
    def __init__(
        self, 
        original_U: np.ndarray | qt.Qobj, 
        target_U: np.ndarray | qt.Qobj,
        qubit_pair: Tuple[int, int] = (0, 1),
        num_qubits: int = 2,
    ):
        super().__init__(original_U, target_U)
        self.qA, self.qB = qubit_pair
        self.num_qubits = num_qubits
        
        effective_orig = self._extract_submatrix(self.original_U)
        effective_tgt = self._extract_submatrix(self.target_U)
        
        self.original_KAK = KAK2Q(effective_orig)
        self.target_KAK = KAK2Q(effective_tgt)
        
        # Compute the required local unitaries
        self._compute_local_unitaries()
        
    def _compute_local_unitaries(self):
        """
        Compute the required local unitaries by matching KAK decompositions.
        """
        # Extract individual qubit unitaries from KAK decompositions
        orig_L1 = self.original_KAK.L1
        orig_L2 = self.original_KAK.L2
        orig_R1 = self.original_KAK.R1
        orig_R2 = self.original_KAK.R2
        
        tgt_L1 = self.target_KAK.L1
        tgt_L2 = self.target_KAK.L2
        tgt_R1 = self.target_KAK.R1
        tgt_R2 = self.target_KAK.R2
        
        # Handle qutip vs numpy arrays
        if isinstance(orig_L1, qt.Qobj):
            orig_L1, orig_L2 = orig_L1.full(), orig_L2.full()
            orig_R1, orig_R2 = orig_R1.full(), orig_R2.full()
        if isinstance(tgt_L1, qt.Qobj):
            tgt_L1, tgt_L2 = tgt_L1.full(), tgt_L2.full()
            tgt_R1, tgt_R2 = tgt_R1.full(), tgt_R2.full()
        
        # Simple approach: just use the individual qubit transformations
        # and forget about the global phase factors.
        self.L1 = tgt_L1 @ orig_L1.conj().T
        self.L2 = tgt_L2 @ orig_L2.conj().T
        self.R1 = orig_R1.conj().T @ tgt_R1
        self.R2 = orig_R2.conj().T @ tgt_R2
        
    def _extract_submatrix(self, U):
        """
        Extracts the 4x4 submatrix corresponding to the qubit pair,
        with other qubits in ground state.
        """
        U = U.full() if isinstance(U, qt.Qobj) else U
        qA, qB = self.qA, self.qB
        
        basis = {}
        for ba in [0, 1]:
            for bb in [0, 1]:
                index = ba * (1 << qA) + bb * (1 << qB)
                basis[(ba, bb)] = index
        
        ordered_indices = [
            basis[(0, 0)], basis[(0, 1)],
            basis[(1, 0)], basis[(1, 1)]
        ]
        sub_U = U[ordered_indices, :][:, ordered_indices]
        
        # check if the submatrix is unitary
        assert np.allclose(sub_U @ sub_U.T.conj(), np.identity(4)), "Submatrix is not unitary, currently not supported."
        
        return sub_U
    
    def _embed_single_qubit(self, U2x2, which_qubit):
        """
        Embeds a 2x2 single-qubit unitary into the full multi-qubit space.
        """
        from functools import reduce
        I = np.eye(2, dtype=complex)
        mats = [I] * self.num_qubits
        mats[which_qubit] = U2x2
        return reduce(np.kron, mats)

    @property
    def synth_fidelity(self):
        """
        Compute the synthesis fidelity by comparing canonical gates.
        
        Returns
        -------
        float
            The process fidelity between original and target canonical gates.
        """
        d = 4
        canonical_gate_1 = self.original_KAK.canonical_gate()
        canonical_gate_2 = self.target_KAK.canonical_gate()
        return np.abs(np.trace(
            canonical_gate_1 @ canonical_gate_2.T.conj()
        )) ** 2 / d ** 2
    
    @property
    def synth_U(self):
        """
        The synthesized multi-qubit gate using the computed local unitaries.
        
        Returns
        -------
        np.ndarray
            The synthesized unitary: L_full @ original_U @ R_full
        """
        L1_emb = self._embed_single_qubit(self.L1, self.qA)
        L2_emb = self._embed_single_qubit(self.L2, self.qB)
        R1_emb = self._embed_single_qubit(self.R1, self.qA)
        R2_emb = self._embed_single_qubit(self.R2, self.qB)
        
        L_full = np.dot(L1_emb, L2_emb)
        R_full = np.dot(R2_emb, R1_emb)
        
        orig_U = self.original_U.full() if isinstance(self.original_U, qt.Qobj) else self.original_U
        
        return np.dot(L_full, np.dot(orig_U, R_full))
    
    @property
    def actual_synth_fidelity(self):
        """
        Compute the actual synthesis fidelity between synth_U and target_U
        in the full space.
        
        Returns
        -------
        float
            The process fidelity between synthesized and target unitaries.
        """
        synth_U = self.synth_U
        tgt_U = self.target_U.full() if isinstance(self.target_U, qt.Qobj) else self.target_U
        d = synth_U.shape[0]
        return np.abs(np.trace(synth_U @ tgt_U.T.conj())) ** 2 / d ** 2