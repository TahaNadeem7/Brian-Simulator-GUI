import abc
import uuid
from traitlets import Unicode
import ipywidgets as ipw
from ipywidgets.widgets import register

__all__ = ['Interface', 'Entry']


# @abc.ABCMeta
# @register('brian2gui.Interface')
class Interface(ipw.Box):

    _model_name = Unicode('VBoxModel').tag(sync=True)
    _view_name = Unicode('VBoxView').tag(sync=True)

    _TYPES = None
    _CONTROLS = None

    ENTRY_BOX = ipw.VBox(children=())
    ENTRIES = []
    ENTRY_COUNTER = 0

    def __init__(self, gui=None, *args, **kwargs):  # name='',

        # ipw.Box.__init__(self, _dom_classes=['widget-interact'])
        super().__init__(*args, **kwargs)
        self.gui = gui  # Top level container

        self._ITEMS = {
            'new': ipw.Button(description='Add', button_style='success', tooltip='Create new object', icon='fa-plus'),
            'check': ipw.Button(description='Check', button_style='info', tooltip='Check Brian objects', icon='fa-search'),
            'valid': ipw.Valid()
        }

        # Set callback functions
        self._ITEMS['new'].on_click(self.on_new_clicked)
        self._ITEMS['check'].on_click(self.on_check_clicked)

        # Formatting
        self._ITEMS['new'].layout = ipw.Layout(width='60px', height='28px')
        #self._ITEMS['new'].button_style = 'success'
        self._ITEMS['check'].layout = ipw.Layout(width='80px', height='28px')
        self._ITEMS['valid'].layout = ipw.Layout(width='70px', height='28px')

        self._CONTROL_STRIP = ipw.HBox(children=list(self._ITEMS.values()))

    def on_new_clicked(self, b, *args, **kwargs):
        self.ENTRIES.append(type(self)(self, *args, **kwargs))
        self.ENTRY_BOX.children = self.ENTRIES  # [nge for nge in self.ENTRIES]
        self.ENTRY_COUNTER += 1

    def on_check_clicked(self, b, *args, **kwargs):
        '''Validate Brian objects'''
        self._CONTROLS['valid'].value = False
        for entry in self.ENTRIES:
            entry.create_brian_object()
        self._CONTROLS['valid'].value = True


# @abc.ABCMeta
# @register('brian2gui.Entry')
class Entry(ipw.Box):

    __metaclass__ = abc.ABCMeta

    _model_name = Unicode('HBoxModel').tag(sync=True)
    _view_name = Unicode('HBoxView').tag(sync=True)

    # TODO: Consolidate controls for interfaces and entries

    # 'primary' 'success' 'info' 'warning' 'danger'
    #_check = ipw.Button(button_style='info',
    #                   tooltip='Check', icon='fa-search') # description='Check',

    #_copy = ipw.Button(button_style='success',
    #                   tooltip='Copy', icon='copy') # description='Copy',

    #_delete = ipw.Button(button_style='danger',
    #                     tooltip='Delete', icon='fa-trash') # description='Delete',

    #_valid_w = ipw.Valid()

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, name):
        self._name.value = name

    def __init__(self, interface=None, *args, **kwargs):  # group_type=None,
        super().__init__()
        self.interface = interface
        if 'group_type' in kwargs:
            self.group_type = kwargs['group_type']
        self._uuid = uuid.uuid4()

        self._ITEMS = {
            'check': ipw.Button(button_style='info',
                                tooltip='Check', icon='fa-search'),
            'copy': ipw.Button(button_style='success',
                                tooltip='Copy', icon='copy'),
            'delete': ipw.Button(button_style='danger',
                                tooltip='Delete', icon='fa-trash'),
            'valid': ipw.Valid(value=True)
        }
        #self._ITEMS['name'] =

        # HACK!
        self._check = self._ITEMS['check']
        self._copy = self._ITEMS['copy']
        self._delete = self._ITEMS['delete']

        # Attach callback functions
        self._ITEMS['check'].on_click(self.on_click_check)
        self._ITEMS['copy'].on_click(self.on_click_copy)
        self._ITEMS['delete'].on_click(self.on_click_delete)

        # Formatting
        #self._ITEMS['name'].layout = ipw.Layout(width='110px', height='32px')
        self._ITEMS['check'].layout = ipw.Layout(width='50px', height='28px')
        self._ITEMS['copy'].layout = ipw.Layout(width='50px', height='28px')
        self._ITEMS['delete'].layout = ipw.Layout(width='50px', height='28px')
        self._ITEMS['valid'].layout = ipw.Layout(width='50px', height='28px')

        self._CONTROL_STRIP = ipw.HBox(children=list(self._ITEMS.values()))

        self._CONTROL_STRIP.layout = ipw.Layout(margin='0px', padding='0px')

    # TODO: Write general function
    def create_brian_object(self):
        pass

    def create_code(self):
        pass

    # TODO: Use exec to execute the whole simulation as a multiline string
    def run_code(self):
        eval(self._code)  # Single statement

    def _change_name(self, change):
        self._name.value = change['new']

    def get_index(self):
        return self.interface.ENTRIES.index(self)

    def get_values(self):
        """Get all values and put them in a dictionary"""
        # return OrderedDict([(label, w.value) for (label, w)
        #                     in zip(self._FIELDS, self.children)])
        # TODO: Revert to more elegant function above
        # pairs = {}
        # for key in self._FIELDS:
        #     attribute = '_{}'.format(key)
        #     if hasattr(self, attribute):
        #         pairs.append((key, self.__dict__[attribute].value))
        pairs = {key: self.__dict__[f'_{key}'].value 
                 for key in self._FIELDS if hasattr(self, f'_{key}')}
        return pairs

    def set_values(self, values_dict):
        """Set all values except the label from a dictionary"""
        for key, value in values_dict.items():
            # This can be simplified with property decorators:
            # e.g. self.__dict__[key] = value
            attribute = f'_{key}'
            if hasattr(self, attribute) and key != 'name':
                self.__dict__[attribute].value = value

    def on_click_check(self, b):
        self.create_brian_object()

    def on_click_copy(self, b):
        clone = type(self)(self.interface, self.group_type)  # self.deepcopy()
        clone.set_values(self.get_values())
        # Insert after original
        self.interface.ENTRIES.insert(self.get_index()+1, clone)
        self.interface.ENTRY_BOX.children = self.interface.ENTRIES
        self.interface.ENTRY_COUNTER += 1

    def on_click_delete(self, b):
        del self.interface.ENTRIES[self.get_index()]
        self.interface.ENTRY_BOX.children = self.interface.ENTRIES


# @register('brian2gui.Simulated')
class Simulated(metaclass=abc.ABCMeta):
    '''Class for simulated objects.
    See: http://brian2.readthedocs.io/en/stable/user/running.html'''

    #__metaclass__ = abc.ABCMeta

    _dt = None
    _schedule = ['start', 'groups', 'thresholds', 'synapses', 'resets', 'end']
    _when = None
    _order = None  # Default: 0
