def check_component_types(component, path="root", warnings_list=None):
    """
    Controlla ricorsivamente i componenti Gradio e segnala valori con tipi sospetti.
    Ora include anche la label dei componenti nei warning e aggiorna correttamente il summary.
    """
    if warnings_list is None:
        warnings_list = []

    # Ottieni label se disponibile
    label = getattr(component, "label", None)

    # Controllo valore
    if hasattr(component, "value"):
        val_type = type(component.value)
        is_warning = False

        if isinstance(component.value, bool) and component.__class__.__name__ in ["Textbox", "JSON"]:
            is_warning = True
        elif component.__class__.__name__ in ["Textbox", "HTML", "File"] and component.value in [None, []]:
            is_warning = True

        if is_warning:
            warnings_list.append((path, component.__class__.__name__, label))
            print(f"[WARNING] {path} (label='{label}'): {component.__class__.__name__} ha value={component.value}")
        else:
            print(f"[OK] {path} (label='{label}'): {component.__class__.__name__} value tipo={val_type.__name__}")
    else:
        print(f"[OK] {path} (label='{label}'): {component.__class__.__name__} (nessun value)")

    # Ricorsione sui figli comuni di Gradio
    children_attrs = ["children", "Row", "Column", "Form"]
    for attr in children_attrs:
        if hasattr(component, attr):
            children = getattr(component, attr)
            if children:
                for idx, child in enumerate(children):
                    check_component_types(child, f"{path}.{attr}[{idx}]", warnings_list)

    # Solo al livello root stampa il summary
    if path == "root":
        print("\n[SUMMARY] check_component_types completato")
        print(f"Totale componenti analizzati: {len(warnings_list) + sum(1 for _ in _iterate_components(component))}")
        print(f"Totale warning rilevati: {len(warnings_list)}")
        if warnings_list:
            print("Componenti coinvolti nei warning:")
            for w_path, w_type, w_label in warnings_list:
                print(f"- {w_path} (label='{w_label}') : {w_type}")

def _iterate_components(component):
    """Helper generator per contare tutti i componenti (ricorsivamente)"""
    yield component
    children_attrs = ["children", "Row", "Column", "Form"]
    for attr in children_attrs:
        if hasattr(component, attr):
            children = getattr(component, attr)
            if children:
                for child in children:
                    yield from _iterate_components(child)
