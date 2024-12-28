import gradio as gr
from image_hosting.core.storage import ImageStorage, StorageError

class ImageHostingUI:
    def __init__(self):
        self.storage = ImageStorage()
    
    def upload_image(self, image) -> tuple[str, str]:
        """
        处理图片上传
        Returns:
            tuple: (上传状态信息, 图片URL)
        """
        if image is None:
            return "请选择要上传的图片", ""
        
        try:
            url = self.storage.save_image(image)
            return "✅ 图片上传成功！", url
        except StorageError as e:
            return f"❌ 上传失败：{str(e)}", ""
        except Exception as e:
            return f"❌ 系统错误：{str(e)}", ""
    
    def get_image_list(self) -> list[dict]:
        """获取图片列表"""
        try:
            return self.storage.get_image_list()
        except StorageError as e:
            return [{"filename": "错误", "url": "", "upload_time": str(e)}]
    
    def create_ui(self) -> gr.Blocks:
        """创建Gradio界面"""
        with gr.Blocks(title="ImageDoge") as demo:
            # 标题区域
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    # 空列用于占位
                    gr.Markdown("")
                with gr.Column(scale=5):
                    # 标题居中显示
                    gr.Markdown(
                        """
                        <h1 style='text-align: center; margin-top: 1em;'>ImageDoge</h1>
                        """,
                        elem_classes=["title"]
                    )
                with gr.Column(scale=1):
                    # 空列用于占位
                    gr.Markdown("")
            
            # 标签页
            with gr.Tabs() as tabs:
                # 上传标签页
                with gr.TabItem("上传图片"):
                    with gr.Row():
                        image_input = gr.Image(
                            label="选择图片",
                            type="filepath"
                        )
                    
                    with gr.Row():
                        upload_button = gr.Button(
                            "上传图片",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Row():
                        status_output = gr.Textbox(
                            label="上传状态",
                            interactive=False,
                            show_copy_button=False
                        )
                    
                    with gr.Row():
                        url_output = gr.Textbox(
                            label="图片地址",
                            interactive=False,
                            show_copy_button=True,  # 显示复制按钮
                            container=True
                        )
                
                # 图片列表标签页
                with gr.TabItem("图片列表"):
                    with gr.Row():
                        refresh_button = gr.Button(
                            "刷新列表",
                            size="sm"
                        )
                    
                    gallery = gr.Gallery(
                        label="已上传图片",
                        show_label=False,
                        columns=4,
                        height="auto",
                        object_fit="contain"
                    )
                    
                    with gr.Row():
                        image_info = gr.JSON(
                            label="图片信息",
                            visible=False
                        )
            
            # 事件处理
            def update_gallery():
                images = self.get_image_list()
                return {
                    gallery: [img["url"] for img in images],
                    image_info: images
                }
            
            # 上传后刷新图片列表
            upload_button.click(
                fn=self.upload_image,
                inputs=image_input,
                outputs=[status_output, url_output]
            ).success(
                fn=update_gallery,
                outputs=[gallery, image_info]
            )
            
            # 刷新按钮点击事件
            refresh_button.click(
                fn=update_gallery,
                outputs=[gallery, image_info]
            )
            
            # 页面加载时自动刷新列表
            demo.load(
                fn=update_gallery,
                outputs=[gallery, image_info]
            )
            
        return demo 