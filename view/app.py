import os
from typing import List, Tuple, Optional, Any

import gradio as gr


def echo_chat(
    message: str, history: List[Tuple[str, Any]]
) -> Tuple[List[Tuple[str, Any]], str]:
    """
    简单对话逻辑：把用户输入的文字原样回复到聊天框。
    """
    if message is None:
        return history, ""

    history = history + [(message, message)]
    return history, ""


def on_image_upload(
    image: Any, history: List[Tuple[str, Any]]
) -> List[Tuple[str, Any]]:
    """
    图片上传后，将图片显示在聊天框中。
    """
    if image is None:
        return history

    history = history + [("图片已上传：", image)]
    return history


def on_doc_upload(
    files: List[gr.File] | None, history: List[Tuple[str, Any]]
) -> List[Tuple[str, Any]]:
    """
    文档上传后，只显示文件名信息在聊天框中。
    """
    if not files:
        return history

    file_names = [os.path.basename(f.name) for f in files]
    msg = f"已收到文档：{', '.join(file_names)}"
    history = history + [(msg, msg)]
    return history


def count_images_in_folder(
    folder: gr.File | None, history: List[Tuple[str, Any]]
) -> List[Tuple[str, Any]]:
    """
    接收一个文件夹路径，统计其中图片文件数量并显示。
    """
    if folder is None:
        return history

    folder_path = folder.name

    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    count = 0
    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in image_exts:
                    count += 1

    msg = f"该文件夹中共有 {count} 张图片。"
    history = history + [(msg, msg)]
    return history


with gr.Blocks(title="PhotoSearch View") as demo:
    gr.Markdown("## PhotoSearch 对话界面（示范版）")

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="聊天框",
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
            gr.Markdown("### 图片 / 文档 / 文件夹")

            img_input = gr.Image(
                label="上传图片（会显示在聊天框）",
                type="filepath",
            )

            doc_input = gr.File(
                label="上传文档（只显示文件名）",
                file_count="multiple",
            )

            folder_input = gr.File(
                label="选择文件夹（统计图片数量）",
                file_count="directory",
            )

            img_input.change(
                on_image_upload,
                inputs=[img_input, chatbot],
                outputs=[chatbot],
            )

            doc_input.change(
                on_doc_upload,
                inputs=[doc_input, chatbot],
                outputs=[chatbot],
            )

            folder_input.change(
                count_images_in_folder,
                inputs=[folder_input, chatbot],
                outputs=[chatbot],
            )


if __name__ == "__main__":
    # 外网访问
    demo.launch(
        server_name="0.0.0.0",  # 对外监听全部网卡
        server_port=7860,       # 自定义端口，例如 7860
        share=False             # 若想用 Gradio 临时外网链接可改 True
    )

