__all__ = [
    "flat_spectral_density",
    "inv_spectral_density",
    "ohmic_spectral_density",
    "q_cap_fun",
    "cap_spectral_density",
    "q_ind_fun",
    "ind_spectral_density",
    "delta_spectral_density",
    "MEConstructor",
]

import warnings
import numpy as np
import qutip as qt
import scipy as sp
import scqubits as scq
from scqubits.core.qubit_base import QuantumSystem
from scqubits.core.noise import NOISE_PARAMS
import networkx as nx

from typing import List, Tuple, Any, Dict, Callable

# When considering dephasing, we only consider the zero-frequency transition
# because the noise spectral density is 1/f.
TPHI_HI_FREQ_CUTOFF = 1e-8

# When considering depolarization, we limit the lowest frequency, or the 
# thermal factor blows up. Unit: GHz
T1_LO_FREQ_CUTOFF = 1e-2

# When encountering rate small than this threshold, we directly ignore the
# jump operator.
RATE_THRESHOLD = 1e-10  # unit (rad/ns)

# The jumps can be clustered together if the spectral density is flat,
# which can be quantified by a relative tolerance, compared to the spectral
# density themselves or the transition frequency difference.
SPEC_DENS_RTOL = 0.1    # unit: spetral density / transition frequency difference divided by mat_elem**2

# The jumps must be clustered together (can't perform secular approximation)
# if the transition frequency difference is comparable to the largest rate.
FREQ_DIFF_THRESHOLD = 10     # unit: decoherence rate

DEPHASING_PREFAC = (
    np.sqrt(2 * np.abs(np.log(NOISE_PARAMS["omega_low"] * NOISE_PARAMS["t_exp"]))) 
    * 2 * np.pi
)

# Utils ======================================================================
def transition_to_str(
    transition: Tuple | None
) -> str:
    if transition is None:
        return "None"
    init, final = transition
    return "->".join([str(init), str(final)])

def transitions_to_str(
    transitions: List[Tuple]
) -> str:
    return ", ".join([transition_to_str(transition) for transition in transitions])

# Thermal factor ==============================================================
try: 
    from chencrafts.cqed.decoherence import thermal_ratio, thermal_factor
except ImportError:
    from scipy.constants import h, k
    def thermal_ratio(
        freq: float | np.ndarray, 
        temp: float | np.ndarray,
    ) -> float | np.ndarray:
        """
        Return the thermal ratio hbar * omega / k_B T.
        
        Parameters
        ----------
        freq: float | np.ndarray
            The frequency of the interested transition, in GHz
        temp: float | np.ndarray
            The temperature of the environment, in Kelvin

        Returns
        -------
        float | np.ndarray
            Thermal ratio
        """
        return (h * freq * 1e9) / (k * temp)

    def thermal_factor(omega, T):
        """
        Return the Boltzmann thermal factor in considering a decoherence rate.
        Equals to (n_th(freq, temp) + 1) when freq is positive or 
        n_th(abs(freq), temp) = - (n_th(freq, temp) + 1) when freq is negative.
        
        Parameters
        ----------
        omega: float | np.ndarray
            The frequency of the interested transition, in GHz
        T: float | np.ndarray
            The temperature of the environment, in Kelvin

        Returns
        -------
        float | np.ndarray
            Thermal factor
        """
        therm_ratio = thermal_ratio(omega, T)
        return (
            1 / np.tanh(0.5 * np.abs(therm_ratio))
            / (1 + np.exp(-therm_ratio))
        )

# Pre-defined spectral density ================================================  
def flat_spectral_density(omega, T, coeff):
    
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    # TODO: add a high frequency cutoff ? e^{-abs(omega) / omega_c} multiplied to the omega
    
    return coeff * thermal_factor(omega, T)

def inv_spectral_density(omega, T, peak_value, low_freq_cutoff = None):
    if low_freq_cutoff is None:
        low_freq_cutoff = T1_LO_FREQ_CUTOFF
    
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < low_freq_cutoff, low_freq_cutoff, omega)
    
    # TODO: add a high frequency cutoff ? e^{-abs(omega) / omega_c} multiplied to the omega
    
    if np.abs(omega) < low_freq_cutoff:
        coeff = peak_value
    else:
        coeff = peak_value * low_freq_cutoff / np.abs(omega)
    
    return coeff * thermal_factor(omega, T)

