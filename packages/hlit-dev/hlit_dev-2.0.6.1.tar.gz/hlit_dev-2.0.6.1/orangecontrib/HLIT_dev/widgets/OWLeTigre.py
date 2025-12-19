import os
import sys
import json
import subprocess
import ntpath

from AnyQt.QtWidgets import QApplication, QLabel, QPushButton
from AnyQt.QtCore import pyqtSignal
from Orange.widgets import widget
from AnyQt.QtGui import QTextCursor

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from Orange.widgets.orangecontrib.HLIT_dev.utils import hlit_python_api
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert
else:
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from orangecontrib.HLIT_dev.utils import hlit_python_api
    from orangecontrib.HLIT_dev.remote_server_smb import convert



def data_to_json_str(workflow_id, num_input, col_names, col_types, values, timeout=100000000):
    payload = {
        "workflow_id": workflow_id,
        "timeout": timeout,
        "data": [
            {
                "num_input": num_input,
                "values": [
                    col_names,
                    col_types,
                    values
                ]
            }
        ]
    }
    return json.dumps(payload)


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWLeTigre(widget.OWWidget):
    name = "Le Tigre"
    description = "Pilotage du workflow de recherche documentaire et d'appel LLM"
    icon = "icons/tiger.png"
    category = "AAIT - ALGORITHM"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/tiger.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/ChatbotTigerODM.ui")
    want_control_area = False
    priority = 1089

    label_update = pyqtSignal(QLabel, str)

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(872)
        self.setFixedHeight(620)
        uic.loadUi(self.gui, self)

        self.textEdit_chat.setReadOnly(True)

        # Connect the buttons
        self.btn_send.clicked.connect(lambda: self.run(self.send_request))
        self.btn_folder.clicked.connect(lambda: self.run(self.send_folder))
        self.label_update.connect(self.update_label)

        # Data
        self.thread = None
        self.model = None
        self.store_path = get_local_store_path()


    def run(self, func):
        for button in self.findChildren(QPushButton):
            button.setEnabled(False)
        # Clear error & warning
        self.error("")
        self.warning("")

        # If Thread is already running, interrupt it
        if self.thread is not None:
            if self.thread.isRunning():
                self.thread.safe_quit()

        # Start progress bar
        # self.progressBarInit()

        # Connect and start thread : main function, progress, result and finish
        # --> progress is used in the main function to track progress (with a callback)
        # --> result is used to collect the result from main function
        # --> finish is just an empty signal to indicate that the thread is finished
        self.thread = thread_management.Thread(func)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()


    def send_request(self, progress_callback=None):
        workflow_id = "IFIA_Chatbot"

        request = self.textEdit_request.toPlainText()
        if not request:
            return

        data_chatbot = data_to_json_str(workflow_id=workflow_id,
                                        num_input="chatbotInput2",
                                        col_names=["content", "format"],
                                        col_types=["str", "str"],
                                        values=[[request, ""]])

        # self.btn_send.setEnabled(False)

        text = self.textEdit_chat.toPlainText()
        if text:
            progress_callback(("chat", "\n\n\n\n"))

        # Add the request to the textBrower
        progress_callback(("chat", f"# Vous : {request}"))
        # Prepare for assistant's answer
        progress_callback(("chat", "\n\n"))
        progress_callback(("chat", "# Le Tigre :"))

        # Input POST
        hlit_python_api.post_input_to_workflow(ip_port="127.0.0.1:8000", data=data_chatbot)
        while True:
            response = hlit_python_api.call_output_workflow_unique_2(ip_port="127.0.0.1:8000", workflow_id=workflow_id)
            if response:
                status = response["_statut"]
                if status == "Stream":

                    ########################
                    ##### À REVOIR !!! #####
                    ########################
                    # Chattyboy Streaming Shitshow
                    url = f"http://127.0.0.1:8000/chat/{workflow_id}"
                    full_text = ""
                    cmd = ["curl", "-s", "-N", url]
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        bufsize=0
                    )
                    try:
                        while True:
                            chunk = proc.stdout.read(1024)  # read raw bytes
                            if not chunk:
                                break
                            token = chunk.decode("utf-8", errors="ignore")
                            if "<|im_end|>" in token or "[DONE]" in token:
                                break
                            else:
                                progress_callback(("chat", token))
                            full_text += token
                    finally:
                        proc.stdout.close()
                        proc.wait()
                    ########################
                    ##### À REVOIR !!! #####
                    ########################

                elif status is not None and status != "Finished":
                    # Update status in UI
                    self.label_update.emit(self.label_freeText, status)

                elif status == "Finished":
                    # Finish the call
                    response = hlit_python_api.call_output_workflow_unique_2(ip_port="127.0.0.1:8000",
                                                                             workflow_id=workflow_id)
                    break
                else:
                    # Do nothing while waiting for infos
                    pass







    def send_folder(self):
        workflow_id = "IFIA_Preprocess"
        data_preproc = data_to_json_str(workflow_id=workflow_id,
                                        num_input="chatbotInput1",
                                        col_names=["trigger"],
                                        col_types=["str"],
                                        values=[["Trigger"]])
        hlit_python_api.post_input_to_workflow(ip_port="127.0.0.1:8000", data=data_preproc)
        while True:
            response = hlit_python_api.call_output_workflow_unique_2(ip_port="127.0.0.1:8000", workflow_id=workflow_id)
            if response:
                status = response["_statut"]
                if status == "Finished":
                    data = convert.convert_json_implicite_to_data_table(response["_result"])
                    path = data[0]["path"].value
                    folder_name = ntpath.basename(path)
                    self.label_update.emit(self.label_folder, folder_name)
                    self.label_update.emit(self.label_freeText, "Préparation terminé !")
                    return

                elif status is not None:
                    # Update status in UI
                    self.label_update.emit(self.label_freeText, status)

                else:
                    # Do nothing while waiting for infos
                    pass



    def handle_progress(self, value) -> None:
        button = value[0]
        if button == "chat":
            token = value[1]
            cursor = self.textEdit_chat.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(token)
            self.textEdit_chat.setTextCursor(cursor)
            # Optional: ensure visible scrolling
            self.textEdit_chat.ensureCursorVisible()
            # app.processEvents()  # Force UI update while streaming
        if button == "folder":
            pass
        if button == "model":
            pass

    def handle_result(self, result):
        if result:
            self.label_folder.setText(result)

    def handle_finish(self):
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)

    # def onDeleteWidget(self):
    #     if self.model is not None:
    #         self.model = None
    #     super().onDeleteWidget()

    def post_initialized(self):
        pass


    def update_label(self, label, text):
        print("Updating label with", text)
        label.setText(text)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWLeTigre()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
