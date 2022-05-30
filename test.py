import dearpygui.dearpygui as dpg

dpg.create_context()
with dpg.window(label="Delete Files", modal=True, show=False, id="sex", no_title_bar=True):
    dpg.add_text("Arsen Daudov.\n+7 705 584 2794")
    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("sex", show=False))

with dpg.window(label="Tutorial"):
    dpg.add_button(label="Open Dialog", callback=lambda: dpg.configure_item("sex", show=True))

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()