def ohmic_spectral_density(omega, T, Q = 10e6):
    """
    Return the ohmic spectral density that is linearly dependent on frequency.
    
    Parameters
    ----------
    omega: float | np.ndarray
        The frequency of the noise, GHz.
    T: float | np.ndarray
        The temperature of the noise, K.
    Q: float | np.ndarray
        The quality factor.

    Returns
    -------
    float | np.ndarray
        The ohmic spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    # TODO: add a high frequency cutoff ? e^{-abs(omega) / omega_c} multiplied to the omega
    
    therm_factor = thermal_factor(omega, T)
    return np.pi * 2 * np.abs(omega) / Q * therm_factor

def q_cap_fun(omega, T, Q_cap = 1e6):
    """
    See Smith et al (2020). Return the capacitive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    Q_cap: float
        The quality factor of the capacitor.

    Returns
    -------
    float
        The capacitive noise's spectral density.
    """
    return (
        Q_cap
        * (6 / np.abs(omega)) ** 0.7
    )

def cap_spectral_density(omega, T, EC, Q_cap = 1e6):
    """
    Return the capacitive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    EC: float
        The charging energy of the qubit.
    Q_cap: float
        The quality factor of the capacitor.

    Returns
    -------
    float
        The capacitive noise's spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    therm_factor = thermal_factor(omega, T)
    s = (
        2
        * 8
        * EC
        / q_cap_fun(omega, T, Q_cap)
        * therm_factor
    )
    s *= (
        2 * np.pi
    )  # We assume that system energies are given in units of frequency
    return s

def q_ind_fun(omega, T, Q_ind = 500e6):
    """
    Return the inductor's quality factor.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    Q_ind: float
        The quality factor of the inductor.

    Returns
    -------
    float
        The inductor's quality factor.
    """
    therm_ratio = abs(thermal_ratio(omega, T))
    therm_ratio_500MHz = thermal_ratio(0.5, T)
    return (
        Q_ind
        * (
            sp.special.kv(0, 1 / 2 * therm_ratio_500MHz)
            * np.sinh(1 / 2 * therm_ratio_500MHz)
        )
        / (
            sp.special.kv(0, 1 / 2 * therm_ratio)
            * np.sinh(1 / 2 * therm_ratio)
        )
    )

