import sublime
import sublime_plugin

from os.path import basename, splitext

# Related reading:
#   https://forum.sublimetext.com/t/zoom-in-all-projects/69019/


## ----------------------------------------------------------------------------


def plugin_loaded():
    """
    Triggers on plugin load; if the user's preferences don't currently have the
    settings for specifying the minimum, maximum and default font sizes, then
    add them.

    The default font size is based on the current font size, while the others
    have the values that are used by default in the core routines.
    """
    settings = sublime.load_settings('Preferences.sublime-settings')
    defaults = {
        'default_font_size': settings.get('font_size'),
        'min_font_size': 8,
        'max_font_size': 128
    }

    updated = False
    for name, default in defaults.items():
        if not settings.has(name):
            settings.set(name, default)
            updated = True

    if updated:
        sublime.save_settings('Preferences.sublime-settings')


## ----------------------------------------------------------------------------


class FontResizeCommandRewriter(sublime_plugin.EventListener):
    """
    This event listener listens for the core commands that alter the global
    font size and rewrite them to use our new
    """
    def on_window_command(self, window, command, args):
        if command == 'increase_font_size':
            return ('global_font_size', {"action": "increase"})

        if command == 'decrease_font_size':
            return ('global_font_size', {"action": "decrease"})

        if command == 'reset_font_size':
            return ('global_font_size', {"action": "reset"})


## ----------------------------------------------------------------------------


class BaseFontSize():
    """
    This base class is the base class for all of the commands that know how to
    manipulate the font sizes in various conditions; it contains the common
    manipulation code and all common core routines so that the classes that use
    it only need to specify the specific logic for how to adjust the settings
    for their particular area of influence.
    """
    def global_font_constraints(self):
        """
        Return the currently configured global constraints on file size; the
        return is a three-tuple of sizes in the order of (default, min, max),
        as configured by the default global preferences.
        """
        settings = sublime.load_settings('Preferences.sublime-settings')
        return (
            settings.get('default_font_size', 10),
            settings.get('min_font_size', 8),
            settings.get('max_font_size', 128),
        )


    def increase_font(self):
        """
        Gets the current font size and increases it, then sets it back. The
        font size is constrained to the largest possible configured font size.
        """
        current = self.get_font_size()
        _, _, max_font = self.global_font_constraints()

        if current >= 36:
            current += 4
        elif current >= 24:
            current += 2
        else:
            current += 1

        if current > max_font:
            current = max_font

        self.set_font_size(current)


    def decrease_font(self):
        """
        Gets the current font size and decreases it, then sets it back. The
        font size is constrained to the smallest possible configured font size.
        """
        current = self.get_font_size()
        _, min_font, _ = self.global_font_constraints()

        if current >= 40:
            current -= 4
        elif current >= 26:
            current -= 2
        else:
            current -= 1

        if current < min_font:
            current = min_font

        self.set_font_size(current)


    def reset_font(self):
        """
        Resets the font size back to the default font size; how this works is
        dependent on the underlying implementation.
        """
        self.erase_font_size()


    def zoom_font(self, action="increase"):
        """
        This is the main logic of any command that's based on this subclass;
        using the action, this will proxy to the appropriate method to carry
        out the defined action; if the action is not valid, an error is logged
        to the console and nothing happens.
        """
        if action == "increase":
            return self.increase_font()

        if action == "decrease":
            return self.decrease_font()

        if action == "reset":
            return self.reset_font()

        print(f"plugin_name: unknown font action '{action}' provided")


## ----------------------------------------------------------------------------


class GlobalFontSizeCommand(BaseFontSize, sublime_plugin.ApplicationCommand):
    """
    Adjust the global font size up or down, or reset it back to the currently
    configured default font. The font adjustments are constrained by the
    configured font size limits.

    This command updates the Preferences.sublime-settings file directly, in a
    manner consistent with the built in commands, except that it does not just
    erase the font size and instead resets it to the default instead.
    """
    def run(self, action="increase"):
        """
        Alter the font size preference in the global Preferences file.
        """
        self.zoom_font(action)


    def get_font_size(self):
        """
        Gets the currently configured global font_size, falling back to the
        default font size if the font size is not specified.
        """
        settings = sublime.load_settings("Preferences.sublime-settings")
        default_size, _, _ = self.global_font_constraints()

        return settings.get("font_size", default_size)


    def set_font_size(self, new_font_size):
        """
        Sets the global font size to the new font size provided; this will
        adjust the global Preferences.sublime-settings file and persist it to
        disk.
        """
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("font_size", new_font_size)
        sublime.save_settings("Preferences.sublime-settings")


    def erase_font_size(self):
        """
        Reset the global font size back to the default font size; this is done
        by explicitly setting the font size to the default in the global
        Preferences.sublime-settings file.
        """
        default_size, _, _ = self.global_font_constraints()
        self.set_font_size(default_size)


