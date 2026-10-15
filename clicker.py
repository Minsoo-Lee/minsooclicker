import wx
import pyautogui

COUNTDOWN_SEC = 3                # '위치 보기' 누른 뒤 마우스를 옮길 시간(초)
DEFAULT_CLICK_DELAY_MS = 1000    # 클릭 대기 시간 기본값(ms)
MAX_CLICK_DELAY_MS = 60000       # 입력할 수 있는 최대값(ms)


class ClickerFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="클리커", size=(260, 220))

        self.target_pos = None  # 저장된 클릭 위치 (x, y)
        self.remaining = 0      # 카운트다운 남은 시간

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # 위에서부터: 위치 보기 버튼 → 위치 텍스트박스
        #            → 클릭 대기 설정 → 클릭하기 버튼
        self.btn_pos = wx.Button(panel, label="위치 보기")
        self.txt_pos = wx.TextCtrl(
            panel,
            style=wx.TE_READONLY | wx.TE_CENTER,
        )

        # 클릭 대기 시간: 라벨 + 숫자 입력칸을 가로로 배치
        delay_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_delay = wx.StaticText(panel, label="클릭 대기(ms)")
        self.spin_delay = wx.SpinCtrl(
            panel,
            min=0,
            max=MAX_CLICK_DELAY_MS,
            initial=DEFAULT_CLICK_DELAY_MS,
        )
        delay_sizer.Add(lbl_delay, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        delay_sizer.Add(self.spin_delay, 1, wx.EXPAND)

        self.btn_click = wx.Button(panel, label="클릭하기")

        sizer.Add(self.btn_pos, 0, wx.EXPAND | wx.ALL, 8)
        sizer.Add(self.txt_pos, 0, wx.EXPAND | wx.ALL, 8)
        sizer.Add(delay_sizer, 0, wx.EXPAND | wx.ALL, 8)
        sizer.Add(self.btn_click, 0, wx.EXPAND | wx.ALL, 8)

        panel.SetSizer(sizer)

        self.btn_pos.Bind(wx.EVT_BUTTON, self.on_show_position)
        self.btn_click.Bind(wx.EVT_BUTTON, self.on_click)

    def on_show_position(self, event):
        # 버튼을 누르는 순간엔 마우스가 버튼 위에 있으니,
        # 몇 초 기다렸다가 그때의 마우스 위치를 저장한다.
        self.btn_pos.Disable()
        self.remaining = COUNTDOWN_SEC
        self._tick()

    def _tick(self):
        if self.remaining > 0:
            self.txt_pos.SetValue(f"{self.remaining}초 뒤 위치 저장...")
            self.remaining -= 1
            # time.sleep 대신 CallLater를 써야 UI가 멈추지 않는다
            wx.CallLater(1000, self._tick)
            return

        x, y = pyautogui.position()
        self.target_pos = (x, y)
        self.txt_pos.SetValue(f"X: {x}, Y: {y}")
        self.btn_pos.Enable()

    def on_click(self, event):
        if self.target_pos is None:
            wx.MessageBox(
                "먼저 '위치 보기'로 위치를 저장하세요.",
                "알림",
            )
            return

        # 버튼을 누른 시점의 설정값을 읽는다
        delay_ms = self.spin_delay.GetValue()

        # 클릭 중에 버튼을 또 누르지 않도록 잠깐 막아 둔다
        self.btn_click.Disable()
        wx.CallLater(delay_ms, self._do_click)

    def _do_click(self):
        # 첫 클릭은 포커스 이동, 두 번째 클릭이 실제 동작
        x, y = self.target_pos
        pyautogui.click(x, y, clicks=2)
        self.btn_click.Enable()


if __name__ == "__main__":
    app = wx.App()
    frame = ClickerFrame()
    frame.Show()
    app.MainLoop()