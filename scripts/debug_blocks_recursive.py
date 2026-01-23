import gradio as gr

def debug_blocks_recursive(blocks: gr.Blocks):
    print("=== DEBUG COMPONENTI GRADIO ===")

    def scan_component(comp, path="root"):
        comp_type = comp.__class__.__name__
        # Stampiamo label se c'è
        label = getattr(comp, "label", None)
        value = getattr(comp, "value", None)
        # Segnala valori sospetti
        suspicious = ""
        if value is not None and isinstance(value, bool) and comp_type not in ["Checkbox", "CheckboxGroup"]:
            suspicious = " <-- POSSIBILE ERRORE BOOLEANO NON VALIDO"
        print(f"{path}: {comp_type}, label={label}, value={value} (type={type(value)}){suspicious}")

        # Se il componente ha children (Rows, Columns, Tabs), scansione ricorsiva
        if hasattr(comp, "children") and comp.children:
            for i, child in enumerate(comp.children):
                scan_component(child, path=f"{path}.{comp_type}[{i}]")

    for i, child in enumerate(blocks.children):
        scan_component(child, path=f"root[{i}]")

    print("=== FINE DEBUG ===")


# ==============================
# Esempio di utilizzo
# ==============================
with gr.Blocks() as demo:
    with gr.Row():
        textbox1 = gr.Textbox(label="Nome", value="")
        checkbox1 = gr.Checkbox(label="Flag corretta", value=False)
        json1 = gr.JSON(label="Dati JSON", value={})
    with gr.Column():
        # Esempio di valore booleano non valido (proprio qui accadrebbe l'errore)
        bad_textbox = gr.Textbox(label="Test Bool Errato", value=True)  # <-- da correggere

# Avvio debug
debug_blocks_recursive(demo)
