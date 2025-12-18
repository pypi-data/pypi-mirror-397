_all__ = [
    "KAK_2q",
    "to_weyl_chamber",
    "canonical_gate",
]
import numpy as np
from scipy.linalg import expm
from typing import Tuple
import qutip as qt

I = np.identity(2)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])

def _to_su(u: np.ndarray) -> np.ndarray:
    """
    Given a unitary in U(N), return the
    unitary in SU(N).
    Args:
        u (np.ndarray): The unitary in U(N).
    Returns:
        np.ndarray: The unitary in SU(N)
    """

    return u * complex(np.linalg.det(u)) ** (-1 / np.shape(u)[0])

def _decompose_one_qubit_product(
    U: np.ndarray
):
    """
    Decompose a 4x4 unitary matrix to two 2x2 unitary matrices.
    Args:
        U (np.ndarray): input 4x4 unitary matrix to decompose.
        validate_input (bool): if check input.
    Returns:
        phase (float): global phase.
        U1 (np.ndarray): decomposed unitary matrix U1.
        U2 (np.ndarray): decomposed unitary matrix U2.
    """

    i, j = np.unravel_index(np.argmax(U, axis=None), U.shape)

    def u1_set(i):
        return (1, 3) if i % 2 else (0, 2)

    def u2_set(i):
        return (0, 1) if i < 2 else (2, 3)

    u1 = U[np.ix_(u1_set(i), u1_set(j))]
    u2 = U[np.ix_(u2_set(i), u2_set(j))]

    u1 = _to_su(u1)
    u2 = _to_su(u2)

    phase = U[i, j] / (u1[i // 2, j // 2] * u2[i % 2, j % 2])

    return phase, u1, u2

def to_weyl_chamber(c0: float, c1: float, c2: float) -> np.ndarray:
    """Bring coordinates vector into the Weyl chamber"""
    
    c = np.array([c0, c1, c2])

    # Step 0: work in terms of multiple of pi
    c /= np.pi

    # Step 1: Bring everything into [0, 1)
    c -= np.floor(c)

    # Step 2: Sort c1 >= c2 >= c3
    c = np.sort(c)[::-1]

    # Step 3: if c1 + c2 >= 1, transform (c1, c2, c3) -> (1-c2, 1-c1, c3)
    if c[0]+c[1] >=1:
        c = np.sort(np.array([1-c[1], 1-c[0], c[2]]))[::-1]

    # Step 4: if c3 = 0 and c1>1/2, transform (c1, c2, 0) -> (1-c1, c2, 0)
    if (c[0] > 1/2) and np.isclose(c[2], 0):
        c = np.array([1-c[0], c[1], 0])

    # Step 5: Turn it back into radians
    c *= np.pi
    
    return c

def canonical_gate(
    c0: float, 
    c1: float, 
    c2: float, 
    to_qobj: bool = False
) -> np.ndarray | qt.Qobj:
    """
    Returns the canonical gate for the given parameters.
    Args:
        c0 (float): XX canonical parameter
        c1 (float): YY canonical parameter
        c2 (float): ZZ canonical parameter
    Returns:
        np.ndarray: The canonical gate
    """
    gate = expm(1j/2 * (
        c0 * np.kron(X, X) 
        + c1 * np.kron(Y, Y) 
        + c2 * np.kron(Z, Z)
    ))

    if to_qobj:
        return qt.Qobj(gate, dims=[[2, 2], [2, 2]])
    else:
        return gate

def _Theta(U: np.ndarray) -> np.ndarray:
    """global Cartan involution of a unitary matrix"""
    return np.conj(U)

class KAK2Q:
    c0: float
    c1: float
    c2: float
    phase1: float
    L1: np.ndarray | qt.Qobj
    L2: np.ndarray | qt.Qobj
    phase2: float
    R1: np.ndarray | qt.Qobj
    R2: np.ndarray | qt.Qobj
    to_qobj: bool
    
    def canonical_gate(self) -> np.ndarray | qt.Qobj:
        """
        Returns:
            np.ndarray: The canonical gate
        """
        return canonical_gate(self.c0, self.c1, self.c2, self.to_qobj)
    
    def __init__(
        self,
        U: np.ndarray | qt.Qobj,
        rounding: int = 14,
    ):
        """
        Decomposes a 2-qubit unitary matrix into the product of three matrices:
        KAK = L @ CAN(theta_vec) @ R where L and R are two-qubit local unitaries, 
        CAN is a 3-parameter canonical matrix, and theta_vec is a vector of 3 angles.

        Args:
            U (np.ndarray): 2-qubit unitary matrix
            rounding (int): Number of decimal places to round intermediate 
            matrices to (default 14)

        Attributes:
            self.phase1 (float): Global phase factor for left local unitary L
            self.L1 (np.ndarray | qt.Qobj): Top 2x2 matrix of left local unitary L
            self.L2 (np.ndarray | qt.Qobj): Bottom 2x2 matrix of left local unitary L
            self.phase2 (float): Global phase factor for right local unitary R
            self.R1 (np.ndarray | qt.Qobj): Top 2x2 matrix of right local unitary R
            self.R2 (np.ndarray | qt.Qobj): Bottom 2x2 matrix of right local unitary R
            self.c0 (float): XX canonical parameter in the Weyl chamber
            self.c1 (float): YY canonical parameter in the Weyl chamber
            self.c2 (float): ZZ canonical parameter in the Weyl chamber
        """
        self.U = U
        self.rounding = rounding
        self.to_qobj = isinstance(U, qt.Qobj)
        self._run()
    
    def _run(self):
        U = self.U.full() if self.to_qobj else self.U

        # 0. Map U(4) to SU(4) (and phase)
        global_phase = np.linalg.det(U)**0.25
        U /= global_phase

        assert np.isclose(np.linalg.det(U), 1), "Determinant of U is not 1"

        # 1. Unconjugate U into the magic basis
        B = 1 / np.sqrt(2) * np.array([[1, 0, 0, 1j], [0, 1j, 1, 0],
                                    [0, 1j, -1, 0], [1, 0, 0, -1j]]) # Magic Basis
        U_prime = np.conj(B).T @ U @ B

        # Isolating the maximal torus
        M_squared = _Theta(np.conj(U_prime).T) @ U_prime

        if self.rounding is not None:
            M_squared = np.round(M_squared, self.rounding)  # For numerical stability

        ## 2. Diagonalizing M^2
        D, P = np.linalg.eig(M_squared)

        ## Check and correct for det(P) = -1
        if np.isclose(np.linalg.det(P), -1):
            P[:, 0] *= -1  # Multiply the first eigenvector by -1

        # 3. Extracting K2
        K2 = np.conj(P).T

        assert np.allclose(K2 @ K2.T, np.identity(4)), "K2 is not orthogonal"
        assert np.isclose(np.linalg.det(K2), 1), "Determinant of K2 is not 1"

        # 4. Extracting A
        A = np.sqrt(D)

        ## Check and correct for det(A) = -1
        if np.isclose(np.prod(A), -1):
            A[0] *= -1  # Multiply the first eigenvalue by -1

        A = np.diag(A)  # Turn the list of eigenvalues into a diagonal matrix

        assert np.isclose(np.linalg.det(A), 1), "Determinant of A is not 1"

        # 5. Extracting K1
        K1 = U_prime @ np.conj(K2).T @ np.conj(A).T

        assert np.allclose(K1 @ K1.T, np.identity(4)), "K1 is not orthogonal"
        assert np.isclose(np.linalg.det(K1), 1), "Determinant of K1 is not 1"

        # 6. Extracting Local Gates
        L = B @ K1 @ np.conj(B).T  # Left Local Product
        R = B @ K2 @ np.conj(B).T  # Right Local Product

        phase1, L1, L2 = _decompose_one_qubit_product(L)  # L1 (top), L2(bottom)
        phase2, R1, R2 = _decompose_one_qubit_product(R)  # R1 (top), R2(bottom)

        # 7. Extracting the Canonical Parameters
        C = np.array([[1, 1, 1], [-1, 1, -1], [1, -1, -1]])  # Coefficient Matrix

        theta_vec = np.angle(np.diag(A))[:3]  # theta vector
        a0, a1, a2 = np.linalg.inv(C) @ theta_vec  # Computing the "a"-vector

        # 8. Unpack Parameters (raw parameters before Weyl chamber transformation)
        c0_raw, c1_raw, c2_raw = 2 * a1, -2 * a0, 2 * a2
        
        # Verify decomposition with raw parameters
        assert np.allclose(
            U, (
                phase1 * np.kron(L1, L2)) 
                @ canonical_gate(c0_raw, c1_raw, c2_raw)
                @ (phase2 * np.kron(R1, R2)
            )
        ), "U does not equal KAK"
        
        self._G = [np.kron(X, X), np.kron(Y, Y), np.kron(Z, Z)]

        left_local = phase1 * np.kron(L1, L2)
        right_local = phase2 * np.kron(R1, R2)
        c_vec = np.array([c0_raw, c1_raw, c2_raw])

        vec = c_vec / np.pi
        floors = np.floor(vec)
        vec -= floors
        total_delta = -floors * np.pi
        shift_op = 0j * np.eye(4)
        for k in range(3):
            shift_op += (1j / 2) * total_delta[k] * self._G[k]
        A = expm(shift_op)
        left_local = left_local @ A.conj().T

        vec = list(vec)

        if vec[0] < vec[1]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 0, 1)
        if vec[0] < vec[2]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 0, 2)
        if vec[1] < vec[2]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 1, 2)

        if vec[0] + vec[1] >= 1:
            left_local, right_local, vec = self._apply_reverse_and_resort(left_local, right_local, vec)

        if np.isclose(vec[2], 0) and vec[0] > 0.5:
            left_local, right_local, vec = self._apply_base_case(left_local, right_local, vec)

        c_vec = np.array(vec) * np.pi
        self.c0, self.c1, self.c2 = c_vec

        phase1, L1, L2 = _decompose_one_qubit_product(left_local)
        phase2, R1, R2 = _decompose_one_qubit_product(right_local)
        self.phase1 = phase1
        self.L1 = L1 if not self.to_qobj else qt.Qobj(L1)
        self.L2 = L2 if not self.to_qobj else qt.Qobj(L2)
        self.phase2 = phase2
        self.R1 = R1 if not self.to_qobj else qt.Qobj(R1)
        self.R2 = R2 if not self.to_qobj else qt.Qobj(R2)

        # Optional: add assertion to verify
        # assert np.allclose(
        #     U, (self.phase1 * np.kron(self.L1, self.L2)) 
        #     @ canonical_gate(self.c0, self.c1, self.c2)
        #     @ (self.phase2 * np.kron(self.R1, self.R2))
        # ), "Adjusted decomposition does not match U"

    @staticmethod
    def _get_swap_ab(a, b):
        """
        Returns the correction matrices A and B for swapping canonical parameters
        between indices a and b.

        Args:
            a (int): First index (0=XX, 1=YY, 2=ZZ)
            b (int): Second index

        Returns:
            Tuple[np.ndarray, np.ndarray]: Correction matrices A and B
        """
        if set([a, b]) == {0, 1}:
            theta = np.pi / 4
            Z_sum = np.kron(Z, I) + np.kron(I, Z)
            A = expm(-1j * theta * Z_sum)
            B = expm(1j * theta * Z_sum)
            return A, B
        elif set([a, b]) == {0, 2}:
            H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
            V = np.kron(H, H)
            return V, V
        elif set([a, b]) == {1, 2}:
            w = 1j
            W = np.array([[1, -w], [-w, 1]]) / np.sqrt(2)
            W_dag = np.array([[1, w], [w, 1]]) / np.sqrt(2)
            V = np.kron(W, W)
            B = np.kron(W_dag, W_dag)
            return V, B

    @staticmethod
    def _perform_swap(left_local, right_local, vec, i, j):
        """
        Performs a swap of canonical parameters at indices i and j, updating
        the local unitaries accordingly.

        Args:
            left_local (np.ndarray): Left local unitary product
            right_local (np.ndarray): Right local unitary product
            vec (list): Normalized canonical vector [c0/pi, c1/pi, c2/pi]
            i (int): First index to swap
            j (int): Second index to swap

        Returns:
            Tuple[np.ndarray, np.ndarray, list]: Updated left_local, right_local, vec
        """
        vec[i], vec[j] = vec[j], vec[i]
        A, B = KAK2Q._get_swap_ab(i, j)
        left_local = left_local @ A.conj().T
        right_local = B.conj().T @ right_local
        return left_local, right_local, vec

    def _apply_reverse_and_resort(self, left_local, right_local, vec):
        """
        Applies the reverse transformation if c0 + c1 >= 1 (in pi units),
        updates vec and locals, and re-sorts.

        Args:
            left_local (np.ndarray): Left local unitary product
            right_local (np.ndarray): Right local unitary product
            vec (list): Normalized canonical vector

        Returns:
            Tuple[np.ndarray, np.ndarray, list]: Updated left_local, right_local, vec
        """
        A_swap, B_swap = self._get_swap_ab(0, 1)
        A_rev = np.kron(Z, I)
        B_rev = A_rev
        G0 = self._G[0]
        G1 = self._G[1]
        A = (-1) * G0 @ G1 @ A_rev @ A_swap
        B = B_swap @ B_rev
        left_local = left_local @ A.conj().T
        right_local = B.conj().T @ right_local
        temp = [1 - vec[1], 1 - vec[0], vec[2]]
        vec = list(temp)
        if vec[0] < vec[1]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 0, 1)
        if vec[0] < vec[2]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 0, 2)
        if vec[1] < vec[2]:
            left_local, right_local, vec = self._perform_swap(left_local, right_local, vec, 1, 2)
        return left_local, right_local, vec

    def _apply_base_case(self, left_local, right_local, vec):
        """
        Applies the base case transformation if c2 ≈ 0 and c0 > 0.5 (in pi units).

        Args:
            left_local (np.ndarray): Left local unitary product
            right_local (np.ndarray): Right local unitary product
            vec (list): Normalized canonical vector

        Returns:
            Tuple[np.ndarray, np.ndarray, list]: Updated left_local, right_local, vec
        """
        V = np.kron(Z, X)
        shift = expm(1j / 2 * np.pi * self._G[0])
        A = shift @ V
        B = V
        left_local = left_local @ A.conj().T
        right_local = B.conj().T @ right_local
        vec = [1 - vec[0], vec[1], 0]
        return left_local, right_local, vec