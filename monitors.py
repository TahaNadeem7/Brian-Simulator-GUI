
import ipywidgets as ipw
#from IPython.display import display
from traitlets import Unicode
#import uuid
from ipywidgets.widgets import register

from brian2gui.utilities import Interface, Entry


# @register('brian2gui.MonitorsInterface')
class MonitorsInterface(Interface):  # ipw.Box):

    _model_name = Unicode('VBoxModel').tag(sync=True)
    _view_name = Unicode('VBoxView').tag(sync=True)

    _TYPES = ('SpikeMonitor', 'StateMonitor', 'PopulationRateMonitor', 'EventMonitor')
    #_CONTROLS = OrderedDict([('type', ipw.Dropdown(description='Type', options=_TYPES)),
                             #('new', ipw.Button(description='Add'))])
    # These should be moved into each instance due to different attributes

    # SpikeMonitor(source, variables=None, record=True, when=None, order=None, name='spikemonitor*', codeobj_class=None)
    # StateMonitor(source, variables, record, dt=None, clock=None, when='start', order=0, name='statemonitor*', codeobj_class=None)
    # PopulationRateMonitor(source, name='ratemonitor*', codeobj_class=None)
    # EventMonitor(source, event, variables=None, record=True, when=None, order=None, name='eventmonitor*', codeobj_class=None)
    #_HEADER = ('Source', 'Variables', 'Record')  # Label
    #_LABELS = [ipw.Label(value=field) for field in _HEADER]

    ENTRY_BOX = ipw.VBox(children=())
    ENTRIES = []
    ENTRY_COUNTER = 0

    def __init__(self, gui=None, *args, **kwargs):  # name='',

        super().__init__(*args, **kwargs)
        self.gui = gui  # Top level container

        self._CONTROLS = {
            'type': ipw.Dropdown(description='Type', options=self._TYPES),
            'new': self._ITEMS['new'],
            'check': self._ITEMS['check'],
            'valid': self._ITEMS['valid']
        }

        self.children = (ipw.HBox(children=list(self._CONTROLS.values())),
                         self.ENTRY_BOX)

        #self._CONTROLS['new'].on_click(self.on_new_clicked)

        # Formatting
        #self._CONTROLS['new'].layout = ipw.Layout(width='50px')
        #self._CONTROLS['new'].button_style = 'success'

    def on_new_clicked(self, b):
        self.ENTRIES.append(MonitorsEntry(self, self._CONTROLS['type'].value))
        self.ENTRY_BOX.children = [mon for mon in self.ENTRIES]
        self.ENTRY_COUNTER += 1

    def __add__(self, entry):
        self.ENTRIES.append(entry)
        self.ENTRY_BOX.children = [mon for mon in self.ENTRIES]
        self.ENTRY_COUNTER += 1

    def __sub__(self, entry):
        del self.ENTRIES[entry.get_index()]
        self.ENTRY_BOX.children = self.ENTRIES


# @register('brian2gui.MonitorsEntry')
class MonitorsEntry(Entry): #ipw.Box):  # MonitorsInterface

    #_model_name = Unicode('HBoxModel').tag(sync=True)
    #_view_name = Unicode('HBoxView').tag(sync=True)

    def __init__(self, interface=None, group_type='SpikeMonitor'): #, *args, **kwargs):

        super().__init__()
        self.interface = interface
        self.group_type = group_type
        #self._FIELDS = ['source', 'name']

        # SpikeMonitor(source, variables=None, record=True, when=None, order=None, name='spikemonitor*', codeobj_class=None)
        # StateMonitor(source, variables, record, dt=None, clock=None, when='start', order=0, name='statemonitor*', codeobj_class=None)
        # PopulationRateMonitor(source, name='ratemonitor*', codeobj_class=None)
        # EventMonitor(source, event, variables=None, record=True, when=None, order=None, name='eventmonitor*', codeobj_class=None)

        # Subclass these monitors?
        if self.group_type == 'SpikeMonitor':
            self._FIELDS = ['source', 'variables', 'record', 'name']  # when, order, codeobj_class

            self._variables = ipw.Text(value='', placeholder='variables', tooltip='Variables')
            self._record = ipw.ToggleButton(value=True, description='Record', tooltip='Record') #, icon='fa-floppy-o icon-save')

        elif self.group_type == 'StateMonitor':
            self._FIELDS = ['source', 'variables', 'record', 'name']  # dt, clock, when, order, codeobj_class

            self._variables = ipw.Text(value='', placeholder='variables', tooltip='Variables')
            self._record = ipw.Text(value='', placeholder='record', tooltip='Record: bool, sequence of ints')

        elif self.group_type == 'EventMonitor':
            self._FIELDS = ['source', 'event', 'record', 'name']  # when, order, codeobj_class

            self._event = ipw.Text(value='', placeholder='event', tooltip='Event')
            self._record = ipw.ToggleButton(value=True, description='Record', tooltip='Record') #, icon='fa-floppy-o icon-save')

        elif self.group_type == 'PopulationRateMonitor':
            self._FIELDS = ['source', 'name']  # codeobj_class

        #self._record = ipw.Checkbox(value=True, description='Record')
        sources = self.interface.gui.get_neuron_group_names()
        self._source = ipw.Dropdown(options=sources, tooltip='Source')

        self._name = ipw.Text(value=f"{self.group_type}{self.interface.ENTRY_COUNTER}",
                              tooltip='Name')
        self._name.observe(self._change_name, names='value')

        #self._copy = ipw.Button(button_style='info',
        #                        tooltip='Copy', icon='copy') # description='Copy',
        #self._copy.on_click(self.on_click_copy)
        #self._delete = ipw.Button(button_style='danger',
        #                          tooltip='Delete', icon='fa-trash') # description='Delete',
        #self._delete.on_click(self.on_click_delete)

        #self.children = [self._source, self._variables, self._record,
        #                 self._name, self._copy, self._delete]

        children = [self.__dict__[f'_{field}'] for field in self._FIELDS]
        #children.extend([self._copy, self._delete])
        children.append(self._CONTROL_STRIP)
        self.children = children

        # Layout and formatting
        self._source.layout = ipw.Layout(width='110px', height='32px')


        if hasattr(self, '_record'):
            self._record.layout = ipw.Layout(width='80px')
            # Change button colour when recording
            # Check this works with Text fields
            self._record.observe(self.on_record_click, names='value')
            if self._record.value is True:
                self._record.button_style = 'success'
                self._record.icon = 'fa-toggle-on'
            else:
                self._record.button_style = ''
                self._record.icon = 'fa-toggle-off'

        self._name.layout = ipw.Layout(width='110px', height='32px')
        self._copy.layout = ipw.Layout(width='25px', height='28px')
        self._delete.layout = ipw.Layout(width='25px', height='28px')

    def on_record_click(self, change):
        if change['new'] is True:
            self._record.button_style = 'success'
            self._record.icon = 'fa-toggle-on'
        else:
            self._record.button_style = ''
            self._record.icon = 'fa-toggle-off'
