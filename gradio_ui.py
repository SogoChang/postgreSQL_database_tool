import gradio as gr
import psycopg2
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import signal
import sys
import webbrowser
import threading
import time
import platform

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def upload_json_from_folder(folder_path, host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS json_data (
            id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            json_data JSONB NOT NULL
        );
        """)
        conn.commit()

        json_batch = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                full_path = os.path.join(folder_path, filename)
                with open(full_path, 'r') as f:
                    content = json.load(f)
                    content['file_name'] = filename
                    #content['id'] = filename.replace(".json", "")
                    json_batch.append(content)

        cursor.execute("CALL insert_multiple_json(%s::JSON);", [json.dumps(json_batch)])
        conn.commit()
        msg = f"\n\n✅ 成功匯入 {len(json_batch)} 筆資料。"

    except Exception as e:
        conn.rollback()
        msg = f"❌ 匯入失敗：{str(e)}"

    finally:
        cursor.close()
        conn.close()

    return msg

def plot_pnl_by_id(target_id, host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        cursor = conn.cursor()
        cursor.execute("SELECT get_pnl_by_id(%s);", (target_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or not result[0]:
            raise ValueError("找不到該 ID 或 PnL 為空")

        pnl_list = result[0]

        if len(pnl_list[0]) == 2:
            pnl_df = pd.DataFrame(pnl_list, columns=["date", "pnl"])
        elif len(pnl_list[0]) == 3:
            pnl_df = pd.DataFrame(pnl_list, columns=["date", "pnl_long", "pnl_short"])
            pnl_df = pnl_df.rename(columns={"pnl_long": "pnl"})
        else:
            raise ValueError("不支援的 PnL 資料格式")

        pnl_df["date"] = pd.to_datetime(pnl_df["date"])
        pnl_df = pnl_df.sort_values("date")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pnl_df["date"], pnl_df["pnl"], marker="o", linestyle="-")
        ax.set_title(f"PnL for ID: {target_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("PnL")
        ax.grid(True)
        plt.tight_layout()
        return fig

    except Exception as e:
        return gr.update(value=None), f"❌ 錯誤：{str(e)}"

def filter_ids(min_sharpe, min_fitness, max_turnover, host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM get_ids_by_conditions(%s, %s, %s);", (min_sharpe, min_fitness, max_turnover))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return pd.DataFrame(rows, columns=["id"])

    except Exception as e:
        return pd.DataFrame([[f"❌ 錯誤：{str(e)}"]], columns=["error"])

def stop_gradio():
    def shutdown():
        time.sleep(1)
        if platform.system() == "Windows":
            os.system("taskkill /f /pid " + str(os.getpid()))
        else:
            os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=shutdown).start()
    return "🛑 Gradio UI 即將關閉（瀏覽器頁面將自動終止）..."

with gr.Blocks() as demo:
    gr.Markdown("# 🧠 PostgreSQL JSON 工具介面")

    with gr.Tab("🔑 資料庫設定"):
        host = gr.Textbox(label="Host", value="localhost")
        port = gr.Number(label="Port", value=5432)
        dbname = gr.Textbox(label="Database Name", value="postgres")
        user = gr.Textbox(label="User", value="postgres")
        password = gr.Textbox(label="Password", type="password")

    with gr.Tab("📈 PnL 視覺化"):
        id_input = gr.Textbox(label="輸入 ID")
        plot_button = gr.Button("繪製 PnL")
        plot_output = gr.Plot()
        plot_button.click(plot_pnl_by_id, 
                          inputs=[id_input, host, port, dbname, user, password], 
                          outputs=[plot_output])

    with gr.Tab("📂 資料匯入"):
        folder_input = gr.Textbox(label="輸入 JSON 資料夾路徑")
        upload_button = gr.Button("開始匯入")
        upload_log = gr.Textbox(label="匯入結果")
        upload_button.click(upload_json_from_folder, 
                            inputs=[folder_input, host, port, dbname, user, password], 
                            outputs=[upload_log])

    with gr.Tab("🔍 條件篩選"):
        sharpe_input = gr.Number(label="最低 Sharpe")
        fitness_input = gr.Number(label="最低 Fitness")
        turnover_input = gr.Number(label="最高 Turnover")
        filter_button = gr.Button("查詢符合條件的 ID")
        filter_output = gr.Dataframe(label="符合條件的 ID")
        filter_button.click(filter_ids, 
                            inputs=[sharpe_input, fitness_input, turnover_input, host, port, dbname, user, password], 
                            outputs=[filter_output])

    with gr.Tab("🛑 關閉系統"):
        stop_button = gr.Button("結束 Gradio 伺服器")
        stop_log = gr.Textbox(label="狀態")
        stop_button.click(fn=stop_gradio, inputs=[], outputs=[stop_log])

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:7860")
    demo.launch()