## ----------------------------------------------------------------------------


class WindowFontSizeCommand(BaseFontSize, sublime_plugin.WindowCommand):
    """
    Adjust the window font size up or down, or reset it back to the currently
    configured default font. The font adjustments are constrained by the
    configured font size limits.

    This command updates the settings key in the project data of the current
    window, and thus affects all files in the window. If the window has a
    project, then the font size is persisted to disk when it changes; otherwise
    the changes only persist while the window exists.
    """
    def run(self, action="increase"):
        """
        Alter the font size preference in the project specific settings of the
        current window; the window need not have an explicit project.
        """
        self.zoom_font(action)


    def get_window_settings(self):
        """
        Get the settings dict from the current window; the return value is a
        dictionary that represents the settings, which may be empty if this
        window has no settings yet.
        """
        project_data = self.window.project_data() or {}
        return project_data.get("settings", {})


    def set_window_settings(self, settings):
        """
        Set the settings dict for the current window to the dict object given.
        This will replace the current settings data in the window, if any.
        """
        project_data = self.window.project_data() or {}
        project_data["settings"] = settings

        self.window.set_project_data(project_data)


    def get_font_size(self):
        """
        Get the font size associated with the project data in the current
        window, getting the default font size if it is not present in the
        settings yet.
        """
        settings = self.get_window_settings()
        default_size, _, _ = self.global_font_constraints()

        return settings.get("font_size", default_size)


    def set_font_size(self, new_font_size):
        """
        Set the new font size into the settings in the project data of the
        current window. This will persist that data to disk if this window has
        a sublime-project associated with it.
        """
        settings = self.get_window_settings()
        settings["font_size"] = new_font_size

        self.set_window_settings(settings)


    def erase_font_size(self):
        """
        Remove the font size from the project data in the current window; this
        will remove the setting from the object entirely, and is careful about
        what happens if the setting is not actually set. The new setting data
        will be persisted to disk if this window has a sublime-project
        associated with it.
        """
        settings = self.get_window_settings()
        if "font_size" in settings:
            del settings["font_size"]

            self.set_window_settings(settings)


## ----------------------------------------------------------------------------


class SyntaxFontSizeCommand(BaseFontSize, sublime_plugin.TextCommand):
    """
    Adjust the font size up or down, or reset it back to the currently
    configured default font. The font adjustments are made in the syntax
    specific settings for the syntax that is currently active in the view, and
    will be persisted to disk in the same manner as the global font preferences
    (except in a different file).
    """
    def run(self, edit, action="increase"):
        """
        Alter the font size preference in the syntax specific settings for the
        syntax in use in the currently active view.
        """
        self.zoom_font(action)


    def settings_file(self):
        """
        Get the name of the settings file that contains the settings for the
        syntax that is currently in use in the current view.
        """
        name = splitext(basename(self.view.syntax().path))[0]
        return f"{name}.sublime-settings"


    def get_font_size(self):
        """
        Get the font size associated with the current view, based on its
        syntax.
        """
        settings = sublime.load_settings(self.settings_file())
        default_size, _, _ = self.global_font_constraints()

        return settings.get("font_size", default_size)


    def set_font_size(self, new_font_size):
        """
        Update the font size associated with the current view; the data is
        stored into the syntax specific settings.
        """
        settings = sublime.load_settings(self.settings_file())
        settings.set("font_size", new_font_size)

        sublime.save_settings(self.settings_file())


    def erase_font_size(self):
        """
        Erase the font size from the current view's syntax specific settings;
        this will drop the font size back to either the global version or the
        project version
        """
        settings = sublime.load_settings(self.settings_file())
        settings.erase("font_size")

        sublime.save_settings(self.settings_file())


## ----------------------------------------------------------------------------


class ViewFontSizeCommand(BaseFontSize, sublime_plugin.TextCommand):
    """
    Adjust the view font size up or down, or reset it back to the currently
    configured default font. The font adjustments are constrained by the
    configured font size limits.

    This command updates the settings in the current view, which will adjust
    the font size in isolation to everything else.
    """
    def run(self, edit, action="increase"):
        """
        Alter the font size preference for the currently active view.
        """
        self.zoom_font(action)


    def get_font_size(self):
        """
        Get the font size associated with the current view.
        """
        default_size, _, _ = self.global_font_constraints()

        return self.view.settings().get("font_size", default_size)


    def set_font_size(self, new_font_size):
        """
        Update the font size associated with the current view.
        """
        self.view.settings().set("font_size", new_font_size)


    def erase_font_size(self):
        """
        Erase the font size from the current view; this will drop the font size
        back to either the global version, the project version, or the syntax
        version, as defined by the settings hierarchy.
        """
        self.view.settings().erase("font_size")


## ----------------------------------------------------------------------------
