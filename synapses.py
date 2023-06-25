import ipywidgets as ipw
from IPython.display import display
from traitlets import Unicode
import uuid
from ipywidgets.widgets import register
from brian2gui.utilities import Interface, Entry


# @register('brian2gui.SynapsesInterface')
class SynapsesInterface(Interface):  # ipw.Box):
    """Class definition for Brian 2 Synapses graphical interface"""

    _model_name = Unicode('VBoxModel').tag(sync=True)
    _view_name = Unicode('VBoxView').tag(sync=True)

    _methods = ('linear', 'euler', 'heun')

    ENTRY_COUNTER = 0  # class variable shared by all instances
    ENTRIES = []
    ENTRY_BOX = ipw.VBox(children=[])  # NeuronGroupEntry()

    def __init__(self, gui=None):
        super().__init__()
        self.gui = gui
        self._CONTROLS = {
            'new': self._ITEMS['new'],
            'check': self._ITEMS['check'],
            'valid': self._ITEMS['valid']
        }
        self._CONTROLS['new'].on_click(self.on_new_clicked)
        self.children = (ipw.HBox(children=list(self._CONTROLS.values())),
                         self.ENTRY_BOX)

        # Set formatiing and layout
        #self._CONTROLS['new'].button_style = 'success'

    def on_new_clicked(self, b):
        self.ENTRIES.append(SynapseEntry(self))
        self.ENTRY_BOX.children = [item for item in self.ENTRIES]
        self.ENTRY_COUNTER += 1

    def __add__(self, entry):
        self.ENTRIES.append(entry)
        self.ENTRY_BOX.children = [item for item in self.ENTRIES]
        self.ENTRY_COUNTER += 1

    def __sub__(self, entry):
        del self.ENTRIES[entry.get_index()]
        self.ENTRY_BOX.children = self.ENTRIES


