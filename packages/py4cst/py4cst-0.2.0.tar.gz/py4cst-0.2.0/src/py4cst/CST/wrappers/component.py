'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class Component(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Component')
        self.set_save_history(False)

    def create(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Component.New(component_name)
        """
        self.record_method('New', component_name)

    def delete(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Component.Delete(component_name)
        """
        self.record_method('Delete', component_name)

    def delete_all_empty_components(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Component.DeleteAllEmptyComponents(component_name)
        """
        self.record_method('DeleteAllEmptyComponents', component_name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Component.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def does_exist(self, component_name: str) -> bool:
        """
        VBA Call
        --------
        Component.DoesExist(component_name)
        """
        return self.query_method_bool('DoesExist', component_name)

    def get_next_free_name(self) -> str:
        """
        VBA Call
        --------
        Component.GetNextFreeName()
        """
        return self.query_method_str('GetNextFreeName')

    def hide(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Component.HideComponent(component_name)
        """
        self.record_method('HideComponent', component_name)

    def show(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Component.ShowComponent(component_name)
        """
        self.record_method('ShowComponent', component_name)

    def hide_selected(self) -> None:
        """
        VBA Call
        --------
        Component.Hide()
        """
        self.record_method('Hide')

    def show_selected(self) -> None:
        """
        VBA Call
        --------
        Component.Show()
        """
        self.record_method('Show')

    def hide_unselected(self) -> None:
        """
        VBA Call
        --------
        Component.HideUnselected()
        """
        self.record_method('HideUnselected')

    def show_unselected(self) -> None:
        """
        VBA Call
        --------
        Component.ShowUnselected()
        """
        self.record_method('ShowUnselected')

    def hide_all(self) -> None:
        """
        VBA Call
        --------
        Component.HideAll()
        """
        self.record_method('HideAll')

    def show_all(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAll()
        """
        self.record_method('ShowAll')

    def hide_all_ports(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllPorts()
        """
        self.record_method('HideAllPorts')

    def show_all_ports(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllPorts()
        """
        self.record_method('ShowAllPorts')

    def hide_all_field_sources(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllFieldSources()
        """
        self.record_method('HideAllFieldSources')

    def show_all_field_sources(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllFieldSources()
        """
        self.record_method('ShowAllFieldSources')

    def hide_all_lumped_elements(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllLumpedElements()
        """
        self.record_method('HideAllLumpedElements')

    def show_all_lumped_elements(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllLumpedElements()
        """
        self.record_method('ShowAllLumpedElements')

    def hide_all_wires(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllWires()
        """
        self.record_method('HideAllWires')

    def show_all_wires(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllWires()
        """
        self.record_method('ShowAllWires')

    def hide_all_dielectric(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllDielectric()
        """
        self.record_method('HideAllDielectric')

    def show_all_dielectric(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllDielectric()
        """
        self.record_method('ShowAllDielectric')

    def hide_all_metals(self) -> None:
        """
        VBA Call
        --------
        Component.HideAllMetals()
        """
        self.record_method('HideAllMetals')

    def show_all_metals(self) -> None:
        """
        VBA Call
        --------
        Component.ShowAllMetals()
        """
        self.record_method('ShowAllMetals')

