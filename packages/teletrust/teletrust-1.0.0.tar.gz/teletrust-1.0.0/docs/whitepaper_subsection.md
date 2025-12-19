# 4.x Prime Gödel Codes for ESM Macro-States

The Ephemerality State Machine (ESM) admits a finite macro-state summary at each time step $t$. Three scalar features are extracted from the 61-node graph:

1. an activity bin $a_t \in \{0, \dots, 6\}$ from the normalized state norm,
2. an entropy bin $e_t \in \{0, \dots, 6\}$ from the spectral entropy $H(t)$,
3. a rail pattern bin $p_t \in \{0, \dots, 6\}$ from rail-wise variance / equalization.

The triplet $(a_t, e_t, p_t)$ defines a point in a $7 \times 7 \times 7$ grid, for a total of $7^3 = 343$ macro-states. Earlier sections flatten this triplet to an index $m_t \in \{0, \dots, 342\}$ and use it to visualize macro-code trajectories.

To obtain a log-friendly and privacy-preserving encoding of these macro-states, we introduce **Prime Gödel Codes**. The construction relies only on the fundamental theorem of arithmetic (unique factorization into primes) and yields a bijection between macro-states and integers.

We fix three disjoint sets of prime numbers:

$$
P(A) = (2, 3, 5, 7, 11, 13, 17) \\
P(E) = (19, 23, 29, 31, 37, 41, 43) \\
P(P) = (47, 53, 59, 61, 67, 71, 73)
$$

For any macro-state $(a, e, p)$, the macro prime code is:

$$
C(\text{macro}) = P_a(A) \cdot P_e(E) \cdot P_p(P)
$$

Because the three prime families are disjoint and every integer admits a unique factorization, this mapping is bijective: each macro-state is represented by a single integer, and the original bins $(a, e, p)$ can be recovered exactly from the prime factors of $C(\text{macro})$.

### Algorithm 1: Encode / Decode Macro Prime Code

```python
P_A = [2, 3, 5, 7, 11, 13, 17]
P_E = [19, 23, 29, 31, 37, 41, 43]
P_P = [47, 53, 59, 61, 67, 71, 73]

def encode_macro(a, e, p):
    # Bins are 0..6
    if not (0 <= a < 7 and 0 <= e < 7 and 0 <= p < 7):
        raise ValueError("Invalid macro bins.")
    return P_A[a] * P_E[e] * P_P[p]

def decode_macro(code):
    # Trial division over known primes; no need for general factoring.
    primes = [2, 3, 5, 7, 11, 13, 17,
              19, 23, 29, 31, 37, 41, 43,
              47, 53, 59, 61, 67, 71, 73]
    factors = []
    for p in primes:
        if code % p == 0:
            code //= p
            factors.append(p)
    if code != 1 or len(factors) != 3:
        raise ValueError("Invalid macro prime code.")
    a = P_A.index(factors[0])
    e = P_E.index(factors[1])
    p = P_P.index(factors[2])
    return a, e, p
```

The same mechanism applies at the micro-state level. The 61 nodes are indexed $i = 0, \dots, 60$ and assigned the first 61 prime numbers $(q_0, \dots, q_{60})$. At each time step the ESM maintains a Boolean configuration $b_t(i) \in \{0, 1\}$ subject to the design constraints:

* all “core” nodes $i \in \{0, \dots, 20\}$ are active ($b_t(i) = 1$);
* the remaining two “toggle” groups are never simultaneously all inactive;
* optionally, a 2/3-activity rule requires at least 41 nodes ON at all times.

The node prime code is then:

$$
C_t(\text{nodes}) = \prod_{i: b_t(i)=1} q_i
$$

This product is again invertible by factorization over the known prime table, yielding the exact set of active nodes. Big-integer arithmetic handles the resulting magnitudes without loss of information.

The **decay theorem** guarantees that, following cessation of external forcing, the ESM converges exponentially to a unique attractor defined by a constant vector $c_1$, vanishing spectral entropy, and equalized rail averages. In the prime-coded representation this implies the existence of a finite time $T$ such that for all $t \geq T$:

$$
C_t(\text{macro}) = C^\star(\text{macro}) \\
C_t(\text{nodes}) = C^\star(\text{nodes})
$$

where $C^\star(\text{macro})$ and $C^\star(\text{nodes})$ are fixed integers representing the attractor’s macro-state and node configuration. Empirically, simulations show the macro prime code and node prime code becoming constant at the same horizon at which the entropy and convergence-error curves flatten.

Logging these integers per time step turns the decay theorem into an **integer-valued safety contract**: an external auditor needs only the prime tables and the agreed thresholds to verify, from integers alone, that the system entered an approved attractor state within the specified time bound, without access to the underlying activations or content.
