import ipywidgets as widgets
from algorithms.shor import *
from IPython.display import display, Markdown, clear_output
from cirq_modules.cirq_shor import find_factor_cirq, naive_order_finder, quantum_order_finder

factoring_number = widgets.IntText(
    value=14,
    description='Type number for factoring:')

timeout = widgets.IntText(
    value=0,
    description='Type the timeout value:')

button = widgets.Button(description="Start Shor's algorithm")
output = widgets.Output()


def on_button_clicked(_):
    with output:
        clear_output()
        display(Markdown(
            f"Factoring for: {factoring_number.value} (timeout: {timeout.value})"))
        factor_list2 = find_factor(
            factoring_number.value, a=2, qubits_count=8, timeout=timeout.value)
        if len(factor_list2) == 0:
            display(Markdown(f"Qiskit - TIMEOUT: no factor found for the second run"))
        else:
            display(
                Markdown(f"Qiskit - Found factors second run: {factor_list2}"))
        factor_list3 = find_factor_cirq(
            factoring_number.value, naive_order_finder, False)
        if factor_list3 is None:
            display(Markdown(f"Cirq - TIMEOUT: no factor found for the naive run"))
        else:
            display(
                Markdown(f"Cirq - Found factors naive run: {factor_list3}"))
        factor_list4 = find_factor_cirq(
            factoring_number.value, quantum_order_finder, False)
        if factor_list4 is None:
            display(Markdown(f"Cirq - TIMEOUT: no factor found for the quantum run"))
        else:
            display(
                Markdown(f"Cirq - Found factors quantum run: {factor_list4}"))


button.on_click(on_button_clicked)


vbox = widgets.VBox([factoring_number, timeout, button, output])

info = Markdown("""# Shor's algorithm for all options
- Write positive number""")


def start_gui():
    display(info, vbox)
