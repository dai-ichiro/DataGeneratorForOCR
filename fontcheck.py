from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os
from PIL import ImageQt, Image

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.currentfont = QFont()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("pyQt6 sample")

        self.button1 = QPushButton('save as image')
        self.button1.clicked.connect(self.saveimage)

        self.label_1 = QLabel(self)
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.label_1.setText('［アート］【あーと】「東京駅」１２３壱弐参')

        self.setCentralWidget(self.button1)
    
    def saveimage(self):
        
        for onefont in fonts:
            
            fontfamily, bold = onefont.split(',')
            self.currentfont.setFamily(fontfamily)
            self.currentfont.setBold(int(bold))

            self.label_1.setFont(self.currentfont)
            self.label_1.adjustSize()

            image = ImageQt.fromqpixmap(self.label_1.grab()) #RGBA
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3]) # 3 is the alpha channel
            background.save(os.path.join('result', f'{fontfamily}_{bold}.jpg'))

if __name__ == "__main__":

    os.makedirs('result', exist_ok=True)
    
    with open('fonts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    fonts = [x.strip() for x in lines]

    app = QApplication([])
    ex =Window()
    ex.show()
    app.exec()