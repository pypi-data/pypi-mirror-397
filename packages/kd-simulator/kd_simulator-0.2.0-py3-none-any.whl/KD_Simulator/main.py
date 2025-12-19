import numpy as np
import matplotlib.pyplot as plt



def compute_per_qubit_kd(rho_list):
    """
    Compute the KD distribution for each qubit from a list of single-qubit density matrices.
    Returns a list of 2x2 KD matrices, one for each qubit.
    """
    # Build single-qubit Hadamard
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    kd_matrices = []
    
    for rho_q in rho_list:
        # Compute KD for this qubit: (rho H†) ∘ Hᵀ
        rho_q_H = rho_q @ H
        Kd_q = rho_q_H * H.conj()

        # Check for imaginary components
        if not np.allclose(Kd_q.imag, 0, atol=1e-12):
            raise ValueError(
                f"KD matrix has non-real entries: max imaginary part = {np.max(np.abs(Kd_q.imag))}"
            )

        # Convert to real
        Kd_q = np.real(Kd_q)

        # Check for negative values
        if np.any(Kd_q < -1e-12):   # tolerance for numerical noise
            neg_vals = Kd_q[Kd_q < 0]
            raise ValueError(
                f"KD matrix has negative entries (beyond numerical tolerance): {neg_vals}"
            )
        
        kd_matrices.append(Kd_q)
    
    return kd_matrices

def sample_from_per_qubit_kd(kd_matrices, num_samples, rng):
    """
    Sample g and chi for each qubit independently from their marginal distributions.
    Returns g_all (num_samples, num_qubits) and chi_all (num_samples, num_qubits).
    """
    num_qubits = len(kd_matrices)
    g_all = np.zeros((num_samples, num_qubits), dtype=int)
    chi_all = np.zeros((num_samples, num_qubits), dtype=int)
    
    for q in range(num_qubits):
        # Flatten the 2x2 KD matrix for this qubit
        probs = kd_matrices[q].ravel()
        
        # Sample flat indices
        flat_indices = rng.choice(4, size=num_samples, p=probs)
        
        # Convert to 2D indices (row=g, col=chi for this qubit)
        g_all[:, q] = flat_indices // 2  # row index (0 or 1)
        chi_all[:, q] = flat_indices % 2  # column index (0 or 1)
    
    return g_all, chi_all

def Hadamard_vectorized(g_all, chi_all):
    """Apply Hadamard to all samples at once"""
    return chi_all.copy(), g_all.copy()

def PauliX_vectorized(g_all, chi_all, qubit):
    """Apply Pauli X to all samples at once"""
    g_all = g_all.copy()
    g_all[:, qubit] = (g_all[:, qubit] + 1) % 2
    return g_all, chi_all

def PauliZ_vectorized(g_all, chi_all, qubit):
    """Apply Pauli Z to all samples at once"""
    chi_all = chi_all.copy()
    chi_all[:, qubit] = (chi_all[:, qubit] + 1) % 2
    return g_all, chi_all

def CNOT_vectorized(g_all, chi_all, control_qubit, target_qubit, num_qubits):
    """Apply CNOT to all samples at once"""
    # Identity matrix of size num_qubits
    I = np.eye(num_qubits, dtype=int)
    
    # Construct A_ct and B_ct
    A_ct = (I + np.outer(I[:, target_qubit], I[control_qubit, :]))
    B_ct = (I + np.outer(I[:, control_qubit], I[target_qubit, :]))
    
    # Apply to all samples: (num_samples, num_qubits) @ (num_qubits, num_qubits).T
    new_g = (g_all @ A_ct.T) % 2
    new_chi = (chi_all @ B_ct.T) % 2
    
    return new_g, new_chi

def Zmeasurement_vectorized(g_all, chi_all, qubit, rng):
    """Perform Z measurement on all samples at once"""
    num_samples = g_all.shape[0]
    outcomes = g_all[:, qubit].copy()
    
    # Random coin flips for all samples
    flip_mask = rng.random(num_samples) < 0.5
    chi_all = chi_all.copy()
    chi_all[flip_mask, qubit] = (chi_all[flip_mask, qubit] + 1) % 2
    
    return outcomes, g_all, chi_all


