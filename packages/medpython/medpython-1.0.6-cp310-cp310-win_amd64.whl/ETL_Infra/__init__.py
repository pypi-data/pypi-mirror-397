"""
This module will contain the ETL infrastructure code+config to load signals into Medial
data repository
"""


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'medpython.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from .etl_process import generate_labs_mapping_and_units_config, map_and_fix_units, finish_prepare_load, prepare_dicts \
     ,prepare_final_signals
