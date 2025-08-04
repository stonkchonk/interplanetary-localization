import os
import zipfile
import shutil
from common import Params


class Modifier:
    original_sol_properties = [
        "PoleRA\t\t\t286.13",
        "PoleDec\t\t\t63.87",
        "PrimeMeridian\t84.176",
        "RotationRate\t14.1844"
    ]
    remark = "// !MODDED!, original:"
    modded_sol_properties = [
        f"PoleRA\t\t\t270.0 {remark} 286.13",
        f"PoleDec\t\t\t90.0 {remark} 63.87",
        f"PrimeMeridian\t0.0 {remark} 84.176",
        f"RotationRate\t0.0 {remark} 14.1844"
    ]
    assert len(original_sol_properties) == len(modded_sol_properties)
    temp_folder = "temp/"
    mod_file_path = temp_folder + "planets/SolarSys.sc"
    pak_file = Params.se_catalogs_pak_file

    @staticmethod
    def _extract_pak_content():
        with zipfile.ZipFile(Params.se_catalogs_pak_file, 'r') as pak:
            pak.extractall(Modifier.temp_folder)

    @staticmethod
    def _mod_file_content() -> str:
        f = open(Modifier.mod_file_path, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        return content

    @staticmethod
    def _is_modified(mod_file_content: str) -> bool:
        return Modifier.remark in mod_file_content

    @staticmethod
    def _replace_mod_file_properties(mod_file_content: str, is_modified: bool) -> str:
        contained_properties = Modifier.original_sol_properties
        replacement_properties = Modifier.modded_sol_properties
        if is_modified:
            contained_properties = Modifier.modded_sol_properties
            replacement_properties = Modifier.original_sol_properties
        for idx, val in enumerate(contained_properties):
            mod_file_content = mod_file_content.replace(val, replacement_properties[idx])
        return mod_file_content

    @staticmethod
    def _content_to_mod_file(mod_file_content: str):
        with open(Modifier.mod_file_path, 'w', encoding='utf-8') as file:
            file.write(mod_file_content)

    @staticmethod
    def _write_to_pak():
        with zipfile.ZipFile(Modifier.pak_file, 'w', compression=zipfile.ZIP_DEFLATED) as pak:
            for root, dirs, files in os.walk(Modifier.temp_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve relative path inside pak
                    arcname = os.path.relpath(file_path, start=Modifier.temp_folder)
                    pak.write(file_path, arcname)

    @staticmethod
    def _clear_temp_folder():
        shutil.rmtree(Modifier.temp_folder)

    @staticmethod
    def setup():
        Modifier._extract_pak_content()
        mod_file_content = Modifier._mod_file_content()
        is_modified = Modifier._is_modified(mod_file_content)
        continue_setup = input(f"Sol properties currently {"" if is_modified else "un"}modified. Continue? [y/n]")
        if continue_setup.lower() != "y":
            Modifier._clear_temp_folder()
            print("Quit setup.")
            return
        modified_mod_file_content = Modifier._replace_mod_file_properties(mod_file_content, is_modified)
        Modifier._content_to_mod_file(modified_mod_file_content)
        Modifier._write_to_pak()
        Modifier._clear_temp_folder()
        if is_modified:
            print("Sol properties have been reversed to their original state.")
        else:
            print("Sol properties are now modified, the tool is now usable.")
            print("To reverse this, run this script again or reinstall SpaceEngine.")

    @staticmethod
    def check_modification_state() -> bool:
        Modifier._extract_pak_content()
        mod_file_content = Modifier._mod_file_content()
        is_modified = Modifier._is_modified(mod_file_content)
        Modifier._clear_temp_folder()
        return is_modified


if __name__ == "__main__":
    Modifier.setup()
