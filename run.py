from traitlets import Unicode
import ipywidgets as ipw
from ipywidgets.widgets import register

from brian2 import *
from brian2gui.utilities import Interface
from brian2gui.neurons import NeuronGroupInterface, InputsInterface
from brian2gui.synapses import SynapsesInterface
from brian2gui.monitors import MonitorsInterface

from textwrap import dedent
import ast


# @register('brian2gui.Interface')
class RunInterface(Interface):  # brian2gui.

    #_model_name = Unicode('VBoxModel').tag(sync=True)
    #_view_name = Unicode('VBoxView').tag(sync=True)

    #_TYPES = ()
    # _CONTROLS = () #OrderedDict([('type', ipw.Dropdown(description='Type', options=_TYPES)),
    #             ('new', ipw.Button(description='Add'))])

    #ENTRY_BOX = ipw.VBox(children=())
    #ENTRIES = []
    #ENTRY_COUNTER = 0

    def __init__(self, gui=None, *args, **kwargs):  # name='',

        super().__init__(*args, **kwargs)
        self.gui = gui  # Top level container

        # TODO: Consolidate the ITEMS/CONTROLS
        self._FIELDS = ['timestep', 'duration']

        self._ITEMS = {
            'timestep': ipw.Text(description='Timestep, $dt$', value='0.1*ms'),
            'duration': ipw.Text(description='Duration', value='100*ms')
        }

        for field in self._FIELDS:
            setattr(self, f'_{field}', self._ITEMS[field])
        # 'fa-flask'

        self._CONTROLS = {
            'Build': ipw.Button(description='Build', tooltip='Build',
                                button_style='success', icon='fa-gears'),
            'Run': ipw.Button(description='Run', tooltip='Run',
                              button_style='success', icon='fa-play'),
            'Progress': ipw.FloatProgress(description='Progress', min=0, max=1,
                                          icon='fa-hourglass'),
            'Save': ipw.Button(description='Save', tooltip='Save',
                               button_style='info', icon='fa-save'),
            'Load': ipw.Button(description='Load', tooltip='Load',
                               button_style='info', icon='fa-sign-in'),
            'Filename': ipw.Text(description='Filename')
        }

        self.children = (
            ipw.HBox(children=[
                self._CONTROLS['Filename'],
                self._CONTROLS['Save'],
                self._CONTROLS['Load']]),
            ipw.HBox(children=[
                self._CONTROLS['Build'],
                self._timestep,
                self._duration,
                self._CONTROLS['Run'],
                self._CONTROLS['Progress']])
        )

        # (ipw.HBox(children=list(self._CONTROLS.values())),
        # ipw.HBox(children=self._LABELS),
        # self.ENTRY_BOX)

        # Set the button click event handlers
        self._CONTROLS['Build'].on_click(self.on_build_button_clicked)
        self._CONTROLS['Run'].on_click(self.on_run_button_clicked)
        self._CONTROLS['Save'].on_click(self.on_save_button_clicked)
        self._CONTROLS['Load'].on_click(self.on_load_button_clicked)

        # self._CONTROLS['new'].on_click(self.on_new_clicked)

    def on_build_button_clicked(self, button):
        # Generate the Brian2 script
        script = self.generate_brian2_script()
        # Save the generated script somewhere (e.g., as an attribute)
        self.generated_script = script

    def on_run_button_clicked(self, button):
        # Run the saved script and display the results
        self.run_brian2_script(self.generated_script)

    def on_save_button_clicked(self, button):
        # Save the generated script to a file
        self.save_script_to_file(
            self.generated_script, self._CONTROLS['Filename'].value)

    def on_load_button_clicked(self, button):
        # Load the script from a file and update the GUI
        self.load_script_from_file(self._CONTROLS['Filename'].value)

    def generate_brian2_script(self):

        # Extract values from the GUI components
        neuron_group_interface = NeuronGroupInterface(gui=self.gui)
        inputs_interface = InputsInterface(gui=self.gui)
        synapses_interface = SynapsesInterface(gui=self.gui)
        monitors_interface = MonitorsInterface()

        # Extract all values of the NeuronGroups
        neuron_group_values = self.extract_neuron_group_values(neuron_group_interface)[
            :-1]
        input_values = self.extract_input_values(inputs_interface)
        synapse_values = self.extract_synapse_values(synapses_interface)
        parameters_value = self.extract_parameters(self.gui)
        monitor_values = self.extract_monitor_values(monitors_interface)

        # print(neuron_group_values)
        # print(input_values)
        # print(synapse_values)
        # print(parameters_value)
        # print(monitor_values)

        script = []

        # Add required imports
        script.append("from brian2 import *\n")

        # Process parameters
        script.append(f"{parameters_value}\n\n")

        # Process neuron_groups
        for neuron_group in neuron_group_values:
            N = neuron_group["N"]
            model = neuron_group["model"]
            method = neuron_group["method"]
            threshold = neuron_group["threshold"]
            reset = neuron_group["reset"] if neuron_group["reset"] else None
            refractory = neuron_group["refractory"]
            name = neuron_group["name"] if neuron_group[
                "name"] else f'neuron_group_{len(script)}'

            model = f"eqs = Equations('''{model}''')\n"

            # Conditionally include parameters in neuron_group_str
            threshold_str = f"threshold='{threshold}'," if threshold else ""
            reset_str = f"reset='{reset}'," if reset else ""
            refractory_str = f"refractory={refractory}," if refractory else ""

            neuron_group_str = dedent(f'''\
            {name} = NeuronGroup({N}, model=eqs, {threshold_str} {reset_str} {refractory_str} method='{method}')''')

            script.append(model)
            script.append(neuron_group_str)

        # Process inputs
        i = 0
        for input_group in input_values:
            if "n" in input_group and "p" in input_group:
                script.append(
                    self.generate_binomial_function_code(input_group, i))
            elif "N" in input_group and "rates" in input_group:
                script.append(self.generate_poisson_group_code(input_group, i))
            elif "target" in input_group and "target_var" in input_group:
                script.append(self.generate_poisson_input_code(input_group, i))
            elif "indices" in input_group and "times" in input_group:
                script.append(
                    self.generate_spike_generator_group_code(input_group, i))
            elif "values" in input_group and "dt" in input_group:
                script.append(self.generate_timed_array_code(input_group, i))

            i += 1

        # Process synapses
        for synapse in synapse_values:
            source = synapse["source"]
            target = synapse["target"]
            model = synapse["model"] if synapse["model"] else None
            on_pre = synapse["on_pre"] if synapse["on_pre"] else None
            name = synapse["name"] if synapse["name"] else f'synapse_{len(script)}'

            model_str = f"model='{model}'," if model else ""
            on_pre_str = f"on_pre='{on_pre}'" if on_pre else ""

            if model_str and on_pre_str:
                synapse_str = f"{name} = Synapses({source}, {target}, {model_str}{on_pre_str})"
            elif model_str:
                synapse_str = f"{name} = Synapses({source}, {target}, {model_str[:-1]})"
            else:
                synapse_str = f"{name} = Synapses({source}, {target}, {model_str}{on_pre_str})"
                
            synapse_str += dedent(f'''
                {name}.connect(p={synapse["p"]})
                ''')
            script.append(synapse_str)

        # Process monitors
        i = 0

        for monitor in monitor_values:
            monitor_type = monitor["type"]
            source = monitor["source"]
            name = monitor["name"] if monitor[
                "name"] else f'{monitor_type}_{len(script)}'

            if monitor_type == "SpikeMonitor":
                variables = monitor["variables"]
                record = monitor["record"]

                monitor_str = dedent(f'''\
                Trace{i} = SpikeMonitor({source}, variables={variables}, record={record})
                run(1 * second, report='text')
                plot(Trace{i}.t/ms, Trace{i}.i, '.')
                ''')

            elif monitor_type == "StateMonitor":
                variables = monitor["variables"]
                record = monitor["record"]

                monitor_str = dedent(f'''\
                Trace{i} = StateMonitor({source}, variables={variables}, record={record})
                run(1 * second, report='text')
                ''')

                lst = ast.literal_eval(record)
                for k in range(len(lst)):
                    monitor_str += f"plot(Trace{i}.t/ms, Trace{i}[{lst[k]}].v/mV)\n"

            elif monitor_type == "PopulationRateMonitor":
                monitor_str = dedent(f'''\
                Trace{i} = PopulationRateMonitor({source})
                run(1 * second, report='text')
                plot(Trace{i}.t/ms, Trace{i}.rate/Hz)
                ''')

            elif monitor_type == "EventMonitor":
                event = monitor["event"]
                record = monitor["record"]

                monitor_str = dedent(f'''\
                Trace{i} = EventMonitor({source}, event='{event}', record={record})
                run(1 * second, report='text')
                plot(Trace{i}.t/ms, Trace{i}.i, '.')
                ''')

            i += 1

            if monitor_type == "StateMonitor" or monitor_type == "SpikeMonitor":
                display = dedent(f'''\
                xlabel('t (ms)')
                ylabel('{variables[1:-1]} (mV)')
                show()
                ''')

            elif monitor_type == "PopulationRateMonitor":
                display = dedent(f'''\
                xlabel('t (ms)')
                ylabel('Rate (Hz)')
                show()
                ''')

            elif monitor_type == "EventMonitor":
                display = dedent(f'''\
                xlabel('t (ms)')
                ylabel('Neuron index')
                show()
                ''')

            script.append(monitor_str)
            script.append(display)

        # Join the script lines
        brian2_script = "\n".join(script)

        # print(brian2_script)

        return brian2_script

    def run_brian2_script(self, script):
        exec(script)

    def save_script_to_file(self, script, filename):
        if not filename:
            print("Error: No filename provided.")
            return

        try:
            with open(filename, 'w') as file:
                file.write(script)
            print(f"Script saved to {filename}")
        except Exception as e:
            print(f"Error while saving script to file: {e}")

    def load_script_from_file(self, filename):
        if not filename:
            print("Error: No filename provided.")
            return

        try:
            with open(filename, 'r') as file:
                script = file.read()
                self.generated_script = script
            print(f"Script loaded from {filename}")
            self.update_GUI_with_script(script)
        except Exception as e:
            print(f"Error while loading script from file: {e}")

    def update_GUI_with_script(self, script):
        # TODO: Implement the logic to update the GUI based on the loaded script
        pass

    def extract_neuron_group_values(self, interface):
        neuron_group_values = []

        for entry in interface.ENTRIES:
            neuron_group_values.append({
                'N': entry.N,
                'model': entry.model,
                'method': entry.method,
                'threshold': entry.threshold,
                'reset': entry.reset,
                'refractory': entry.refractory,
                'name': entry.name,
            })

        return neuron_group_values

    def extract_input_values(self, interface):
        input_values = []

        for entry in interface.ENTRIES:
            entry_values = {}
            for field in entry._FIELDS:
                widget = getattr(entry, f'_{field}')
                if isinstance(widget, (ipw.Text, ipw.BoundedIntText, ipw.BoundedFloatText)):
                    entry_values[field] = widget.value
                elif isinstance(widget, ipw.Dropdown):
                    entry_values[field] = widget.value
                elif isinstance(widget, ipw.Checkbox):
                    entry_values[field] = widget.value
                elif isinstance(widget, ipw.IntSlider):
                    entry_values[field] = widget.value
            input_values.append(entry_values)
        return input_values

    def extract_synapse_values(self, interface):
        synapse_values = []
        for entry in interface.ENTRIES:
            synapse_data = {
                'source': entry._source.value,
                'target': entry._target.value,
                'model': entry._model.value,
                'on_pre': entry._on_pre.value,
                'on_post': entry._on_post.value,
                'delay': entry._delay.value,
                'on_event': entry._on_event.value,
                'method': entry._method.value,
                'name': entry._name.value,
                'condition': entry._condition.value,
                'i': entry._i.value,
                'j': entry._j.value,
                'p': entry._p.value,
                'n': entry._n.value,
            }
            synapse_values.append(synapse_data)
        return synapse_values

    def extract_parameters(self, interface):
        parameters = interface._Parameters_tab.children[0]
        parameter_values = parameters.value
        return parameter_values

    def extract_monitor_values(self, monitors_interface):
        monitor_values = []

        for entry in monitors_interface.ENTRIES:
            monitor_data = {
                'type': entry.group_type,
                'source': entry._source.value,
                'name': entry._name.value
            }

            if hasattr(entry, '_variables'):
                monitor_data['variables'] = entry._variables.value

            if hasattr(entry, '_record'):
                if isinstance(entry._record, ipw.ToggleButton):
                    monitor_data['record'] = entry._record.value
                elif isinstance(entry._record, ipw.Text):
                    monitor_data['record'] = entry._record.value

            if hasattr(entry, '_event'):
                monitor_data['event'] = entry._event.value

            monitor_values.append(monitor_data)

        return monitor_values

    def generate_binomial_function_code(self, input_group, i):
        n = input_group["n"]
        p = input_group["p"]
        approximate = input_group["approximate"]
        name = input_group["name"] if input_group[
            "name"] else f'input_group_{len(i)}'

        input_group_str = dedent(f'''\
        {name} = BinomialFunction({n}, {p}, approximate={approximate})
        ''')

        return input_group_str

    def generate_poisson_group_code(self, input_group, i):
        N = input_group["N"]
        rates = input_group["rates"] + "*Hz"
        name = input_group["name"] if input_group[
            "name"] else f'input_group_{len(i)}'

        input_group_str = dedent(f'''\
        {name} = PoissonGroup({N}, rates={rates})
        ''')

        return input_group_str

    def generate_poisson_input_code(self, input_group, i):
        target = input_group["target"]
        target_var = input_group["target_var"]
        N = input_group["N"]
        rate = input_group["rate"]
        weight = input_group["weight"]
        when = input_group["when"]
        order = input_group["order"]
        name = input_group["name"] if input_group[
            "name"] else f'input_group_{len(i)}'

        input_group_str = dedent(f'''\
        {name} = PoissonInput({target}, {target_var}, {N}, {rate}*Hz, {weight}, when='{when}', order={order})
        ''')

        return input_group_str

    def generate_spike_generator_group_code(self, input_group, i):
        N = input_group["N"]
        indices = input_group["indices"]
        times = input_group["times"]
        period = input_group["period"]
        when = input_group["when"]
        order = input_group["order"]
        sorted = input_group["sorted"]
        name = input_group["name"] if input_group[
            "name"] else f'input_group_{len(i)}'

        input_group_str = dedent(f'''\
        {name} = SpikeGeneratorGroup({N}, {indices}, {times}*second, period={period}*second, when='{when}', order={order}, sorted={sorted})
        ''')

        return input_group_str

    def generate_timed_array_code(self, input_group, i):
        values = input_group["values"]
        dt = input_group["dt"]
        name = input_group["name"] if input_group[
            "name"] else f'input_group_{len(i)}'

        input_group_str = dedent(f'''\
        {name} = TimedArray({values}, dt={dt})
        ''')

        return input_group_str
