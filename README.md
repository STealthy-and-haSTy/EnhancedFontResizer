EnhancedFontResizer
===================

This is a simple package for Sublime Text 4 builds 4153 and up that allows you
to alter the font zoom:

  - Globally, in the Preferences.sublime-settings file
  - Per window, in the settings key of the project data for the window
  - By syntax, by updating your Syntax Specific sublime-settings file for you
  - Per view, adjusting only the current tab

In addition, when the font size is reset, the size resets a known default
rather than just erasing the setting (and reverting you back to the official
Sublime default).

In addition, new settings are added to the Preferences.sublime-settings file to
provide more control over the font zoom:

  - "default_font_size" to specify the font size to return to when resetting
  - "min_font_size" to specify the minimum desired font size while zooming
  - "max_font_size" to specify the maximum desired font size while zooming

The settings will be added to your preferences when the package loads, and set
to default values if they are not already present.


Menu Entries
============

A new menu entry `Preferences > EnhancedFontResizer` contains the full set of
font adjustment commands for all of the various situations.


Keyboard and Mouse controls
===========================

Under `Preferences > Package Settings > EnhancedFontResizer` are menu entries
for the keyboard and mouse mappings; the default files that ship with the
package have examples for all of the various font zoom options; copy the ones
you would like to use to your user preferences, un-comment them, and adjust as
desired.

By default, no key bindings are added, but Sublime's default key bindings will
map to the global font manipulation options.