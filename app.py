import wx


class MainFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title='Сборщик log-файлов ПК "Спринтер"', size=(600, 400), style=(wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION))
        self.Centre()
        self.Show()


if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame(None)
    app.MainLoop()