def make_qubit_rhos(state_labels):
    states = {
        "0": np.array([[1, 0], [0, 0]], dtype=complex),
        "1": np.array([[0, 0], [0, 1]], dtype=complex),
        "+": 0.5 * np.array([[1, 1], [1, 1]], dtype=complex),
        "-": 0.5 * np.array([[1, -1], [-1, 1]], dtype=complex),
        "r": 0.5 * np.array([[1, -1j], [1j, 1]], dtype=complex),   # |R⟩
        "l": 0.5 * np.array([[1,  1j], [-1j, 1]], dtype=complex),   # |L⟩
    }
    return [states[s] for s in state_labels]



# -------------------------------------------------------
# 1. TOP-K MOST PROBABLE OUTCOMES
# -------------------------------------------------------
def plot_top_k(counts, num_qubits, k=20):
    total = counts.sum()
    if total == 0:
        print("No counts to plot.")
        return

    freqs = counts / total
    top_indices = np.argsort(counts)[-k:][::-1]
    top_freqs = freqs[top_indices]
    top_labels = [
        format(i, f'0{num_qubits}b')[::-1] 
        for i in top_indices
    ]

    plt.figure(figsize=(10, 4))
    plt.bar(range(k), top_freqs)
    plt.xticks(range(k), top_labels, rotation=60)
    plt.ylabel("Frequency")
    plt.title(f"Top {k} Measurement Outcomes")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# 2. GROUP BY HAMMING WEIGHT
# -------------------------------------------------------
def plot_hamming_weight(counts, num_qubits):
    total = counts.sum()
    if total == 0:
        print("No counts to plot.")
        return

    weights = np.array([bin(i).count("1") for i in range(2**num_qubits)])
    weight_counts = np.bincount(weights, weights=counts, minlength=num_qubits+1)
    weight_freqs = weight_counts / total

    plt.figure(figsize=(8, 4))
    plt.bar(range(num_qubits+1), weight_freqs)
    plt.xlabel("Hamming Weight (# of ones)")
    plt.ylabel("Frequency")
    plt.title("Distribution by Hamming Weight")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# 3. SINGLE-QUBIT MARGINAL DISTRIBUTIONS
# -------------------------------------------------------
def plot_single_qubit_marginals(counts, num_qubits):
    total = counts.sum()
    if total == 0:
        print("No counts to plot.")
        return

    marginals = []
    for q in range(num_qubits):
        # Probability qubit q is 1
        p1 = np.sum(counts[(np.arange(2**num_qubits) >> q) & 1])
        p0 = total - p1
        marginals.append([p0/total, p1/total])

    marginals = np.array(marginals)

    plt.figure(figsize=(6, 6))
    plt.imshow(marginals, aspect="auto", cmap="viridis")
    plt.colorbar(label="Probability")
    plt.xlabel("Outcome (0 or 1)")
    plt.ylabel("Qubit index")
    plt.title("Single-Qubit Marginals")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# 4. HEATMAP OF RAW SAMPLES (NOT ALL 2^n OUTCOMES)
# -------------------------------------------------------
def plot_sample_heatmap(output_all):
    plt.figure(figsize=(10, 5))
    plt.imshow(output_all.T, aspect='auto', cmap='Greys')
    plt.xlabel("Shot index")
    plt.ylabel("Qubit index")
    plt.title("Sampled Bitstring Heatmap")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# 5. CORRELATION MATRIX BETWEEN QUBITS
# -------------------------------------------------------
def plot_qubit_correlation(output_all):
    if output_all.shape[0] < 2:
        print("Need at least two qubits.")
        return

    corr = np.corrcoef(output_all.T)

    plt.figure(figsize=(6, 6))
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(label="Correlation")
    plt.title("Qubit Correlation Matrix")
    plt.tight_layout()
    plt.show()



