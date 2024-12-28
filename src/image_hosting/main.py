from image_hosting.config.settings import Config
from image_hosting.ui.app import ImageHostingUI

def main():
    ui = ImageHostingUI()
    demo = ui.create_ui()
    demo.launch(
        server_name=Config.HOST,
        server_port=Config.PORT,
        debug=Config.DEBUG
    )

if __name__ == "__main__":
    main() 