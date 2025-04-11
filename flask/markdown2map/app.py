from flask import Flask, request, send_from_directory, url_for
import time
import subprocess
import os

app = Flask(__name__)

# 测试根路径
@app.route('/')
def index():
    return "Flask server is running!"

# 上传并处理Markdown文件的路径ForPPT
@app.route('/upload_for_ppt', methods=['POST'])
def upload_markdown_for_ppt():
    content = request.get_data(as_text=True)
    time_name = str(int(time.time()))  # 生成时间戳作为文件名
    md_file_name = time_name + ".md"  # Markdown文件名
    ppt_file_name = time_name + ".pptx"  # HTML文件名

    # 创建markdown和html文件夹，如果它们不存在的话
    os.makedirs('static/md', exist_ok=True)
    os.makedirs('static/ppt', exist_ok=True)

    # 将Markdown内容写入文件
    with open(f'static/md/{md_file_name}', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Markdown file created: static/md/{md_file_name}")
    try:
        return f'Markdown 文件已保存\n预览链接: http://192.168.0.168:8080/{md_file_name} \n下载链接: http://192.168.0.168:8080/{md_file_name}?pptx'
        # return f'Markdown文件已保存. 点击预览: {url_for("get_md", filename=md_file_name, _external=True)}'
    except subprocess.CalledProcessError as e:
        # 如果转换过程中出现错误，返回错误信息
        return f"Error generating HTML file: {e.output}\n{e.stderr}", 500

# 上传并处理Markdown文件的路径
@app.route('/upload', methods=['POST'])
def upload_markdown():
    content = request.get_data(as_text=True)
    time_name = str(int(time.time()))  # 生成时间戳作为文件名
    md_file_name = time_name + ".md"  # Markdown文件名
    html_file_name = time_name + ".html"  # HTML文件名

    # 创建markdown和html文件夹，如果它们不存在的话
    os.makedirs('static/md', exist_ok=True)
    os.makedirs('static/html', exist_ok=True)

    # 将Markdown内容写入文件
    with open(f'static/md/{md_file_name}', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Markdown file created: static/md/{md_file_name}")

    try:
        # 使用subprocess调用markmap-cli将Markdown转换为HTML，并移动到static/html目录
        result = subprocess.run(
            ['npx', 'markmap-cli', f'static/md/{md_file_name}', '--no-open'],
            capture_output=True,
            text=True
        )
        
        print(f"执行转html命令")
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr
            )
        print(f"命令应该是完事了")
        # 尝试将生成的HTML文件移动到static/html文件夹
        os.replace(f'static/md/{html_file_name}', f'static/html/{html_file_name}')
        print(f"HTML file moved to: static/html/{html_file_name}")

        # 返回转换后的HTML文件链接
        return f'思维导图文件已保存. 点击预览: {url_for("get_html", filename=html_file_name, _external=True)}'

    except subprocess.CalledProcessError as e:
        # 如果转换过程中出现错误，返回错误信息
        return f"Error generating HTML file: {e.output}\n{e.stderr}", 500

# 提供HTML文件的路径
@app.route('/html/<filename>')
def get_html(filename):
    return send_from_directory('static/html', filename)

# 提供Md文件的路径
@app.route('/md/<filename>')
def get_md(filename):
    return send_from_directory('static/md', filename)

    # 提供pptx文件的路径
@app.route('/ppt/<filename>')
def get_ppt(filename):
    return send_from_directory('static/ppt', filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5802, debug=True)



    