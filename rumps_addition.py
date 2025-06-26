# add toggle mute to alt-r pageup key
if keyboard.Key.alt_r in self.pressed_keys and keyboard.Key.pageup:
    toggle_mute()

# notification for mute. add to toggle_mute() function
rumps.notification(title='Mute {}'.format(self.mute_status), subtitle=None, message=None, data=None, sound=False)

