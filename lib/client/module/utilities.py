def show_notification(title, content):
    import xbmcgui
    dialog = xbmcgui.Dialog()
    dialog.notification(title, content, xbmcgui.NOTIFICATION_INFO)

def show_warning(title, content):
    import xbmcgui
    dialog = xbmcgui.Dialog()
    dialog.notification(title, content, xbmcgui.NOTIFICATION_WARNING)

def show_error(title, content):
    import xbmcgui
    dialog = xbmcgui.Dialog()
    dialog.notification(title, content, xbmcgui.NOTIFICATION_ERROR)

def file_select(target, files):
    import os
    if os.path.isfile(target):
        return target
    largest_name = None
    largest_size = 0
    for file_info in files:
        size = file_info.get('size')
        if size>largest_size:
            largest_name = file_info.get('name')
            largest_size = size
    return target+'/'+largest_name

def get_string(id):
    import xbmcaddon
    str = xbmcaddon.Addon().getLocalizedString(id).encode('utf-8')
    return str