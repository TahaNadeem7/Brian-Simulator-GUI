import ipywidgets as ipw
from IPython.display import display, HTML
from traitlets import Unicode
from ipywidgets.widgets import register
# import brian2 as br
from brian2gui.neurons import InputsInterface, NeuronGroupInterface
from brian2gui.synapses import SynapsesInterface
from brian2gui.monitors import MonitorsInterface
from brian2gui.run import RunInterface


INTEGRATOR_TYPES = ['Auto', 'linear', 'independent', 'exponential_euler',
                    'euler', 'rk2', 'rk4', 'heun', 'milstein']
INTEGRATORS = {name: ind for ind, name in enumerate(INTEGRATOR_TYPES)}


class Brian2GUI(ipw.Box):
    """Class definition for Brian 2 graphical user interface"""

    _model_name = Unicode('HBoxModel').tag(sync=True)
    _view_name = Unicode('HBoxView').tag(sync=True)

    _TAB_NAMES = ('Neurons', 'Synapses', 'Parameters', 'Monitors', 'Run', 'Results')

    def __init__(self):
        ipw.Box.__init__(self, _dom_classes=['widget-interact'])

        # These VBox's are placeholders for interface objects
        self._tabs = ipw.Tab(children=[ipw.VBox() for tab in self._TAB_NAMES])
        for ind, name in enumerate(self._TAB_NAMES):
            self._tabs.set_title(ind, name)
            setattr(self, f'_{name}_tab', self._tabs.children[ind])
            #self._tabs.children[ind].layout = ipw.Layout(width='800px')
            
         # Custom CSS for Tabs
        display(
                HTML(
                    """
            <style>
            .jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab {
                color: #4a4a4a;
                font-size: 22px;
                font-weight: bold;
                font-family: "Helvetica", Arial, sans-serif;
                padding: 5px 10px;
                margin: 5px 10px 0px 10px;
                width: 200px;
            }
            .jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current {
                background-color: #337ab7;
                border-top: 2px solid #1a73e8;
            }
            </style>
            """
                )
            )

        # Make accordion for each type of group
        self._accordion_titles = ['Inputs', 'Neurons']
        self._accordion = ipw.Accordion(children=[ipw.VBox(children=[InputsInterface(self)]),
                                                  ipw.VBox(children=[NeuronGroupInterface(self)])])
        for ind, title in enumerate(self._accordion_titles):  # self._CONTROLS.keys()):
            self._accordion.set_title(ind, title)

        display(
            HTML(
                """
                <style>
                .jupyter-widgets.widget-accordion .p-Accordion-header {
                    font-size: 24px; /* Increase the font size */
                    height: 50px; /* Increase the height of the accordion header */
                    line-height: 50px; /* Align the text vertically in the center */
                    font-weight: bold;
                    font-family: "Helvetica", Arial, sans-serif;
                    margin: 5px 10px 0px 10px;
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #c1c1c1;
                }
                .jupyter-widgets.widget-accordion .p-Accordion-header.p-mod-current {
                    background-color: #ffffff;
                    border-bottom: none;
                }
                </style>
                """
            )
        )



        self._accordion.selected_index = self._accordion_titles.index('Neurons')
        self._Neurons_tab.children = [self._accordion]
        # TODO: Add SpatialNeuron
        #self._Neurons_tab.children = [NeuronGroupInterface(self)]
        self._Synapses_tab.children = [SynapsesInterface(self)]
        self._Parameters_tab.children = [ipw.Textarea(placeholder='Enter additional parameters here. ')]
        self._Monitors_tab.children = [MonitorsInterface(self)]
        self._Run_tab.children = [RunInterface(self)]
        #self._Results_tab.children = [ipw.Button(description='Plot', tooltip='Plot',
        #                                         button_style='danger', icon='fa-area-chart')]

        self.children = [self._tabs]

        self.interfaces = {name: tab.children for name, tab in zip(self._TAB_NAMES, self._tabs.children)}
        self.entries = {
            'Inputs': self._Neurons_tab.children[0].children[0].children[0].ENTRIES,
            'Neurons': self._Neurons_tab.children[0].children[1].children[0].ENTRIES,
            'Synapses': self._Synapses_tab.children[0].ENTRIES,
            'Monitors': self._Monitors_tab.children[0].ENTRIES
        }
        # Assign callback functions
        self._accordion.observe(self.on_input_change, names='selected_index')
        self._tabs.observe(self.on_tab_change, names='selected_index')

        # Layout and formatting
        self._tabs.layout = ipw.Layout(width='1800px')  ### SIZE OF TABS
        #display(self)


        display(HTML("""
            <style>
                .widget-label {
                    font-size: 20px;
                }

                .widget-text input[type="text"],
                .widget-text input[type="number"] {
                    font-size: 16px;
                }

                .widget-checkbox input[type="checkbox"] {
                    width: 24px;
                    height: 24px;
                }

                .widget-dropdown > select {
                    font-size: 16px;
                }

                .widget-slider input[type="range"] {
                    height: 32px;
                }

                .widget-slider .widget-label {
                    font-size: 20px;
                }
            </style>
        """))

        ### TEXT AREA STYLE ###
        display(
            HTML(
                """
                <style>
                .custom-textarea {
                    font-size: 30px;
                    font-family: "Helvetica", Arial, sans-serif;
                }
                </style>
                """
            )
        )

# TODO: Fix this minor bug requiring back and forth between tabs to update
    def on_tab_change(self, change):
        '''Update lists of NeuronGroup names for Synapses and Monitors'''
        # Raise an error if there are no NeuronGroups
        if change['old'] == list(self.entries.keys()).index('Neurons'):
            inputs = self.get_input_names()
            neurons = self.get_neuron_group_names()
            sources = [*inputs, *neurons]

            for syn in self.entries['Synapses']:
                syn._source.options = sources
                syn._target.options = neurons
            for mon in self.entries['Monitors']:
                mon._source.options = neurons
        return

    def on_input_change(self, change):
        '''Update lists of NeuronGroup names for PoissonInput'''
        if change['old'] == self._accordion_titles.index('Neurons'):
            for inp in self.entries['Inputs']:
                if inp.group_type == 'PoissonInput':
                    inp._target.options = self.get_neuron_group_names()

    def get_input_names(self):
        return [obj.name for obj in self.entries['Inputs']]

    def get_neuron_group_names(self):
        return [group.name for group in self.entries['Neurons']]

    def _progress_reporter(self):
        '''
        Returns a widget and callback function to be used with Brian 2 simulations
        '''
        progress_slider = ipw.FloatProgress(description="Simulation progress",
                                            min=0, max=1)

        def update_progress(elapsed, complete, t_start, duration):
            progress_slider.value = complete
            if complete == 1:
                progress_slider.bar_style = 'success'
            else:
                progress_slider.bar_style = ''

        return progress_slider, update_progress

    def run_simulation(self):
        pass

    def generate_script(self):
        '''Output a script for execution without the GUI'''
        pass

    def save_state(self):
        pass

    def load_state(self, state=None):
        '''
        Pass a dictionary of values for each GUI element configuration
        state : {'Neurons' : [{'name': NG0', 'N': 10, 'model': 'dv/dt = ...'}]
                 'Synapses' : []}
        '''
