import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
from math import gcd
from numpy.random import randint
import pandas as pd
from fractions import Fraction
from time import perf_counter

import sympy


def c_amod15(a, power):
    """Controlled multiplication by a mod 15"""
    if a not in [2, 4, 7, 8, 11, 13]:
        raise ValueError("'a' must be 2,4,7,8,11 or 13")
    U = QuantumCircuit(4)
    for iteration in range(power):
        if a in [2, 13]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [7, 8]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [4, 11]:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = "%i^%i mod 15" % (a, power)
    c_U = U.control()
    return c_U


def qft_dagger(n):
    """n-qubit QFTdagger the first n qubits in circ"""
    qc = QuantumCircuit(n)
    # Don't forget the Swaps!
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

# def a2jmodN(a, j, N):
#     """Compute a^{2^j} (mod N) by repeated squaring"""
#     for i in range(j):
#         a = np.mod(a**2, N)
#     return a


def qpe_amod15(a, n_count, show):
    qc = QuantumCircuit(4+n_count, n_count)
    for q in range(n_count):
        qc.h(q)     # Initialize counting qubits in state |+>
    qc.x(3+n_count)  # And auxiliary register in state |1>
    for q in range(n_count):  # Do controlled-U operations
        qc.append(c_amod15(a, 2**q),
                  [q] + [i+n_count for i in range(4)])
    qc.append(qft_dagger(n_count), range(n_count))  # Do inverse-QFT
    qc.measure(range(n_count), range(n_count))
    # Simulate Results
    aer_sim = Aer.get_backend('aer_simulator')
    # Setting memory=True below allows us to see a list of each sequential reading
    t_qc = transpile(qc, aer_sim)
    qobj = assemble(t_qc, shots=1)
    result = aer_sim.run(qobj, memory=True).result()
    readings = result.get_memory()
    if show:
        print("Register Reading: " + readings[0])
    phase = int(readings[0], 2)/(2**n_count)
    if show:
        print("Corresponding Phase: %f" % phase)
    return phase


def find_factor(N, a, qubits_count, show=False, timeout=0):
    factor_found = False
    attempt = 0
    found = []
    start = perf_counter()
    while not factor_found:
        attempt += 1
        if show:
            print("\nAttempt %i:" % attempt)
        phase = qpe_amod15(a, qubits_count, show)  # Phase = s/r
        # Denominator should (hopefully!) tell us r
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        if show:
            print("Result: r = %i" % r)
        if phase != 0:
            # Guesses for factors are gcd(x^{r/2} ±1 , 15)
            guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]
            if show:
                print("Guessed Factors: %i and %i" % (guesses[0], guesses[1]))
            for guess in guesses:
                # Check to see if guess is a factor
                if guess not in [1, N] and (N % guess) == 0:
                    if show:
                        print("*** Non-trivial factor found: %i ***" % guess)
                    factor_found = True
                    found.append(guess)
        if timeout != 0 and (perf_counter() - start) > timeout:
            return []
    return found


def find_factor_return1st(N, a, qubits_count, show=False, timeout=0):
    if sympy.isprime(N):
        return N
    if N % 2 == 0:
        return 2
    factor_found = False
    attempt = 0
    found = []
    start = perf_counter()
    while not factor_found:
        attempt += 1
        if show:
            print("\nAttempt %i:" % attempt)
        phase = qpe_amod15(a, qubits_count, show)  # Phase = s/r
        # Denominator should (hopefully!) tell us r
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        if show:
            print("Result: r = %i" % r)
        if phase != 0:
            # Guesses for factors are gcd(x^{r/2} ±1 , 15)
            guesses = [gcd(a**(r//2)-1, N), gcd(a**(r//2)+1, N)]
            if show:
                print("Guessed Factors: %i and %i" % (guesses[0], guesses[1]))
            for guess in guesses:
                # Check to see if guess is a factor
                if guess not in [1, N] and (N % guess) == 0:
                    if show:
                        print("*** Non-trivial factor found: %i ***" % guess)
                    factor_found = True
                    found.append(guess)
        if timeout != 0 and (perf_counter() - start) > timeout:
            return None
    return found[0]


if __name__ == "__main__":
    N = 15
    a = 7
    qubits_count = 8
    find_factor(N, a, qubits_count, True)
