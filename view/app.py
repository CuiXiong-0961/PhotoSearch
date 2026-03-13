import os
from typing import List, Tuple, Optional, Any

import gradio as gr


def echo_chat(
    message: str, history: List[List[Any]]
) -> Tuple[List[List[Any]], str]:
    """
    简单对话逻辑：把用户输入的文字原样回复到聊天框。
    """
    if message is None:
        return history, ""

    # Chatbot(type="tuples") 要求 history 是 List[List[...]]，每条消息长度为 2
    history = history + [[message, message]]
    return history, ""


def on_image_upload(
    image: Any, desc: str, history: List[List[Any]]
) -> Tuple[List[List[Any]], Optional[Any], Optional[str]]:
    """
    图片上传后，将图片和说明文字一起显示在聊天框中。
    """
    if image is None:
        # 不修改聊天记录，也不改上传框和说明框
        return history, gr.update(), gr.update()

    print(image)

    # 在聊天框中直接展示图片，而不是本地磁盘路径
    # Gradio 5 需要使用 /gradio_api/file=... 形式的 URL，并且在 launch() 中配置 allowed_paths
    # image 是形如 C:\Users\...\AppData\Local\Temp\gradio\...\xxx.png 的本地路径
    # 这里统一转成 /gradio_api/file=本地绝对路径 的形式
    image_markdown = f"![上传的图片](/gradio_api/file={image})"
    # 左侧显示用户对图片的说明，右侧显示图片本身 + 说明文字
    bot_content = f"{image_markdown}\n\n{desc}" if desc else image_markdown
    history = history + [[desc or "图片说明", bot_content]]

    # 返回 history，同时把图片上传框和说明输入框都清空
    return history, gr.update(value=None), gr.update(value="")


def on_doc_upload(
    files: List[gr.File] | None, history: List[List[Any]]
) -> Tuple[List[List[Any]], Optional[List[gr.File]]]:
    """
    （已废弃）文档上传逻辑，保留占位，避免引用错误。
    """
    return history, gr.update()


def count_images_in_folder(
    folder: List[gr.File] | None, history: List[List[Any]]
) -> Tuple[List[List[Any]], Optional[List[gr.File]]]:
    """
    接收一个文件夹路径，统计其中图片文件数量并显示。
    """
    if not folder:
        # 不修改聊天记录，也不改上传框
        return history, gr.update()

    # Gradio 5 中，file_count="directory" 会返回一个文件列表
    # 其中每个元素都有 .name 属性（文件的完整路径）
    # 这里取第一个元素所在的目录作为文件夹路径
    first_file_path = folder[0].name
    folder_path = os.path.dirname(first_file_path)

    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    count = 0
    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in image_exts:
                    count += 1

    msg = f"该文件夹中共有 {count} 张图片。"
    history = history + [[msg, msg]]

    # 返回 history（供聊天框使用），并把 folder_input 清空
    return history, gr.update(value=None)


with gr.Blocks(title="PhotoSearch View") as demo:
    gr.Markdown("## PhotoSearch 对话界面（示范版）")

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="聊天框",
                type="tuples",
            )
            txt = gr.Textbox(
                label="输入消息",
                placeholder="输入内容后按下 Enter 或点击发送",
            )
            send_btn = gr.Button("送出")

            txt.submit(
                echo_chat,
                inputs=[txt, chatbot],
                outputs=[chatbot, txt],
            )
            send_btn.click(
                echo_chat,
                inputs=[txt, chatbot],
                outputs=[chatbot, txt],
            )

        with gr.Column(scale=1):
            gr.Markdown("### 图片 / 文件夹")

            img_input = gr.Image(
                label="上传图片（会显示在聊天框）",
                type="filepath",
            )

            img_desc = gr.Textbox(
                label="图片说明",
                placeholder="请输入这张图片的含义或补充说明",
            )

            img_send = gr.Button("发送图片与说明")

            folder_input = gr.File(
                label="选择文件夹（统计图片数量）",
                file_count="directory",
            )

            # 点击发送按钮或在说明框回车时，一次性发送「图片 + 说明」
            img_send.click(
                on_image_upload,
                inputs=[img_input, img_desc, chatbot],
                outputs=[chatbot, img_input, img_desc],  # 清空图片和说明
            )

            img_desc.submit(
                on_image_upload,
                inputs=[img_input, img_desc, chatbot],
                outputs=[chatbot, img_input, img_desc],  # 清空图片和说明
            )

            folder_input.change(
                count_images_in_folder,
                inputs=[folder_input, chatbot],
                outputs=[chatbot, folder_input],  # 清空上传文件夹框
            )


if __name__ == "__main__":
    # 外网访问
    demo.launch(
        server_name="0.0.0.0",          # 对外监听全部网卡
        server_port=7860,               # 自定义端口，例如 7860
        share=False,                    # 若想用 Gradio 临时外网链接可改 True
        # 允许前端通过 /gradio_api/file=... 访问本地文件
        # 这里把整个临时目录父级和当前工程目录都加入白名单，避免找不到路径
        allowed_paths=[
            os.getcwd(),
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # C:\Users\22096\AppData\Local\Temp\gradio 的上层
        ],
    )

