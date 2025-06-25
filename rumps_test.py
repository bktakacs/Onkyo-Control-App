import rumps

class OnkyoStatusBarApp(rumps.App):
    @rumps.clicked("Volume up")
    def increase_volume(self, _):
        rumps.alert('volume increased')



OnkyoStatusBarApp("音響").run()