def ind_spectral_density(omega, T, EL, Q_ind = 500e6):
    """
    Return the inductive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    EL: float
        The inductive energy of the qubit, GHz.
    Q_ind: float
        The quality factor of the inductor.

    Returns
    -------
    float
        The inductive noise's spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    therm_factor = thermal_factor(omega, T)
    s = (
        2
        * EL
        / q_ind_fun(omega, T, Q_ind)
        * therm_factor
    )
    s *= (
        2 * np.pi
    )  # We assume that system energies are given in units of frequency
    return s

def delta_spectral_density(omega, peak_value, peak_loc = 0, peak_width = 1e-10):
    """
    Obtain a delta function spectral density. 
    
    It's used to model the dephasing noise, which typically have a 1/f spectrum. 
    Although it is known that dynamics under a 1/f noise is non-Markovian,
    which can't be modeled properly in the Lindblad master equation framework.
    Nevertheless, we have to include it with a delta spectrum density or the 
    dephasing is completely missing in the dynamics. 
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    peak_value: float
        The value of the delta function.
    peak_loc: float
        The location of the delta function.
    peak_width: float
        The width of the delta function, for numrical purposes.

    Returns
    -------
    float
        The delta function spectral density.
    """    
    # add a cutoff to avoid zero divisio
    if np.allclose(omega, peak_loc, atol=peak_width):
        return peak_value
    else:
        return 0

# Rate calculation based on Golden rule =======================================
class Jump:
    def __init__(
        self, 
        channel: str,
        transition: Tuple[int, int],
        freq: float,
        spec_dens: float,
        mat_elem: complex,
        op: qt.Qobj,
        bare_transition: 
            Tuple[Tuple[int, ...], Tuple[int, ...]] | None = None,
    ):
        """
        A jump operator in the Lindblad master equation, jumping 
        from one (subsystem or composite system) eigenstate to another, 
        labeled by the name of the decoherence channel, transition frequency, etc. 
        
        This class facilitates the (re-)clustering of jumps from the Lindblad-Davies
        master equation, where the full secular approximation is performed. 
        
        Parameters
        ----------
        channel: str
            The name of the decoherence channel.
        transition: Tuple[int, int]
            The initial and final state eigenstate indices.
        freq: float
            The transition frequency of this jump. 
        spec_dens: float
            The bath spectral density at the transition frequency.
        op: qt.Qobj
            The system-bath coupling operator associated with this transition
            frequency. The spectral density is not included in this operator.
        bare_transition: [
            Tuple[Tuple[int, ...], Tuple[int, ...]] | None
        ] = None,
            Optioinal, the bare indices of the initial and final states.
        """
        self.channel = channel
        self.transition = transition
        self.freq = freq
        self.spec_dens = spec_dens
        self.op = op
        self.bare_transition = bare_transition
        
        # pre-calculate to save the runtime
        self._mat_elem = np.abs(mat_elem)
        self._rate = self._mat_elem ** 2 * self.spec_dens
        
    @property
    def mat_elem(self) -> float:
        return self._mat_elem
        
    @property
    def rate(self) -> float:
        return self._rate

    def can_cluster_with(self, other: 'Jump') -> bool:
        """
        Check if two jumps CAN or MUST be clustered together.
        
        Equivalently, we are checking if we CAN or MUST NOT do secular 
        approximation on two transitions from the Bloch-Redfield equation.
        
        Note: valid at least for the short time limit. Not sure what should we 
        compare the freq-difference to in the long time limit.
        For long time limit, simulate BR equation.
        """
        # Never cluster transition induced by different baths
        if self.channel != other.channel:
            return False
        
        # If the spec_dens are close to each other, in any cases we don't need 
        # to do secular approximation---we can always cluster the jumps
        freq_diff = np.abs(self.freq - other.freq)
        avg_mat_elem = np.sqrt(self.mat_elem * other.mat_elem)
        
        is_spec_dens_close = (
            np.abs(self.spec_dens - other.spec_dens) 
            <= SPEC_DENS_RTOL * np.abs(other.spec_dens)
        )
        
        is_rate_close = (
            np.abs(
                self.spec_dens * avg_mat_elem - other.spec_dens * avg_mat_elem
            ) <= SPEC_DENS_RTOL * freq_diff
        )

        if is_spec_dens_close and is_rate_close:
            return True
        else:
            largest_rate = np.sqrt(self.rate * other.rate)
            if freq_diff < FREQ_DIFF_THRESHOLD * largest_rate:
                warnings.warn(
                    f"Two jumps ({self}, {other}) have different spectral density, but similar "
                    "transition frequency, indicating no approximation can be "
                    "made that leads to a Lindblad master equation. We uncluster "
                    "them for the moment. Consider simulating BR equation instead."
                )
            return False
    
    def must_cluster_with(self, other: 'Jump | ClusteredJump') -> bool:
        """
        Check if two jumps must be (re-)clustered together.
        """
        if isinstance(other, ClusteredJump):
            return other.must_cluster_with(self)
        
        if not self.can_cluster_with(other):
            # non-flat spectral density
            return False
        
        freq_diff = np.abs(self.freq - other.freq)
        largest_rate = np.sqrt(self.rate * other.rate)
        if freq_diff <= FREQ_DIFF_THRESHOLD * largest_rate:
            # If two transitions are close in frequency, secular approximation
            # can't be performed.
            return True
        else:
            # Secular approximation can be performed, leaving the jump unclustered.
            return False
        
    def __add__(self, other: 'Jump | ClusteredJump') -> 'ClusteredJump':
        """
        Add two jumps together.
        """
        # Realized based on the __add__ of ClusteredJump.
        if isinstance(other, Jump):
            clustered_jump = ClusteredJump([self])
            return clustered_jump + other
        else:
            return other + self
        
    def forced_cluster(self, other: 'Jump | ClusteredJump') -> 'ClusteredJump':
        """
        Force the clustering of two jumps / clusters.
        """
        if isinstance(other, Jump):
            return ClusteredJump([self, other])
        else:
            return other.force_cluster(self)
    
    def __str__(self):
        if self.bare_transition is not None:
            bare_transition_str = f"""
    bare_transition={transition_to_str(self.bare_transition)},"""
        else:
            bare_transition_str = ""
        
        return f"""Jump(
    channel={self.channel}, 
    transition={transition_to_str(self.transition)},{bare_transition_str}
    Transition frequency: {self.freq:.1e} GHz
    Rate: {self.rate:.1e} rad/ns
)
"""
    
    def __repr__(self):
        return self.__str__()
    
    def op_LME(self) -> qt.Qobj:
        """
        Return the jump operator in the Lindblad Master Equation.
        """
        return self.op * np.sqrt(self.spec_dens)
    

class ClusteredJump:
    def __init__(self, jumps: 'List[Jump]'):
        self.jumps = jumps
        
    def __add__(self, other: 'ClusteredJump | Jump') -> 'ClusteredJump':
        """
        (Re-)cluster the jumps. The clustering is allowed if at least one of the
        jumps from two clusters "must" be clustered together.
        """
        if not self.must_cluster_with(other):
            raise ValueError(
                "Normally, we follow the partial secular approximation and "
                "cluster jumps only when it's necessary. For a forced clustering, "
                "please use the `force_cluster` method."
            )
        return self.force_cluster(other)
            
    def force_cluster(self, other: 'ClusteredJump | Jump') -> 'ClusteredJump':
        """
        Force the clustering a jump / a cluster into this cluster.
        """
        if isinstance(other, Jump):
            return ClusteredJump(self.jumps + [other])
        else:
            return ClusteredJump(self.jumps + other.jumps)
        
    def sort(self, attr: str = "transition"):
        """
        Sort the jumps by their labels.
        """
        self.jumps.sort(key=lambda jump: getattr(jump, attr))
        
    def must_cluster_with(self, other: 'ClusteredJump | Jump') -> bool:
        """
        Check if any one of the jumps in two clusters must be clustered together.
        """
        if isinstance(other, Jump):
            return any(jump.must_cluster_with(other) for jump in self.jumps)
        else:
            return any(self.must_cluster_with(other_jump) for other_jump in other.jumps)
        
    def can_cluster_with(self, other: 'ClusteredJump | Jump') -> bool:
        """
        Check if all jumps in two clusters can be clustered together.
        """
        if isinstance(other, Jump):
            return all(jump.can_cluster_with(other) for jump in self.jumps)
        else:
            return all(self.can_cluster_with(other_jump) for other_jump in other.jumps)
        
    def is_valid(self) -> bool:
        """
        Check if all clustered jumps can be clustered with each other.
        """
        return self.can_cluster_with(self)
        
    @property
    def transitions(self) -> List[Tuple[int, int]]:
        return [jump.transition for jump in self.jumps]
    
    @property
    def bare_transitions(self) -> List[Tuple[Tuple[int, ...], Tuple[int, ...]] | None]:
        return [jump.bare_transition for jump in self.jumps]
    
    @property
    def channel(self) -> str:
        return self.jumps[0].channel
    
    @property
    def median_freq(self) -> float:
        return np.median([jump.freq for jump in self.jumps])
    
    @property
    def median_spec_dens(self) -> float:
        return np.median([jump.spec_dens for jump in self.jumps])
    
    @property
    def max_mat_elem(self) -> float:
        return np.max([jump.mat_elem for jump in self.jumps])
    
    @property
    def minimum_rate(self) -> float:
        return np.min([jump.rate for jump in self.jumps])
    
    def __repr__(self):
        bare_transitions = self.bare_transitions
        if any([trans is not None for trans in bare_transitions]):
            bare_transition_str = f"""
    bare_transition={transitions_to_str(bare_transitions)},"""
        else:
            bare_transition_str = ""

        return f"""ClusteredJump(
    channel={self.channel},
    transition={transitions_to_str(self.transitions)},{bare_transition_str}
    median_freq={self.median_freq:.1e} GHz
    minimum_rate={self.minimum_rate:.1e} rad/ns
)
"""

    def __str__(self):
        return self.__repr__()
    
    def op_LME(self, lindbladian: bool = False) -> qt.Qobj:
        if len(self.jumps) == 0:
            raise ValueError("No jumps in the cluster.")
        
        sum_ops = sum([jump.op_LME() for jump in self.jumps])
        if lindbladian:
            return qt.lindblad_dissipator(sum_ops)
        else:
            return sum_ops

    
class MEConstructor:
    """
    Construct a clustered master equation.
    
    Core functionality of this constructor is to construct the jump operators
    based on the system-bath coupling operator and the bath spectral density.
    
    We construct jump operators for one system-bath coupling at a time, which    
    - Take in: 
        - A system-bath coupling operator
        - Bath spectral density
    - Obtain intermediate results (for each pair of eigenstates): 
        - Transition frequency
        - Transition rate
        - Spectral density
        - Projector
    - Stores: 
        - Clustered projectors
    """
    
    def __init__(
        self, 
        hilbertspace: scq.HilbertSpace,   # type: ignore
        truncated_dim: int | None = None,
        regenerate_lookup: bool = True,
    ):
        self.hilbertspace = hilbertspace
        if truncated_dim is not None:
            self.truncated_dim = truncated_dim
        else:
            self.truncated_dim = hilbertspace.dimension
            
        if regenerate_lookup:
            hilbertspace.generate_lookup(ordering="LX")
        self.evals = hilbertspace["evals"][0]   # type: ignore
        self.evecs = hilbertspace["evecs"][0]   # type: ignore
        self.dressed_indices = hilbertspace["dressed_indices"][0]   # type: ignore
        self.bare_evals = [
            subsys_evals[0]
            for subsys_evals in hilbertspace["bare_evals"]  # type: ignore
        ]   
        self.bare_evecs = [
            subsys_evecs[0]
            for subsys_evecs in hilbertspace["bare_evecs"]  # type: ignore
        ]
            
        self.unclustered_jumps: Dict[str, np.ndarray[Jump, Any]] = {}
        self.clustered_jumps: Dict[str, List[ClusteredJump]] = {}
        
    def _bare_indices(
        self,
        dressed_idx: int,
    ) -> Tuple[int, ...] | None:
        """
        Convert the dressed index to the bare index.
        """
        try:
            idx_bare_ravel = np.where(
                self.dressed_indices == dressed_idx
            )[0][0]
            idx_bare = np.unravel_index(
                idx_bare_ravel,
                self.hilbertspace.subsystem_dims,
            )
        except IndexError:
            idx_bare = None
        return idx_bare
    
    def hamiltonian(self) -> qt.Qobj:
        """
        Return the Hamiltonian of the system in eigenbasis, the unit of rad / ns.
        """
        hamiltonian = qt.qdiags(self.evals[:self.truncated_dim]) * np.pi * 2
        return hamiltonian
    
    def add_local_channel(
        self,
        channel: str,
        subsys_op: qt.Qobj | np.ndarray,
        subsys: QuantumSystem,
        spec_dens_fun: Callable,
        spec_dens_kwargs: Dict[str, Any] = {},
        depolarization_only: bool = True,
    ):
        """
        Add a local dissipative channel to the MEConstructor, both unclustered and
        clustered. This yields a local Lindblad master equation.
        
        Parameters
        ----------
        channel: str
            The channel of the jump operator.
        subsys_op: qt.Qobj | np.ndarray
            The subsystem operator coupled to the bath, in the subsytem eigenbasis.
        subsys: QuantumSystem
            The subsystem that the local channel is acting on.
        spec_dens_fun: Callable
            The bath spectral density as a function of frequency, should have 
            the signature `spec_dens_fun(omega, **spec_dens_kwargs)`.
        spec_dens_kwargs: Dict[str, Any]
            The keyword arguments provided to the bath spectral density function.
        depolarization_only: bool
            Whether to only consider the depolarization channel (i.e., ignoring
            all self-transitions).
        """
        # get the transition frequency and spectral density for each pair of 
        # eigenstates
        subsys_idx = self.hilbertspace.subsystem_list.index(subsys)
        bare_evals = self.bare_evals[subsys_idx]
        subsys_dim = self.hilbertspace.subsystem_dims[subsys_idx]
        
        jumps = np.empty((subsys_dim, subsys_dim), dtype=object)
        for idx_init in range(subsys_dim):
            for idx_final in range(subsys_dim):
                if idx_init == idx_final and depolarization_only:
                    continue
                
                # compute the transition rate
                freq = bare_evals[idx_init] - bare_evals[idx_final] # negative for upward transition
                spec_dens = spec_dens_fun(freq, **spec_dens_kwargs)
                mat_elem = subsys_op[idx_final, idx_init]
                
                rate = np.abs(mat_elem) ** 2 * spec_dens
                if rate < RATE_THRESHOLD:
                    continue
                
                # construct the jump operator
                jump_op = qt.projection(
                    dimensions = subsys_dim,
                    n = idx_final,
                    m = idx_init,
                ) * mat_elem
                jump_op_dressed = self.hilbertspace.op_in_dressed_eigenbasis(
                    op_callable_or_tuple = (jump_op.full(), subsys),
                    truncated_dim = self.truncated_dim,
                    op_in_bare_eigenbasis = True,
                )
                
                # record the jump
                jumps[idx_init, idx_final] = (
                    Jump(
                        channel = channel,
                        transition = (idx_init, idx_final),
                        freq = freq,
                        spec_dens = spec_dens,
                        mat_elem = mat_elem,
                        op = jump_op_dressed,
                        bare_transition = None,
                    )
                )
                
        self.unclustered_jumps[channel] = jumps
        
        jumps_flatten = [jump for jump in jumps.flatten() if jump is not None]
        clustered_jumps = self._cluster_jumps(jumps_flatten)
        self.clustered_jumps[channel] = clustered_jumps
                
    def add_channel(
        self,
        channel: str,
        op: qt.Qobj,
        spec_dens_fun: Callable,
        spec_dens_kwargs: Dict[str, Any] = {},
        depolarization_only: bool = True,
        record_bare_transition: bool = True,
    ):
        """
        Construct the jump operators for a given channel, both unclustered
        (yielding a global Lindblad master equation) and clustered (yielding
        a master equation with partial secular approximation).
        
        Parameters
        ----------
        channel: str
            The channel of the jump operator.
        op: qt.Qobj
            The system-bath coupling operator in the eigenbasis, typically
            obtained by `HilbertSpace.op_in_dressed_eigenbasis()`.
        spec_dens_fun: Callable
            The bath spectral density as a function of frequency, should have 
            the signature `spec_dens_fun(omega, **spec_dens_kwargs)`.
        spec_dens_kwargs: Dict[str, Any]
            The keyword arguments provided to the bath spectral density function.
        depolarization_only: bool
            Whether to only consider the depolarization channel (i.e., ignoring
            all self-transitions).
        """
        # get the transition frequency and spectral density for each pair of 
        # eigenstates
        jumps = np.empty((self.truncated_dim, self.truncated_dim), dtype=object)
        for idx_init in range(self.truncated_dim):
            for idx_final in range(self.truncated_dim):
                if idx_init == idx_final and depolarization_only:
                    continue
                
                # compute the transition rate
                freq = self.evals[idx_init] - self.evals[idx_final] # negative for upward transition
                spec_dens = spec_dens_fun(freq, **spec_dens_kwargs)
                mat_elem = op[idx_final, idx_init]
                
                rate = np.abs(mat_elem) ** 2 * spec_dens
                if rate < RATE_THRESHOLD:
                    continue
                
                # record the bare transition indices if requested
                if record_bare_transition:
                    bare_transition = (
                        self._bare_indices(idx_init),
                        self._bare_indices(idx_final),
                    )
                else:
                    bare_transition = None
                
                # construct the jump operator
                jump_op = qt.projection(
                    dimensions = self.truncated_dim,
                    n = idx_final,
                    m = idx_init,
                ) * mat_elem
                
                # record the jump
                jumps[idx_init, idx_final] = (
                    Jump(
                        channel = channel,
                        transition = (idx_init, idx_final),
                        freq = freq,
                        spec_dens = spec_dens,
                        mat_elem = mat_elem,
                        op = jump_op,
                        bare_transition = bare_transition,
                    )
                )
                
        self.unclustered_jumps[channel] = jumps
        
        jumps_flatten = [jump for jump in jumps.flatten() if jump is not None]
        clustered_jumps = self._cluster_jumps(jumps_flatten)
        self.clustered_jumps[channel] = clustered_jumps

    def _cluster_jumps(self, jumps: List[Jump]) -> List[ClusteredJump]:
        """
        Perform the (re-)clustering of the jump operators when necessary.
        In other words, the result is a Lindblad master equation with the 
        secular approximation performed whenever applicable.
        
        Parameters
        ----------
        jumps: List[Jump]
            The jump operators to be clustered in a 1D array.

        Returns
        -------
        List[ClusteredJump]
            The clustered jump operators.
        """
        # check whether two jumps can be clustered together
        compatibility_matrix = np.zeros((len(jumps), len(jumps)))
        for idx_1, jump_1 in enumerate(jumps):
            for idx_2, jump_2 in enumerate(jumps):
                if idx_1 == idx_2:
                    continue
                elif idx_1 > idx_2:
                    compatibility_matrix[idx_1, idx_2] = jump_1.must_cluster_with(jump_2)
                else:
                    compatibility_matrix[idx_1, idx_2] = compatibility_matrix[idx_2, idx_1]
                    
        # think of this as a graph, and cluster the jumps that are 
        # associated with the same connected component
        G = nx.Graph(compatibility_matrix)
        connected_components = list(nx.connected_components(G))
        
        # cluster the jumps
        clustered_jumps = []
        for idx_cluster, connected_component in enumerate(connected_components):
            if len(connected_component) == 1:
                jump_idx = connected_component.pop()    # this is a set
                jump = jumps[jump_idx]
                clustered_jumps.append(ClusteredJump([jump]))
            else:
                clustered_jump = ClusteredJump([jumps[jump_idx] for jump_idx in connected_component])
                clustered_jump.sort()
                clustered_jumps.append(clustered_jump)
                if not clustered_jump.is_valid():
                    warnings.warn(
                        f"Within the cluster #{idx_cluster} of channel {jumps[0].channel}, "
                        f"some jumps can't be clustered with each other while others must "
                        f"be clustered, causing conflicts. Consider "
                        f"simulating the Bloch-Redfield equation instead."
                    )

        clustered_jumps.sort(
            key=lambda clustered_jump: clustered_jump.minimum_rate,
            reverse=True,
        )
        return clustered_jumps
            
    def all_clustered_jump_ops(
        self,
        lindbladian: bool = False,
    ) -> List[qt.Qobj]:
        """
        Return all the constructed jump operators.
        """
        ops = []
        for _, jumps in self.clustered_jumps.items():
            for jump in jumps:
                try: 
                    op = jump.op_LME(lindbladian=lindbladian)
                except ValueError:
                    # No jumps in the cluster
                    continue
                ops.append(op)
        return ops
    
    def all_unclustered_jump_ops(
        self,
        lindbladian: bool = False,
    ) -> List[qt.Qobj]:
        """
        Return all the constructed jump operators.
        """
        ops = []
        for _, jumps in self.unclustered_jumps.items():
            for jump in jumps.flatten():
                if jump is None:
                    continue
                if lindbladian:
                    ops.append(qt.lindblad_dissipator(jump.op_LME()))
                else:
                    ops.append(jump.op_LME())
        return ops
    
    def all_ULE_jump_ops(
        self,
        lindbladian: bool = False,
    ) -> List[qt.Qobj]:
        """
        Return all the jump operators for the Universal Lindblad Equation (ULE)
        in PHYS. REV. B 102, 115109 (2020). Basically, it clusters all jumps that
        are associated with the noise channel.
        """
        ops = []
        for _, jumps in self.unclustered_jumps.items():
            # Cluster every jump corresponding to the same noise channel
            clustered_jump = ClusteredJump([
                jump for jump in jumps.flatten() if jump is not None
            ])
            try: 
                op = clustered_jump.op_LME(lindbladian=lindbladian)
            except ValueError:
                # No jumps in the cluster
                continue
            ops.append(op)
        return ops