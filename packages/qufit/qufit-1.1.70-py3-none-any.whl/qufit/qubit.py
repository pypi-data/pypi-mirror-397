import numpy as np

def coherence_limit(nQ=2, T1_list=None, T2_list=None, gatelen=0.1):
        """
        This function is from qiskit
        The error per gate (1-average_gate_fidelity) given by the T1,T2 limit.

        Args:
            nQ (int): Number of qubits (1 and 2 supported).
            T1_list (list): List of T1's (Q1,...,Qn).
            T2_list (list): List of T2's (as measured, not Tphi). If not given assume T2=2*T1 .
            gatelen (float): Length of the gate.

        Returns:
            float: coherence limited error per gate.
        Raises:
            ValueError: If there are invalid inputs
        """
        # pylint: disable = invalid-name

        T1 = np.array(T1_list)

        if T2_list is None:
            T2 = 2 * T1
        else:
            T2 = np.array(T2_list)

        if len(T1) != nQ or len(T2) != nQ:
            raise ValueError("T1 and/or T2 not the right length")

        coherence_limit_err = 0

        if nQ == 1:

            coherence_limit_err = 0.5 * (
                1.0 - 2.0 / 3.0 * np.exp(-gatelen / T2[0]) - 1.0 / 3.0 * np.exp(-gatelen / T1[0])
            )

        elif nQ == 2:

            T1factor = 0
            T2factor = 0

            for i in range(2):
                T1factor += 1.0 / 15.0 * np.exp(-gatelen / T1[i])
                T2factor += (
                    2.0
                    / 15.0
                    * (
                        np.exp(-gatelen / T2[i])
                        + np.exp(-gatelen * (1.0 / T2[i] + 1.0 / T1[1 - i]))
                    )
                )

            T1factor += 1.0 / 15.0 * np.exp(-gatelen * np.sum(1 / T1))
            T2factor += 4.0 / 15.0 * np.exp(-gatelen * np.sum(1 / T2))

            coherence_limit_err = 0.75 * (1.0 - T1factor - T2factor)

        else:
            raise ValueError("Not a valid number of qubits")

        return coherence_limit_err