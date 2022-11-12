import logging
import sys

from gi.repository import Gtk

log = logging.getLogger(__name__)

if sys.platform != "darwin":
    macos_init = None
elif Gtk.get_major_version() == 3:
    import gi

    macos_app = None

    def open_file(macos_app, path, application):
        if path == __file__:
            return False

        application.new_session(filename=path)

        return True

    def block_termination(macos_app, application):
        quit = application.quit()
        return not quit

    def macos_init(application):
        try:
            gi.require_version("GtkosxApplication", "1.0")
        except ValueError:
            log.warning("GtkosxApplication not found")
            return

        from gi.repository import GtkosxApplication

        global macos_app
        if macos_app:
            return

        macos_app = GtkosxApplication.Application.get()

        macos_app.connect("NSApplicationOpenFile", open_file, application)
        macos_app.connect(
            "NSApplicationBlockTermination", block_termination, application
        )

else:

    def macos_init(application):
        pass
