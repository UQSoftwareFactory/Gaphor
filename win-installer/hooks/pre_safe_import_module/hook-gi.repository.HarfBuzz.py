"""Temporary hook to support HarfBuzz.

Work around for https://github.com/pyinstaller/pyinstaller/issues/5129
"""


def pre_safe_import_module(api):
    # PyGObject modules loaded through the gi repository are marked as
    # MissingModules by modulegraph so we convert them to
    # RuntimeModules so their hooks are loaded and run.
    api.add_runtime_module(api.module_name)
