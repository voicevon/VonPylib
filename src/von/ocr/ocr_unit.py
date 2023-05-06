


class OcrUnit:
    def __init__(self) -> None:
        self.name = "new_target_area"
        self.top_offset = 0
        self.left_offset = 0
        self.width = 100
        self.height = 100



    def GetAreaImage(self, origin, left, top):
        y1 = top + self.top_offset
        x1 = left + self.left_offset
        y2 = y1 + self.height
        x2 = x1 + self.width
        cropped_image = origin[y1:y2, x1:x2]
        return cropped_image
