import gradio as gr
import pandas as pd
from image_hosting.core.storage import ImageStorage, StorageError
from image_hosting.config.settings import Config

class ImageHostingUI:
    def __init__(self):
        self.storage = ImageStorage()
    
    def upload_image(self, image, compress: bool, quality: int) -> tuple[str, str]:
        """
        处理图片上传
        
        Args:
            image: 上传的图片
            compress: 是否压缩
            quality: 压缩质量(0-100)
            
        Returns:
            tuple: (上传状态信息, 图片URL)
        """
        if image is None:
            return "请选择要上传的图片", ""
        
        try:
            url, sizes = self.storage.save_image(image, compress, quality)
            
            if sizes:
                original_size = self._format_size(sizes[0])
                compressed_size = self._format_size(sizes[1])
                compression_ratio = (1 - sizes[1]/sizes[0]) * 100
                status = (
                    f"✅ 图片上传成功！\n"
                    f"原始大小：{original_size}\n"
                    f"压缩后大小：{compressed_size}\n"
                    f"压缩率：{compression_ratio:.1f}%"
                )
            else:
                status = "✅ 图片上传成功！"
                
            return status, url
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
                        with gr.Column():
                            compress_checkbox = gr.Checkbox(
                                label="压缩图片",
                                value=False,
                                info="上传时压缩图片以提高访问效率"
                            )
                            
                            # 压缩质量滑动条，默认使用配置值
                            quality_slider = gr.Slider(
                                label="压缩质量",
                                minimum=1,
                                maximum=100,
                                step=1,
                                value=Config.COMPRESS_QUALITY,
                                interactive=True,
                                visible=False,  # 初始隐藏
                                info="数值越大，图片质量越好，文件越大"
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
                            show_copy_button=False,
                            max_lines=4  # 增加行数以显示压缩率
                        )
                    
                    with gr.Row():
                        url_output = gr.Textbox(
                            label="图片地址",
                            interactive=False,
                            show_copy_button=True
                        )
                    
                    # 复选框状态改变时显示/隐藏滑动条
                    compress_checkbox.change(
                        fn=lambda x: gr.update(visible=x),
                        inputs=compress_checkbox,
                        outputs=quality_slider
                    )
                
                # 图片列表标签页
                with gr.TabItem("图片列表"):
                    with gr.Row():
                        refresh_button = gr.Button(
                            "刷新列表",
                            size="sm"
                        )
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            # 使用DataFrame显示图片列表
                            image_list = gr.DataFrame(
                                headers=["文件名", "大小", "上传时间"],
                                datatype=["str", "str", "str"],
                                col_count=(3, "fixed"),
                                interactive=False,
                                wrap=True
                            )
                        
                        with gr.Column(scale=1):
                            # 图片预览
                            preview = gr.Image(
                                label="图片预览",
                                interactive=False,
                                height=300
                            )
                            # 图片URL显示和复制
                            with gr.Group():
                                url_display = gr.Textbox(
                                    label="图片链接",
                                    interactive=False,
                                    show_copy_button=True
                                )
            
            # 事件处理
            def update_image_list():
                try:
                    images = self.storage.get_image_list()
                    # 构建DataFrame数据
                    data = [
                        [
                            img["filename"],
                            img["size"],
                            img["upload_time"]
                        ]
                        for img in images
                    ]
                    df = pd.DataFrame(
                        data,
                        columns=["文件名", "大小", "上传时间"]
                    )
                    return df
                except StorageError as e:
                    return pd.DataFrame(
                        [[str(e), "", ""]],
                        columns=["文件名", "大小", "上传时间"]
                    )
            
            def preview_image(evt: gr.SelectData) -> tuple[str, str]:
                """处理图片预览和URL显示"""
                try:
                    images = self.storage.get_image_list()
                    # 获取选中行的图片信息
                    selected_image = images[evt.index[0]]
                    return selected_image["url"], selected_image["url"]
                except Exception:
                    return None, ""
            
            # 上传后刷新图片列表
            upload_button.click(
                fn=self.upload_image,
                inputs=[
                    image_input,
                    compress_checkbox,
                    quality_slider
                ],
                outputs=[status_output, url_output]
            ).success(
                fn=update_image_list,
                outputs=image_list
            )
            
            # 刷新按钮点击事件
            refresh_button.click(
                fn=update_image_list,
                outputs=image_list
            )
            
            # 点击列表行时预览图片和显示URL
            image_list.select(
                fn=preview_image,
                outputs=[preview, url_display]
            )
            
            # 页面加载时自动刷新列表
            demo.load(
                fn=update_image_list,
                outputs=image_list
            )
            
        return demo 
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """将字节大小转换为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB" 