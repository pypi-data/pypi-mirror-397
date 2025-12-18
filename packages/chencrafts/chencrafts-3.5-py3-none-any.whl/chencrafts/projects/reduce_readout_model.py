# This module is from Darren's notebook simplemodel.ipynb, sent via Slack on 12/11/2025.

__all__ = [
    "simplemodel",
]

import qutip as qt
import numpy as np
import matplotlib.pyplot as plt
import scqubits as scq
π = np.pi
import pandas as pd
from chencrafts.cqed.clustered_me import *

class simplemodel: #ADJUST THIS
    def __init__(self, EJ=12.1, EC=1.78, EL=0.81, g=0.15, 
                 E_osc=6.42586, L_osc=1, flux=-0.451322, 
                 fdim=15, rdim=6, total_truncation=50, driveamp=2.5e-4, 
                 qubit_temp=0.02, resonator_temp=0.06, Qcap=24000, Qohmic=5.35e4,
                 atol=1e-8, rtol=1e-8, n_it=100):

        self.EJ = EJ
        self.EC = EC
        self.EL = EL
        self.g = g
        self.E_osc = E_osc
        self.L_osc = L_osc
        self.flux = flux

        self.fdim = fdim
        self.rdim = rdim
        self.total_truncation = total_truncation

        self.driveamp = driveamp
        self.qubit_temp = qubit_temp
        self.resonator_temp = resonator_temp
        self.Qcap = Qcap
        self.Qohmic = Qohmic

        self.atol=atol
        self.rtol=rtol
        self.n_it=n_it
        
        # Set up fluxonium and resonator
        self.fluxonium = scq.Fluxonium(EJ=EJ, EC=EC, EL=EL, flux=flux, cutoff=110, truncated_dim=fdim)
        self.resonator = scq.Oscillator(E_osc=E_osc, truncated_dim=rdim, l_osc=L_osc)
        self.hilbertspace = scq.HilbertSpace([self.fluxonium, self.resonator])
        operator1 = self.fluxonium.n_operator()
        operator2 = self.resonator.creation_operator() + self.resonator.annihilation_operator()
        self.hilbertspace.add_interaction(g=g, op1=(operator1, self.fluxonium), op2=(operator2, self.resonator))
        H0 = (2 * np.pi) * self.hilbertspace.hamiltonian()
        self.dressed_energies, self.dressed_states = H0.eigenstates()
        self.hilbertspace.generate_lookup()

        # Bare state labeling
        self.bare_states = []
        self.bare_state_labels = []
        for i in range(fdim):
            for j in range(rdim):
                self.bare_states.append(qt.tensor(qt.basis(fdim, i), qt.basis(rdim, j)))
                self.bare_state_labels.append(f'{i},{j}')

        # Dressed state labeling
        overlap_matrix = np.zeros((len(self.dressed_states), len(self.bare_states)))
        for d_idx, state in enumerate(self.dressed_states):
            overlaps = [bare_state.dag() * state for bare_state in self.bare_states]
            probabilities = [abs(overlap)**2 for overlap in overlaps]
            overlap_matrix[d_idx] = probabilities

        self.dressed_state_labels = []
        used_labels = set()
        for d_idx, state in enumerate(self.dressed_states):
            probabilities = overlap_matrix[d_idx]
            max_prob = max(probabilities)
            idx = np.argmax(probabilities)
            label = self.bare_state_labels[idx]
            if max_prob >= 0.95 and label not in used_labels:
                self.dressed_state_labels.append(label)
                used_labels.add(label)
            else:
                top_indices = np.argsort(probabilities)[-2:][::-1]
                bare1, bare2 = self.bare_state_labels[top_indices[0]], self.bare_state_labels[top_indices[1]]
                prob1, prob2 = probabilities[top_indices[0]], probabilities[top_indices[1]]
                self.dressed_state_labels.append(f'un_{d_idx}_({bare1})_{prob1:.2f}_({bare2})_{prob2:.2f}')

        # Truncating dressed_state_labels
        self.dressed_state_labels = self.dressed_state_labels[:total_truncation]

        # Dressed Hamiltonian and operators
        diag_dressed_hamiltonian = qt.Qobj(np.diag(self.dressed_energies))
        self.diag_dressed_hamiltonian_trunc = self.truncate(diag_dressed_hamiltonian, total_truncation)
        self.operator2_dressed = (self.hilbertspace.op_in_dressed_eigenbasis((self.resonator.annihilation_operator(), self.resonator)) +
                                 self.hilbertspace.op_in_dressed_eigenbasis((self.resonator.creation_operator(), self.resonator)))
        self.operator2_dressed_trunc = self.truncate(self.operator2_dressed, total_truncation)
        self.driveomega = self.hilbertspace.energy_by_bare_index((0, 1)) - self.hilbertspace.energy_by_bare_index((0, 0))

        # Projectors
        self.e_ops = []
        self.e_op_labels = self.dressed_state_labels
        for i in range(total_truncation):
            projector = qt.basis(total_truncation, i) * qt.basis(total_truncation, i).dag()
            self.e_ops.append(projector)

        #constructor
        self.constructor = MEConstructor(hilbertspace=self.hilbertspace, truncated_dim=total_truncation, regenerate_lookup=True)

        #qubit capacitive noise
        self.constructor.add_channel(
            channel='flxn_cap',
            op=self.hilbertspace.op_in_dressed_eigenbasis(
                op_callable_or_tuple=self.fluxonium.n_operator,
                truncated_dim=total_truncation
            ),
            spec_dens_fun=cap_spectral_density,
            spec_dens_kwargs={'T': qubit_temp, 'EC': EC, 'Q_cap': Qcap},
            depolarization_only=True
        )

        #resonator decay
        self.constructor.add_channel(
            channel='res_decay',
            op=self.hilbertspace.op_in_dressed_eigenbasis(
                op_callable_or_tuple=(self.resonator.creation_operator() + self.resonator.annihilation_operator(), self.resonator),
                truncated_dim=total_truncation,
                op_in_bare_eigenbasis=True
            ),
            spec_dens_fun=ohmic_spectral_density,
            spec_dens_kwargs={'T': resonator_temp, 'Q': Qohmic},
            depolarization_only=True
        )
        self.c_ops = self.constructor.all_clustered_jump_ops()
        self.coeff = f'(2*{π})*{driveamp} * sin((2*{π}) * {self.driveomega} * t)'

    def truncate(self, operator: qt.Qobj, dimension: int) -> qt.Qobj:
        return qt.Qobj(operator[:dimension, :dimension])

    def get_connections(self, starting_index):
        data = []
        op = self.operator2_dressed_trunc.full()
        col = op[starting_index, :]
        abs_col = np.abs(col)
        large_indices = np.where(abs_col > 1e-20)[0]

        for j in large_indices:
            starting_label = self.dressed_state_labels[starting_index]
            final_label = self.dressed_state_labels[j]

            matrix_element = op[j, starting_index]  # <final | op | starting>
        
            starting_energy = self.dressed_energies[starting_index] / (2 * np.pi)
            final_energy = self.dressed_energies[j] / (2 * np.pi)
            energy_diff = (final_energy - starting_energy)

            if energy_diff > 0:
                type = 'up'
            if energy_diff < 0:
                type = 'down'

            try:
                res = self.constructor.unclustered_jumps['res_decay'][starting_index, j].rate
            except AttributeError:
                res = 0
            try:
                qub = self.constructor.unclustered_jumps['flxn_cap'][starting_index, j].rate
            except AttributeError:
                qub = 0
            decayrate = res + qub

            data.append({
                'Starting State': starting_label,
                'SI': starting_index,
                'Final_State': final_label,
                'FI': j,
                '<Final State| (a+adag) | Starting>': matrix_element,
                'Starting Energy': starting_energy,
                'Final Energy': final_energy,
                'Energy Diff': energy_diff,
                'Type': type,
                'Detuning to Dressed 01-00 Gap': np.abs(np.abs(energy_diff) - np.abs(self.driveomega)),
                'Omega_R': (np.abs(matrix_element)) * (self.driveamp),
                'Omega_R^2': (np.abs(matrix_element))**2 * (self.driveamp**2),
                'Omega^2': (np.abs(matrix_element))**2 * (self.driveamp**2) + np.abs(np.abs(energy_diff) - np.abs(self.driveomega)),

                # (Omega_R / Omega)^2
                'metric': np.abs( (np.abs(matrix_element)**2) * (self.driveamp**2) / ((np.abs(matrix_element)**2) * (self.driveamp**2) + np.abs(np.abs(energy_diff) - np.abs(self.driveomega))) ),
                # Omega_R ^2 / Omega
                'metric2': (np.abs((matrix_element)**2) * (self.driveamp**2)) / np.sqrt((np.abs(matrix_element)**2) * (self.driveamp**2) + np.abs(np.abs(energy_diff) - np.abs(self.driveomega))),
                'decay': decayrate
            })
        return pd.DataFrame(data)

    def gamma_matrix(self):
        totaltrunc = self.total_truncation
        gamma_matrix = np.zeros((totaltrunc, totaltrunc))
        for starting in np.arange(totaltrunc):
            for finish in np.arange(totaltrunc):
                try:
                    res = self.constructor.unclustered_jumps['res_decay'][starting, finish].rate
                except AttributeError:
                    res = 0
                try:
                    qub = self.constructor.unclustered_jumps['flxn_cap'][starting, finish].rate
                except AttributeError:
                    qub = 0
                decayrate = res + qub
                gamma_matrix[starting, finish] = decayrate
        return qt.Qobj(gamma_matrix)
    
    def process_level(self, starting_indices, c1, c2):
        dfs = []
        for nt in starting_indices:
            df_nt = self.get_connections(nt)
            dfs.append(df_nt)
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
        df = df[(df['metric'] > c1) | (df['decay'] > c2)]
        new_starting_indices = df['FI'].unique()
        
        return df, new_starting_indices
    
    def combined_unique(self, fulldf):
        return sorted(set(fulldf['Starting State'].unique()) | set(fulldf['Final_State'].unique()))

    def iterate_process_levels(self, starting_label='0,0', metriccutoff=1e-5, decaycutoff=1e-6, numsteps=2):
        op = self.operator2_dressed_trunc.full()

        #find the index of starting_label
        for i, label in enumerate(self.dressed_state_labels):
            if label == starting_label:
                starting_index = i
                break
        else:
            raise ValueError(f"Can't find starting_label in dressed_state_labels")

        #find connections from starting
        df1 = self.get_connections(starting_index)
        df1 = df1[(df1['metric'] > metriccutoff) | (df1['decay'] > decaycutoff)]  # use abs for monotonicity
        new_starting_labels = df1['FI'].unique() #new indices

        dfs = [df1]
        for level in range(2, numsteps + 1):
            if len(new_starting_labels) == 0:
                break
            # Connections to states from previous level
            df, new_starting_labels = self.process_level(new_starting_labels, metriccutoff, decaycutoff)
            dfs.append(df)

        all_dfs = pd.concat(dfs, ignore_index=True).drop_duplicates()
        fulldf = all_dfs
        unique_states = self.combined_unique(fulldf)
        
        return fulldf, unique_states
    
    def getindices(self, states):
        indices = []
        for label in states:
            if label in self.dressed_state_labels:
                pos = self.dressed_state_labels.index(label)
                indices.append(pos)
        return indices
    
    def subdynamics(self, keptindices, tfinal): #mesolve and floquet steady for truncated hilbert space
        if not keptindices:
            raise ValueError("keptindices is empty")
        if 0 not in keptindices:
            raise ValueError("potential no ground state issues")
        
        idx = keptindices
        H_sub = qt.Qobj(self.diag_dressed_hamiltonian_trunc[np.ix_(idx, idx)])
        V_sub = qt.Qobj(self.operator2_dressed_trunc[np.ix_(idx, idx)])

        newc_ops = []
        for op in self.c_ops:
            sub = op[np.ix_(idx, idx)]
            if not np.allclose(sub, 0.0, atol=1e-20):
                newc_ops.append(qt.Qobj(sub))

        sub_ground = idx.index(0)
        psi0 = qt.basis(len(idx), sub_ground)
        rho0 = psi0 * psi0.dag()

        H = [H_sub, [V_sub, self.coeff]]

        tlist = np.linspace(0, tfinal, 31)
        e_ops = [qt.basis(len(idx), i) * qt.basis(len(idx), i).dag() for i in range(len(idx))]

        options = qt.Options(store_states=True, atol=self.atol, rtol=self.rtol, nsteps=1000000000, progress_bar=False)
        result = qt.mesolve(H, rho0, tlist, c_ops=newc_ops, e_ops=e_ops, options=options)

        Op_t = (2*π * self.driveamp) * V_sub
        steady = qt.steadystate_floquet(H_sub, Op_t=Op_t, c_ops=newc_ops, w_d=(2*π) * self.driveomega, n_it=self.n_it)

        return result, steady

    def backtofull(self, rho_trunc, kept_indices): #convert truncated density operators to the full hilbert space by inserting 0's
        n = len(kept_indices)
        U_data = np.zeros((self.total_truncation, n), dtype=complex)
        for col, idx in enumerate(kept_indices):
            U_data[idx, col] = 1.0
        U = qt.Qobj(U_data)
        return U * rho_trunc * U.dag()
    
    def fulldynamics(self, tfinal): #mesolve in full hilbert space (total truncation)
        H0 = self.diag_dressed_hamiltonian_trunc
        V = self.operator2_dressed_trunc

        H = [H0, [V, self.coeff]]
        tlist = np.linspace(0, tfinal, 31)
        psi0 = qt.basis(self.total_truncation, 0)
        e_ops = [qt.basis(self.total_truncation, i) * qt.basis(self.total_truncation, i).dag() for i in range(self.total_truncation)]
        options = qt.Options(store_states=True, atol=self.atol, rtol=self.rtol, nsteps=1000000000, progress_bar=False)
        result = qt.mesolve(H, psi0, tlist, c_ops=self.c_ops, e_ops=e_ops, options=options)

        driveamp = self.driveamp
        driveomega = self.driveomega
        Op_t = (2*π * driveamp) * V
        steady = qt.steadystate_floquet(H0, Op_t=Op_t, c_ops=self.c_ops, w_d=(2*π) * driveomega, n_it=self.n_it)
        return result, steady
    
    def collect_convergence_grid(self, metric_cutoffs, decay_cutoffs, numsteps=15, starting_label='0,0'):
        records = []
        
        for mc in metric_cutoffs:
            for dc in decay_cutoffs:
                _, uniquestates = self.iterate_process_levels(
                    starting_label=starting_label, 
                    metriccutoff=mc, 
                    decaycutoff=dc, 
                    numsteps=numsteps
                )
                indices = self.getindices(uniquestates)
                n_states = len(indices)
                
                records.append({
                    'metriccutoff': mc,
                    'decaycutoff': dc,
                    'n_states': n_states,
                    'states': uniquestates.copy()
                })
        df_incomplete = pd.DataFrame(records)
        return df_incomplete

    def complete_convergence_grid(self, df_incomplete, tfinal=100):
        full_res, full_steady = self.fulldynamics(tfinal)
        rho_full_final = full_res.states[-1]

        full_time_states = full_res.states
        full_times = full_res.times
        
        for col in ['sub_time_states_full', 'rho_final_full', 'rho_steady_full', 'dist_final', 'dist_steady']:
            if col not in df_incomplete.columns:
                df_incomplete[col] = None
        
        # go through incomplete dataframe
        for idx, row in df_incomplete.iterrows():
            mc, dc, n_states, uniquestates = row['metriccutoff'], row['decaycutoff'], row['n_states'], row['states']
            if n_states == 0:
                continue
                
            indices = self.getindices(uniquestates)
            
            #truncated dynamics
            sub_res, sub_steady = self.subdynamics(indices, tfinal)
            rho_sub_final = sub_res.states[-1]

            #embed all substates
            sub_time_states_full = [self.backtofull(state, indices) for state in sub_res.states]
            
            #embed final and steady states
            rho_sub_final_full = self.backtofull(rho_sub_final, indices)
            rho_sub_steady_full = self.backtofull(sub_steady, indices)
            
            #distances
            dist_final = qt.tracedist(rho_sub_final_full, rho_full_final)
            dist_steady = qt.tracedist(rho_sub_steady_full, full_steady)
            
            #update row
            df_incomplete.at[idx, 'sub_time_states_full'] = sub_time_states_full
            df_incomplete.at[idx, 'rho_final_full'] = rho_sub_final_full
            df_incomplete.at[idx, 'rho_steady_full'] = rho_sub_steady_full
            df_incomplete.at[idx, 'dist_final'] = dist_final
            df_incomplete.at[idx, 'dist_steady'] = dist_steady
            
            print(f"mc={mc:.2e}, dc={dc:.2e} to {n_states:3d} states | "
                f"dist_final={dist_final:.2e}, dist_steady={dist_steady:.2e}")
        
        return df_incomplete, full_times, full_time_states
    
    def brute_force_state_reduction(self, base_states, max_k=2, tfinal=1000, n_times=31, threshold=0.05):
        fixed = '0,0'
        states = [s for s in base_states if s != fixed]
        #store '0,0' and base_states separately
        times = np.linspace(0, tfinal, n_times)

        idx_full = self.getindices([fixed] + states) #get indices where '0,0' is the first entry (so that our initial state is always ground)
        H_full = qt.Qobj(self.diag_dressed_hamiltonian_trunc[np.ix_(idx_full, idx_full)])
        V_full = qt.Qobj(self.operator2_dressed_trunc[np.ix_(idx_full, idx_full)])
        newc_ops_full = [qt.Qobj(op[np.ix_(idx_full, idx_full)]) for op in self.c_ops]
        sub_ground_full = idx_full.index(0)
        psi0_full = qt.basis(len(idx_full), sub_ground_full)
        H = [H_full, [V_full, self.coeff]]
        e_ops_full = [qt.basis(len(idx_full), i) * qt.basis(len(idx_full), i).dag() for i in range(len(idx_full))]
        options = qt.Options(store_states=True, atol=self.atol, rtol=self.rtol, nsteps=1000000000, progress_bar=False)

        full_result = qt.mesolve(H, psi0_full, times, c_ops=newc_ops_full, e_ops=e_ops_full, options=options)
        full_result_states = [self.backtofull(state, idx_full) for state in full_result.states]

        data = []
        good_states = []

        for k in range(1, max_k + 1):
            for combo in combinations(states, k):
                current_states = [fixed] + [s for s in states if s not in combo]
                idx = self.getindices(current_states)

                H_sub = qt.Qobj(self.diag_dressed_hamiltonian_trunc[np.ix_(idx, idx)])
                V_sub = qt.Qobj(self.operator2_dressed_trunc[np.ix_(idx, idx)])
                newc_ops = [qt.Qobj(op[np.ix_(idx, idx)]) for op in self.c_ops]

                sub_ground = idx.index(0)
                psi0 = qt.basis(len(idx), sub_ground)
                H = [H_sub, [V_sub, self.coeff]]

                e_ops = [qt.basis(len(idx), i) * qt.basis(len(idx), i).dag() for i in range(len(idx))]
                result2 = qt.mesolve(H, psi0, times, c_ops=newc_ops, e_ops=e_ops, options=options)
                res2states = [self.backtofull(state, idx) for state in result2.states]

                distances = [qt.tracedist(full_result_states[i], res2states[i]) for i in range(len(times))]
                mean_dist = np.mean(distances)

                row = {
                    'removed': list(combo),
                    'k': k,
                    'states': current_states.copy(),
                    'mean_distance': mean_dist
                }
                row.update({f'dist_t{t:.0f}': d for t, d in zip(times, distances)})
                data.append(row)

                if mean_dist < threshold:
                    good_states.append(current_states.copy())

        df = pd.DataFrame(data)

        plt.figure(figsize=(12, 6))
        for _, row in df.iterrows():
            plt.plot(times, [row[f'dist_t{t:.0f}'] for t in times], color='lightgray', alpha=0.5, linewidth=0.8)
        for states_set in good_states:
            row = df[df['states'].apply(lambda x: x == states_set)].iloc[0]
            plt.plot(times, [row[f'dist_t{t:.0f}'] for t in times], color='blue', linewidth=2)
        plt.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold = {threshold}')
        plt.xlabel('Time (ns)')
        plt.ylabel('Trace Distance')
        plt.title(f'Trace Distance vs Time\n({len(good_states)} good approximations)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        plt.show()

        return df
    
    def _build_path(
        self, 
        current_state, 
        current_path, 
        current_depth,
        all_dfs,
        all_pathways,
        max_cycles,
    ):
        #max depth, stop
        if current_depth >= max_cycles:
            return

        #found '1,0', stop and save path
        if current_state == '1,0' and current_path:
            all_pathways.append(current_path[:])
            return  
        
        #all transitions starting from this state
        matching_transitions = all_dfs[all_dfs['Starting State'] == current_state]

        #if none found, stop
        if matching_transitions.empty:
            return

        #build the next path (whether or not it's ultimately saved depends on if it reaches '1,0')
        for _, transition_row in matching_transitions.iterrows():
            next_state = transition_row['Final_State']

            transition_details = {
                'Starting State': transition_row['Starting State'],
                'Final_State': transition_row['Final_State'],
                'SI': transition_row['SI'],       
                'FI': transition_row['FI'],
                'Type': transition_row['Type'],
                'Detuning to Dressed 01-00 Gap': transition_row['Detuning to Dressed 01-00 Gap'],
                'Omega_R': transition_row['Omega_R'],
                'metric': transition_row['metric'],
                'decay': transition_row['decay']
            }

            new_path = current_path + [transition_details]
            self._build_path(
                next_state, 
                new_path, 
                current_depth + 1, 
                all_dfs, 
                all_pathways, 
                max_cycles,
            )
            
    def _remove_loops(self, df):
        seen = {}
        for i, state in enumerate(df['Final_State']):
            if state in seen:
                first_idx = seen[state]
                drop_rows = list(range(first_idx + 1, i + 1))  #drop after the first one up to and including the repeat
                return df.drop(drop_rows).reset_index(drop=True)
            seen[state] = i
        return df

    def trace_pathways(
        self, 
        starting_label, 
        metriccutoff, 
        decaycutoff, 
        numsteps, 
        max_cycles=3,
    ):
        #recursive function, traces all paths from '0,0' backwards through transitions in all_dfs that reach back to '1,0'
        all_dfs, _ = self.iterate_process_levels(
            starting_label=starting_label,
            metriccutoff=metriccutoff,
            decaycutoff=decaycutoff,
            numsteps=numsteps,
        )
        
        all_pathways = []
        self._build_path(starting_label, [], 0, all_dfs, all_pathways, max_cycles)
        
        pathdfs = [pd.DataFrame(path) for path in all_pathways]
        
        simplified_pathdfs = [self._remove_loops(df) for df in pathdfs]
        
        unique_pathdfs = []
        seen = set()
        for df in simplified_pathdfs:
            df_tuple = tuple(map(tuple, df.fillna('NaN').itertuples(index=False)))
            if df_tuple not in seen:
                seen.add(df_tuple)
                unique_pathdfs.append(df)
                
        return unique_pathdfs