# Synapses(source, target=None, model=None, on_pre=None, pre=None, on_post=None,
# post=None, connect=None, delay=None, on_event='spike', multisynaptic_index=None,
# namespace=None, dtype=None, codeobj_class=None, dt=None, clock=None, order=0,
# method=('linear', 'euler', 'heun'), name='synapses*')
# @register('brian2gui.SynapseEntry')  # 'Jupter.HBox'
class SynapseEntry(Entry):  # Subclass br.Synpases too?

    _model_name = Unicode('VBoxModel').tag(sync=True)
    _view_name = Unicode('VBoxView').tag(sync=True)

    _ids = []

    # TODO: Remove group_type and use variable numbbers of arguments
    # , source='NeuronGroup', target='', model=None, on_pre=None,
    def __init__(self, interface=None, group_type=None):
        # pre=None, on_post=None, post=None, connect=None, delay=None): #,
        # *args, **kwargs):
        # on_event='spike', multisynaptic_index=None, namespace=None, dtype=None, codeobj_class=None, dt=None, clock=None, order=0, method=('linear', 'euler', 'heun'), name='synapses*'):

        super().__init__()
        self.interface = interface

        self.group_type = group_type  # HACK!

        # self._name.observe(self._change_label, names='value')
        self._uuid = uuid.uuid4()
        self._ids.append(self._uuid)

        # Create widgets
        inputs = self.interface.gui.get_input_names()
        neurons = self.interface.gui.get_neuron_group_names()
        sources = [*inputs, *neurons]

        self._ITEMS = {
            'source': ipw.Dropdown(tooltip='Source neurons', options=sources),
            'target': ipw.Dropdown(tooltip='Target neurons', options=neurons),
            'model': ipw.Textarea(placeholder='model', tooltip='Model equations'),
            'on_pre': ipw.Text(placeholder='on_pre'),  # description='on_pre'
            # description='on_post'
            'on_post': ipw.Text(placeholder='on_post'),
            'delay': ipw.Text(placeholder='delay'),
            'on_event': ipw.Text(placeholder='on_event'),
            'multisynaptic_index': ipw.Text(placeholder='multisynaptic_index'),
            'namespace': ipw.Text(placeholder='namespace'),
            'dtype': ipw.Text(placeholder='dtype'),
            'codeobj_class': ipw.Text(placeholder='codeobj_class'),
            'dt': ipw.Text(placeholder='dt'),
            'clock': ipw.Text(placeholder='clock'),  # description='condition'
            'order': ipw.Text(placeholder='order'),  # description='condition'
            'method': ipw.Dropdown(options=self.interface._methods, tooltip='Integrator'),
            'name': ipw.Text(value=f"Synapses{self.interface.ENTRY_COUNTER}",
                             placeholder='name', tooltip='name'),
            # Connect attributes
            # description='condition'
            'condition': ipw.Text(placeholder='condition'),
            'i': ipw.Text(placeholder='i'),  # description='i'
            'j': ipw.Text(placeholder='j'),  # description='j'
            # description='p'
            'p': ipw.BoundedFloatText(tooltip='p', value=1, min=0, max=1),
            'n': ipw.Text(placeholder='n'),  # description='n'
            # description='p'
            'skip_if_invalid': ipw.Checkbox(tooltip='skip_if_invalid'),
            # description='condition'
            'namespace': ipw.Text(placeholder='namespace'),
            'level': ipw.Text(placeholder='level')
        }

        self._FIELDS = ['source', 'target', 'model', 'on_pre', 'on_post',
                        'delay', 'on_event', 'method', 'name',
                        'condition', 'i', 'j', 'p', 'n']

        #self._source = self._ITEMS['source']
        #self._target = self._ITEMS['target']
        #self._name = self._ITEMS['name']
        for field in self._FIELDS:
            setattr(self, f'_{field}', self._ITEMS[field])

        # self._copy = ipw.Button(button_style='info',
        #                        tooltip='Copy', icon='copy') # description='Copy',
        # self._copy.on_click(self.on_click_copy)
        # self._delete = ipw.Button(button_style='danger',
        #                          tooltip='Delete', icon='fa-trash') # description='Delete',
        # self._delete.on_click(self.on_click_delete)

        #self.children = list(self._ITEMS.values())
        # ipw.Label(value='$\\rightarrow$'),
        children = [ipw.HBox(children=(self._ITEMS['source'], self._ITEMS['target'], self._ITEMS['model'], self._ITEMS['on_pre'], self._ITEMS['on_post'], self._ITEMS['delay'], self._ITEMS['on_event'])),
                    ipw.HBox(children=(self._ITEMS['i'], self._ITEMS['j'], self._ITEMS['n'], self._ITEMS['condition'], self._ITEMS['p'], self._ITEMS['method'], self._ITEMS['name'], self._CONTROL_STRIP))]
        #children.extend(self.copy, self.delete)
        self.children = children

        # formatting
        # Create a central dict of format values
        # , display='flex', flex_direction='column')
        self.layout = ipw.Layout(
            border='solid grey 1px', overflow_x='scroll', margin='2px')
        self._source.layout = ipw.Layout(width='110px', height='32px')
        self._target.layout = ipw.Layout(width='110px', height='32px')
        self._model.layout = ipw.Layout(min_width='325px')
        self._on_pre.layout = ipw.Layout(width='80px', height='32px')
        self._on_post.layout = ipw.Layout(width='80px', height='32px')
        self._delay.layout = ipw.Layout(width='80px', height='32px')
        self._on_event.layout = ipw.Layout(width='80px', height='32px')
        self._name.layout = ipw.Layout(width='110px', height='32px')
        self._p.layout = ipw.Layout(width='80px')
        self._n.layout = ipw.Layout(width='25px')
        self._method.layout = ipw.Layout(width='70px', height='32px')
        self._ITEMS['condition'].layout = ipw.Layout(
            width='110px', height='32px')
        self._ITEMS['i'].layout = ipw.Layout(width='110px', height='32px')
        self._ITEMS['j'].layout = ipw.Layout(width='110px', height='32px')
        #self._copy.layout = ipw.Layout(width='25px', height='28px')
        #self._delete.layout = ipw.Layout(width='25px', height='28px')
