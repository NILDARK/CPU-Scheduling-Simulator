import image_rc
from PyQt5 import QtCore, QtGui, QtWidgets,QAxContainer
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import QMessageBox,QApplication,QVBoxLayout,QWidget,QPushButton,QInputDialog
import sys
import test_rc
import fcfs
import sjf
import srtf
import rr
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import socket
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from creds import sender as sender_email,password as sender_pass
import io
sys.path.append('../')
def generateGanttChart(processStats,result,tat,wt,tq=None,filename=None,flag=False):
    end = max(processStats[2])
    x_ticks = [i for i in range(end+1)]
    x_labels = [str(i) for i in x_ticks]
    
    fig,(ax1,ax2,ax3) = plt.subplots(3,1)
    color1 = 'tab:blue'
    color2 = 'tab:orange'
    ax1.set_ylim(0,1)
    for cntr in range(len(processStats[0])):
        if(cntr%2==0):
            facecolors = color1    
        else:
            facecolors = color2
        ax1.broken_barh([(processStats[1][cntr],processStats[3][cntr])], (8,4),facecolors=(facecolors))
        ax1.annotate("P"+str(processStats[0][cntr]), (processStats[1][cntr]+(processStats[3][cntr])/2,10),size=15,ha='center', va="center")
    columns = ('Process ID', 'Arrival Time', 'Burst Time',
		'First Response Time', 'Completion Time','Turn Around Time','Waiting Time','Response Time')
    data = result
    n_rows = len(data)
    y_offset = np.zeros(len(columns))
    cell_text = []
    for row in range(n_rows):
        y_offset = data[row]
        cell_text.append([x for x in y_offset])
    ax1.set_xticks(ticks=x_ticks,labels=x_labels)
    ax1.set_yticks(ticks=[10,20],labels=["",""])
    ax1.set_xlabel("Time (unit time)",font="Georgia",fontsize=14)
    ax1.set_ylabel("Process Id",font="Georgia",fontsize=14)
    ax1.set_title("Gantt Chart",font='Georgia',fontsize=14)
    ax2.axis('off')
    table = ax2.table(cellText=cell_text, colLabels=columns,loc='center',colLoc='center',cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    if(tq!=None):
        ax3.text(0,1,f'Time Quantum: {tq}\nAverage Turn Around Time: {tat}\nAverage Waiting Time: {wt}',ha='left',va='center',fontsize=14)
    else:
        ax3.text(0,1,f'Average Turn Around Time: {tat}\nAverage Waiting Time: {wt}',ha='left',va='center',fontsize=14)
    # ax3.set_axis_off()
    # ax3.axis('tight')
    ax3.axis('off')
    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    fig.set_size_inches(19,17)
    if(flag):
        buf = io.BytesIO()
        plt.savefig(buf,format='png')
        buf.seek(0)
        im = Image.open(buf)
        with io.BytesIO() as output:
            im.save(output, format="png")
            contents = output.getvalue()
        return contents
    
    if(filename!=None):
        if(filename[-4:]!='.png'):
            plt.savefig(filename+'.png',format='png')
        else:
            plt.savefig(filename,format='png')
    else:
        plt.show()
class Ui_Execution_window(QtWidgets.QWidget):
    win = None
    processInfo = []
    processStats = None
    rowCnt = 0
    at = None
    bt = None
    tq = None
    algo = 0
    tq_status = False
    avg_wt = None
    avg_tat = None
    confirm_toggle = 0
    save_flag = None
    result = None
    def getProcessStat(self,output):
        final = []
        pid,at,bt,ct,ft,tat,wt,rt = [],[],[],[],[],[],[],[]
        for process in output:
            pid.append(process[0])
            at.append(process[1])
            bt.append(process[2])
            ft.append(process[3])
            ct.append(process[4])
            tat.append(process[5])
            wt.append(process[6])
            rt.append(process[7])
        return [pid,at,bt,ft,ct,tat,wt,rt]
    def getSaveFlag(self):
        return self.save_flag
    def closeActivePlots(self):
        try:
            plt.close('all')
        except:
            pass
    def errorMsg(self):
        critical_msgbox = QMessageBox()
        critical_msgbox.setIcon(QMessageBox.Critical)
        critical_msgbox.setWindowTitle("Critical Error")
        critical_msgbox.setText("Invalid Input!")
        critical_msgbox.setInformativeText("""\nTime Quantum must be greater than 0 and less than 1000.""")
        critical_msgbox.setStandardButtons(QMessageBox.Ok)
        critical_msgbox.exec_()
    def getProcessInfo(self):
        self.at = self.arrivaltime_input.text()
        self.bt = self.bursttime_input.text()
        if(self.at == "" or self.bt == "" or (not self.at.isnumeric()) or (not self.bt.isnumeric()) or int(self.bt)==0):
            self.arrivaltime_input.clear()
            self.bursttime_input.clear()
            critical_msgbox = QMessageBox()
            critical_msgbox.setIcon(QMessageBox.Critical)
            critical_msgbox.setWindowTitle("Critical Error")
            critical_msgbox.setText("Invalid Input!")
            critical_msgbox.setInformativeText("""\n1. Arrival Time & Burst Time must be Positive\n2. Arrival Time & Burst Time must be Integer\n3. Burst Time must be greater than 0\n4. Input fields must not be empty""")
            critical_msgbox.setStandardButtons(QMessageBox.Ok)
            critical_msgbox.exec_()
            try:
                if(self.algo==3):
                    self.timequantum_input.clear()
            except:
                pass
            return
        if(self.algo==3):
            if(self.tq==None):
                self.tq = (self.timequantum_input.text())
                if(self.tq=="" or (not self.tq.isnumeric()) or int(self.tq)>999):
                    self.errorMsg()
                    self.tq=None
                    self.timequantum_input.clear()
                    return
                else:
                    self.tq = int(self.tq)
                self.timequantum_input.clear()
                self.timequantum_input.setEnabled(False)
        self.processInfo.append([self.at, self.bt])
        self.rowCnt += 1
        self.arrivaltime_input.clear()
        self.bursttime_input.clear()
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(13)
        item_pid = QtWidgets.QTableWidgetItem(str((len(self.processInfo))-1))
        item_pid.setTextAlignment(QtCore.Qt.AlignCenter)
        item_pid.setFont(font)
        item_at = QtWidgets.QTableWidgetItem(self.processInfo[-1][0])
        item_at.setTextAlignment(QtCore.Qt.AlignCenter)
        item_at.setFont(font)
        item_bt = QtWidgets.QTableWidgetItem(self.processInfo[-1][1])
        item_bt.setTextAlignment(QtCore.Qt.AlignCenter)
        item_bt.setFont(font)
        self.input_table.setRowCount(self.input_table.rowCount()+1)
        self.input_table.setItem(self.rowCnt-1, 0, item_pid)
        self.input_table.setItem(self.rowCnt-1, 1, item_at)
        self.input_table.setItem(self.rowCnt-1, 2, item_bt)
        self.processInfo[-1] = list(map(int,self.processInfo[-1]))
        try:
            if(len(self.processInfo)>0):
                self.execute_button.setEnabled(True)
        except:
            pass
    
    def execute(self):
        execute_confirm = QMessageBox()
        execute_confirm.setIcon(QMessageBox.Question)
        execute_confirm.setText('Confirm')
        execute_confirm.setInformativeText('Confirm to execute Algorithm?')
        execute_confirm.setWindowTitle('Confirm')
        execute_confirm.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel)
        confirm_button = execute_confirm.button(QMessageBox.Yes)
        confirm_button.setText('Execute')
        reject_button = execute_confirm.button(QMessageBox.Cancel)
        def execute_command():
            self.confirm_toggle = 1
            execute_confirm.done(1)
        confirm_button.clicked.connect(execute_command)
        response = execute_confirm.exec_()
        if(self.confirm_toggle==0):
            return
        _translate = QtCore.QCoreApplication.translate
        no_of_process = len(self.processInfo)
        if(no_of_process==0):
            return
        newProcesses = []
        for i in range(no_of_process):
            newProcesses.append([i]+self.processInfo[i])
        if(self.algo==0):
            result = fcfs.fcfs(newProcesses)
            self.result = result
            self.processStats=fcfs.getStatsForGanttChart(result)
            
        elif(self.algo==1):
            result = sjf.sjf(newProcesses)
            self.result = result
            self.processStats = sjf.getStatsForGanttChart(result)
        elif(self.algo==2):
            result = srtf.srtf(newProcesses)
            self.processStats = srtf.getStatsForGanttChart(result[1])
            result = result[0]
            self.result = result
        elif(self.algo==3):
            result = rr.rr(newProcesses,self.tq)
            f_time = result[2]
            bt_dict = result[3]
            self.processStats = rr.getStatsForGanttChart(result[1],f_time,bt_dict,self.tq)
            result = result[0]
            self.result = result
        # [pid,at,bt,ft,ct,tat,wt,rt]
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(13)
        self.output_table.setRowCount(no_of_process)
        self.avg_wt = 0
        self.avg_tat = 0
        rowCnt = 0
        for process in result:
            item_pid = QtWidgets.QTableWidgetItem(str(process[0]))
            item_at = QtWidgets.QTableWidgetItem(str(process[1]))
            item_bt = QtWidgets.QTableWidgetItem(str(process[2]))
            item_ft = QtWidgets.QTableWidgetItem(str(process[3]))
            item_ct = QtWidgets.QTableWidgetItem(str(process[4]))
            item_tat = QtWidgets.QTableWidgetItem(str(process[5]))
            item_wt = QtWidgets.QTableWidgetItem(str(process[6]))
            item_rt = QtWidgets.QTableWidgetItem(str(process[7]))
            self.avg_wt+=process[6]
            self.avg_tat+=process[5]
            item_pid.setTextAlignment(QtCore.Qt.AlignCenter)
            item_pid.setFont(font)
            item_at.setTextAlignment(QtCore.Qt.AlignCenter)
            item_at.setFont(font)
            item_bt.setTextAlignment(QtCore.Qt.AlignCenter)
            item_bt.setFont(font)
            item_ct.setTextAlignment(QtCore.Qt.AlignCenter)
            item_ct.setFont(font)
            item_ft.setTextAlignment(QtCore.Qt.AlignCenter)
            item_ft.setFont(font)
            item_wt.setTextAlignment(QtCore.Qt.AlignCenter)
            item_wt.setFont(font)
            item_tat.setTextAlignment(QtCore.Qt.AlignCenter)
            item_tat.setFont(font)
            item_rt.setTextAlignment(QtCore.Qt.AlignCenter)
            item_rt.setFont(font)
            self.output_table.setItem(rowCnt, 0, item_pid)
            self.output_table.setItem(rowCnt, 1, item_at)
            self.output_table.setItem(rowCnt, 2, item_bt)
            self.output_table.setItem(rowCnt, 3, item_ct)
            self.output_table.setItem(rowCnt, 4, item_tat)
            self.output_table.setItem(rowCnt, 5, item_wt)
            self.output_table.setItem(rowCnt, 6, item_ft)
            self.output_table.setItem(rowCnt, 7, item_rt)
            rowCnt+=1
        self.avg_wt = round(self.avg_wt/no_of_process,4)
        self.avg_tat = round(self.avg_tat/no_of_process,4)
        self.result_frame.setEnabled(True)
        self.save_result_frame.setEnabled(True)
        self.awt_result_label.setText(_translate(
            "Execution_window", str(self.avg_wt)))
        self.atat_result_label.setText(_translate(
            "Execution_window", str(self.avg_tat)))
        self.tabWidget.setCurrentIndex(1)
        self.confirm_toggle = 0
        self.save_flag = False
    def resetProcesses(self):
        _translate = QtCore.QCoreApplication.translate
        self.confirm_toggle = 0
        self.input_table.clearContents()
        self.avg_wt = None
        self.avg_tat = None
        self.processInfo = []
        self.processStats = None
        self.tq_status = False
        self.result = None
        self.tq = None
        self.execute_button.setEnabled(False)
        if(self.algo==3):
            self.timequantum_input.setEnabled(True)
        self.rowCnt = 0
        self.input_table.setRowCount(0)
        try:
            self.output_table.clearContents()
            self.output_table.setRowCount(0)
            self.awt_result_label.setText(_translate(
                "Execution_window", "Average Time Result"))
            self.atat_result_label.setText(_translate(
                "Execution_window", "Average Turn Around Time Result"))
            self.result_frame.setEnabled(False)
            self.save_result_frame.setEnabled(False)
        except:
            pass
        self.save_flag = None
        return

    def removeLastProcess(self):
        if(self.input_table.rowCount() == 0):
            return
        self.input_table.removeRow(self.input_table.rowCount()-1)
        self.processInfo.pop(-1)
        if(len(self.processInfo)==0):
            self.execute_button.setEnabled(False)
        self.rowCnt -= 1
        return
    
    def file_save(self):
        name,_ = QtWidgets.QFileDialog.getSaveFileName(self.win, 'Save File')
        if(self.algo==3):
            generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt,tq=self.tq,filename=name)
        else:    
            generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt,filename=name)
        self.save_flag = True
        return
    def showGanttChart(self):
        if(self.algo==3):
            generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt,tq=self.tq)
        else:    
            generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt)
    def is_connected(self):
        try:
            sock = socket.create_connection(("www.google.com", 80))
            if sock is not None:
                sock.close
            return True
        except OSError:
            pass
        return False

    def sendEmail(self):
        internet_connection = self.is_connected()
        if(internet_connection==False):
            critical_msgbox = QMessageBox()
            critical_msgbox.setIcon(QMessageBox.Critical)
            critical_msgbox.setWindowTitle("Critical Error")
            critical_msgbox.setText("No Internet Connection!")
            critical_msgbox.setInformativeText("""Sorry! Your request can not be processed due to no internet.""")
            critical_msgbox.setStandardButtons(QMessageBox.Ok)
            critical_msgbox.exec_()
            return
        if(self.algo==3):
            image_data = generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt,tq=self.tq,flag=True)
        else:    
            image_data = generateGanttChart(self.processStats,self.result,self.avg_tat,self.avg_wt,flag=True)
        inp_dialog = QInputDialog()
        inp_dialog.setInputMode(QInputDialog.TextInput)
        inp_dialog.setLabelText("Enter Your Email: ")
        inp_dialog.setWindowTitle("Email")
        inp_dialog.resize(400,400)
        response = inp_dialog.exec_()
        email_id = inp_dialog.textValue()
        if(response==0):
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = 'Result'
        sender = sender_email
        msg['From'] = sender
        msg['To'] = email_id

        text = MIMEText("Hi There!\nYou may find your result attached below.")
        msg.attach(text)
        image = MIMEImage(image_data, name="Result")
        msg.attach(image)
        try:
            s = smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(sender, sender_pass)
            s.sendmail(sender, email_id, msg.as_string())
            s.quit()
            success_msgbox = QMessageBox()
            success_msgbox.setIcon(QMessageBox.Information)
            success_msgbox.setWindowTitle("Success")
            success_msgbox.setText("Email Sent Sucessfully")
            success_msgbox.setInformativeText("""You may now check your email for the result.""")
            success_msgbox.setStandardButtons(QMessageBox.Ok)
            success_msgbox.exec_()
        except Exception as e:
            # dialog box
            print(e)
            critical_msgbox = QMessageBox()
            critical_msgbox.setIcon(QMessageBox.Critical)
            critical_msgbox.setWindowTitle("Unexpected Error")
            critical_msgbox.setText("Something Went Wrong")
            critical_msgbox.setInformativeText("""This might happen because of\n1. Invalid Email Address\n2. Connection Error\nPlease try again later.""")
            critical_msgbox.setStandardButtons(QMessageBox.Ok)
            critical_msgbox.exec_()
    def setupUi(self, Execution_window, windowName, tq_status,algo):
        Execution_window.setObjectName("Execution_window")
        Execution_window.resize(900, 700)
        self.win = Execution_window
        self.tq_status = tq_status
        self.algo = algo
        self.centralwidget = QtWidgets.QWidget(Execution_window)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.input_tab = QtWidgets.QWidget()
        self.input_tab.setObjectName("input_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.input_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.input_tab)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 610, 427))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.frame_9 = QtWidgets.QFrame(self.frame_6)
        self.frame_9.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_9)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.arrivaltime_label = QtWidgets.QLabel(self.frame_9)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(18)
        self.arrivaltime_label.setFont(font)
        self.arrivaltime_label.setObjectName("arrivaltime_label")
        self.horizontalLayout_3.addWidget(self.arrivaltime_label)
        self.arrivaltime_input = QtWidgets.QLineEdit(self.frame_9)
        self.arrivaltime_input.setObjectName("arrivaltime_input")
        self.horizontalLayout_3.addWidget(self.arrivaltime_input)
        self.verticalLayout_9.addWidget(self.frame_9)
        self.frame_8 = QtWidgets.QFrame(self.frame_6)
        self.frame_8.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bursttime_label = QtWidgets.QLabel(self.frame_8)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(18)
        self.bursttime_label.setFont(font)
        self.bursttime_label.setObjectName("bursttime_label")
        self.horizontalLayout_2.addWidget(self.bursttime_label)
        self.bursttime_input = QtWidgets.QLineEdit(self.frame_8)
        self.bursttime_input.setObjectName("bursttime_input")
        self.horizontalLayout_2.addWidget(self.bursttime_input)
        self.verticalLayout_9.addWidget(self.frame_8)
        self.frame_5 = QtWidgets.QFrame(self.frame_6)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.timequantum_label = QtWidgets.QLabel(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(18)
        self.timequantum_label.setFont(font)
        self.timequantum_label.setTextFormat(QtCore.Qt.AutoText)
        self.timequantum_label.setObjectName("timequantum_label")
        self.horizontalLayout.addWidget(self.timequantum_label)
        self.timequantum_input = QtWidgets.QLineEdit(self.frame_5)
        self.timequantum_input.setEnabled(self.tq_status)
        self.timequantum_input.setObjectName("timequantum_input")
        self.horizontalLayout.addWidget(self.timequantum_input)
        self.verticalLayout_9.addWidget(self.frame_5)
        self.frame_7 = QtWidgets.QFrame(self.frame_6)
        self.frame_7.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.addprocess_button = QtWidgets.QPushButton(self.frame_7)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.addprocess_button.setFont(font)
        self.addprocess_button.setObjectName("addprocess_button")
        self.addprocess_button.setToolTip('Add Process')
        self.addprocess_button.clicked.connect(self.getProcessInfo)
        self.horizontalLayout_4.addWidget(self.addprocess_button)
        self.deleteProcess = QtWidgets.QPushButton(self.frame_7)
        self.deleteProcess.setToolTip('Delete Previous Process')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.deleteProcess.setFont(font)
        self.deleteProcess.setObjectName("deleteProcess")
        self.deleteProcess.clicked.connect(self.removeLastProcess)
        self.horizontalLayout_4.addWidget(self.deleteProcess)
        #
        self.reset = QtWidgets.QPushButton(self.frame_7)
        self.reset.setToolTip('Reset All')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.reset.setFont(font)
        self.reset.setObjectName("reset")
        self.horizontalLayout_4.addWidget(self.reset)
        self.reset.clicked.connect(self.resetProcesses)
        #
        self.execute_button = QtWidgets.QPushButton(self.frame_7)
        self.execute_button.setToolTip('Execute Algorithm')
        self.execute_button.setEnabled(False)
        self.execute_button.clicked.connect(self.execute)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.execute_button.setFont(font)
        self.execute_button.setObjectName("execute_button")
        self.horizontalLayout_4.addWidget(self.execute_button)
        self.verticalLayout_9.addWidget(self.frame_7)
        self.verticalLayout_8.addWidget(self.frame_6)
        self.verticalLayout_5.addWidget(self.frame)
        self.input_table = QtWidgets.QTableWidget(
            self.scrollAreaWidgetContents)
        self.input_table.setMinimumSize(QtCore.QSize(0, 0))
        self.input_table.setStyleSheet("background:#e4e9eb;")
        self.input_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.input_table.setObjectName("input_table")
        self.input_table.setColumnCount(3)
        self.input_table.setRowCount(0)
        self.input_table.verticalHeader().setVisible(False)
        self.input_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.input_table.setDragDropOverwriteMode(False)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.input_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.input_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.input_table.setHorizontalHeaderItem(2, item)
        self.input_table.horizontalHeader().setDefaultSectionSize(618)
        self.verticalLayout_5.addWidget(self.input_table)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.input_tab, "")
        self.output_tab = QtWidgets.QWidget()
        self.output_tab.setObjectName("output_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.output_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.output_tab)
        self.scrollArea_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(
            QtCore.QRect(0, 0, 610, 427))
        self.scrollAreaWidgetContents_2.setObjectName(
            "scrollAreaWidgetContents_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_3 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_2 = QtWidgets.QFrame(self.frame_3)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.output_table = QtWidgets.QTableWidget(self.frame_2)
        self.output_table.setStyleSheet("background:#e4e9eb;")
        self.output_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.output_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.output_table.setObjectName("output_table")
        self.output_table.setColumnCount(8)
        self.output_table.setRowCount(0)
        self.output_table.verticalHeader().setVisible(False)
        self.output_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.output_table.setDragDropOverwriteMode(False)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        item.setBackground(QtGui.QColor(135, 155, 161))
        self.output_table.setHorizontalHeaderItem(7, item)
        self.output_table.horizontalHeader().setDefaultSectionSize(300)
        self.verticalLayout_10.addWidget(self.output_table)
        self.gridLayout.addWidget(self.frame_2, 0, 0, 1, 1)
        self.result_frame = QtWidgets.QFrame(self.frame_3)
        self.result_frame.setEnabled(False)
        self.result_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.result_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.result_frame.setObjectName("result_frame")
        self.verticalLayout_20 = QtWidgets.QVBoxLayout(self.result_frame)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.awt_frame = QtWidgets.QFrame(self.result_frame)
        self.awt_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.awt_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.awt_frame.setObjectName("awt_frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.awt_frame)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.awt_label = QtWidgets.QLabel(self.awt_frame)
        self.awt_label.setObjectName("awt_label")
        self.horizontalLayout_5.addWidget(self.awt_label)
        self.awt_result_label = QtWidgets.QLabel(self.awt_frame)
        self.awt_result_label.setObjectName("awt_result_label")
        self.horizontalLayout_5.addWidget(self.awt_result_label)
        self.verticalLayout_20.addWidget(self.awt_frame)
        self.atat_frame = QtWidgets.QFrame(self.result_frame)
        self.atat_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.atat_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.atat_frame.setObjectName("atat_frame")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.atat_frame)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.atat_label = QtWidgets.QLabel(self.atat_frame)
        self.atat_label.setObjectName("atat_label")
        self.horizontalLayout_8.addWidget(self.atat_label)
        self.atat_result_label = QtWidgets.QLabel(self.atat_frame)
        self.atat_result_label.setObjectName("atat_result_label")
        self.horizontalLayout_8.addWidget(self.atat_result_label)
        self.verticalLayout_20.addWidget(self.atat_frame)
        self.awt_result_label.setStyleSheet("color:#e32b2e;")
        self.atat_result_label.setStyleSheet("color:#e32b2e;")
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(16)
        self.awt_result_label.setFont(font)
        self.atat_result_label.setFont(font)
        self.atat_label.setFont(font)
        self.awt_label.setFont(font)
        self.gridLayout.addWidget(self.result_frame, 1, 0, 1, 1)
        self.verticalLayout_6.addWidget(self.frame_3)
        self.save_result_frame = QtWidgets.QFrame(
            self.scrollAreaWidgetContents_2)
        self.save_result_frame.setEnabled(False)
        self.save_result_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.save_result_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.save_result_frame.setObjectName("save_result_frame")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.save_result_frame)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.save_button = QtWidgets.QPushButton(self.save_result_frame)
        self.save_button.setToolTip('Save Result To My Computer')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout_6.addWidget(self.save_button)
        self.save_button.clicked.connect(self.file_save)
        #
        self.show_chart_button = QtWidgets.QPushButton(self.save_result_frame)
        self.show_chart_button.setToolTip('Show Gantt Chart')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.show_chart_button.setFont(font)
        self.show_chart_button.setObjectName("show_chart_button")
        self.horizontalLayout_6.addWidget(self.show_chart_button)
        self.show_chart_button.clicked.connect(self.showGanttChart)
        #
        self.email_button = QtWidgets.QPushButton(self.save_result_frame)
        self.email_button.setToolTip('Email Me Result')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(14)
        self.email_button.setFont(font)
        self.email_button.setObjectName("email_button")
        self.email_button.clicked.connect(self.sendEmail)
        self.horizontalLayout_6.addWidget(self.email_button)
        self.verticalLayout_6.addWidget(self.save_result_frame)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.addWidget(self.scrollArea_2)
        self.tabWidget.addTab(self.output_tab, "")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(
            QtCore.QRect(0, 0, 610, 427))
        self.scrollAreaWidgetContents_3.setObjectName(
            "scrollAreaWidgetContents_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents_3)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout.addWidget(self.tabWidget)
        Execution_window.setCentralWidget(self.centralwidget)
        self.retranslateUi(Execution_window, windowName)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Execution_window)

    def retranslateUi(self, Execution_window, windowName):
        _translate = QtCore.QCoreApplication.translate
        Execution_window.setWindowTitle(
            _translate("Execution_window", windowName))
        self.tabWidget.setWhatsThis(_translate(
            "Execution_window", "Gantt Chart"))
        self.arrivaltime_label.setText(_translate(
            "Execution_window", "Arrival Time       "))
        self.bursttime_label.setText(_translate(
            "Execution_window", "Burst Time         "))
        self.timequantum_label.setText(_translate(
            "Execution_window", "Time Quantum  "))
        self.addprocess_button.setWhatsThis(
            _translate("Execution_window", "Add Process"))
        self.addprocess_button.setAccessibleName(
            _translate("Execution_window", "Add Process"))
        self.addprocess_button.setText(
            _translate("Execution_window", "Add Process"))
        self.deleteProcess.setWhatsThis(_translate(
            "Execution_window", "Delete Previous Process"))
        self.deleteProcess.setText(_translate(
            "Execution_window", "Delete Previous Process"))
        self.reset.setWhatsThis(_translate("Execution_window", "Reset"))
        self.reset.setText(_translate("Execution_window", "Reset"))
        self.execute_button.setWhatsThis(_translate(
            "Execution_window", "Execute Algorithm"))
        self.execute_button.setText(_translate("Execution_window", "Execute"))
        item = self.input_table.horizontalHeaderItem(0)
        item.setText(_translate("Execution_window", "Process Id"))
        item.setWhatsThis(_translate("Execution_window", "Process Id"))
        item = self.input_table.horizontalHeaderItem(1)
        item.setText(_translate("Execution_window", "Arrival Time"))
        item = self.input_table.horizontalHeaderItem(2)
        item.setText(_translate("Execution_window", "Burst Time"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.input_tab), _translate("Execution_window", "Input"))
        item = self.output_table.horizontalHeaderItem(0)
        item.setText(_translate("Execution_window", "Process Id"))
        item.setWhatsThis(_translate("Execution_window", "Process Id"))
        item = self.output_table.horizontalHeaderItem(1)
        item.setText(_translate("Execution_window", "Arrival Time"))
        item.setWhatsThis(_translate("Execution_window", "Arrival Time"))
        item = self.output_table.horizontalHeaderItem(2)
        item.setText(_translate("Execution_window", "Burst Time"))
        item.setWhatsThis(_translate("Execution_window", "Burst Time"))
        item = self.output_table.horizontalHeaderItem(3)
        item.setText(_translate("Execution_window", "Completion Time (CT)"))
        item.setWhatsThis(_translate("Execution_window", "Completion Time"))
        item = self.output_table.horizontalHeaderItem(4)
        item.setText(_translate("Execution_window", "Turn Around Time (TAT)"))
        item.setWhatsThis(_translate("Execution_window", "Turn Around Time"))
        item = self.output_table.horizontalHeaderItem(5)
        item.setText(_translate("Execution_window", "Waiting Time (WT)"))
        item.setWhatsThis(_translate("Execution_window", "Waiting Time"))
        item = self.output_table.horizontalHeaderItem(6)
        item.setText(_translate("Execution_window", "First Response Time"))
        item.setWhatsThis(_translate(
            "Execution_window", "First Response Time"))
        item = self.output_table.horizontalHeaderItem(7)
        item.setText(_translate("Execution_window", "Response Time"))
        self.awt_label.setText(_translate(
            "Execution_window", "Average Waiting Time"))
        self.atat_label.setText(_translate(
            "Execution_window", "Average Turn Around Time"))
        self.awt_result_label.setText(_translate(
            "Execution_window", "Average Time Result"))
        self.atat_result_label.setText(_translate(
            "Execution_window", "Average Turn Around Time Result"))
        self.save_button.setWhatsThis(_translate(
            "Execution_window", "Save To Device"))
        self.save_button.setText(_translate(
            "Execution_window", "Save Result to Device"))
        self.email_button.setWhatsThis(
            _translate("Execution_window", "Email Result"))
        self.email_button.setText(_translate(
            "Execution_window", "Email Me Result"))
        self.show_chart_button.setText(_translate(
            "Execution_window", "Show Gantt Chart"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.output_tab), _translate("Execution_window", "Output"))
class DocViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(900,900)
        self.setWindowTitle('Developer Documentation')
        self.main_layout = QVBoxLayout(self)
        self.WebBrowser = QAxContainer.QAxWidget(self)
        self.WebBrowser.setFocusPolicy(Qt.StrongFocus)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.main_layout.addWidget(self.WebBrowser)
        self.doc_action()
    def doc_action(self):
        f = 'https://drive.google.com/file/d/1F99Xm_TJfCn_UdzIlYUSw_C-02s138cB/view?usp=sharing'
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)
class About_Us_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.frame)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -60, 603, 966))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.frame_8 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_8)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.textEdit = QtWidgets.QTextEdit(self.frame_8)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_6.addWidget(self.textEdit)
        self.verticalLayout_3.addWidget(self.frame_8)
        self.frame_7 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_7.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.HImage = QtWidgets.QLabel(self.frame_7)
        self.HImage.setText("")
        self.HImage.setPixmap(QtGui.QPixmap(":/newPrefix/H.png"))
        self.HImage.setObjectName("HImage")
        self.horizontalLayout.addWidget(self.HImage)
        self.label_2 = QtWidgets.QLabel(self.frame_7)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("font-size: 13pt;\n"
"font:Georgia;\n"
"")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout_3.addWidget(self.frame_7)
        self.frame_5 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Nimage = QtWidgets.QLabel(self.frame_5)
        self.Nimage.setText("")
        self.Nimage.setPixmap(QtGui.QPixmap(":/newPrefix/N.png"))
        self.Nimage.setObjectName("Nimage")
        self.horizontalLayout_2.addWidget(self.Nimage)
        self.label_3 = QtWidgets.QLabel(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.verticalLayout_3.addWidget(self.frame_5)
        self.frame_4 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.RImage = QtWidgets.QLabel(self.frame_4)
        self.RImage.setText("")
        self.RImage.setPixmap(QtGui.QPixmap(":/newPrefix/R.png"))
        self.RImage.setObjectName("RImage")
        self.horizontalLayout_3.addWidget(self.RImage)
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.verticalLayout_3.addWidget(self.frame_4)
        self.frame_6 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.SImage = QtWidgets.QLabel(self.frame_6)
        self.SImage.setText("")
        self.SImage.setPixmap(QtGui.QPixmap(":/newPrefix/SM.png"))
        self.SImage.setObjectName("SImage")
        self.horizontalLayout_4.addWidget(self.SImage)
        self.label_5 = QtWidgets.QLabel(self.frame_6)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.verticalLayout_3.addWidget(self.frame_6)
        self.frame_3 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.DImage = QtWidgets.QLabel(self.frame_3)
        self.DImage.setText("")
        self.DImage.setPixmap(QtGui.QPixmap(":/newPrefix/D.png"))
        self.DImage.setObjectName("DImage")
        self.horizontalLayout_5.addWidget(self.DImage)
        self.label_6 = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.verticalLayout_3.addWidget(self.frame_3)
        self.frame_2 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.DhImage = QtWidgets.QLabel(self.frame_2)
        self.DhImage.setText("")
        self.DhImage.setPixmap(QtGui.QPixmap(":/newPrefix/Dh.png"))
        self.DhImage.setObjectName("DhImage")
        self.horizontalLayout_6.addWidget(self.DhImage)
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_6.addWidget(self.label_7)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.frame_11 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_11.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_11)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_13 = QtWidgets.QFrame(self.frame_11)
        self.frame_13.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_13.setObjectName("frame_13")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_13)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.frame_13)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(18)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_5.addWidget(self.label_9)
        self.verticalLayout_4.addWidget(self.frame_13)
        self.frame_15 = QtWidgets.QFrame(self.frame_11)
        self.frame_15.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_15.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_15.setObjectName("frame_15")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_15)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.RHJImage = QtWidgets.QLabel(self.frame_15)
        self.RHJImage.setText("")
        self.RHJImage.setPixmap(QtGui.QPixmap(":/newPrefix/rhj.png"))
        self.RHJImage.setObjectName("RHJImage")
        self.horizontalLayout_7.addWidget(self.RHJImage)
        self.label_8 = QtWidgets.QLabel(self.frame_15)
        font = QtGui.QFont()
        font.setFamily("Georgia")
        font.setPointSize(13)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_7.addWidget(self.label_8)
        self.verticalLayout_4.addWidget(self.frame_15)
        self.verticalLayout_3.addWidget(self.frame_11)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Know Our Team"))
        self.label.setText(_translate("MainWindow", "Know Our Team"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt;\">This project Is prepared by 2nd year Computer Science Engineering students from Pandit Deendayal Energy University (PDEU). We have created a desktop GUI which shows implementation of different CPU scheduling algorithms through simulations and Gantt chart. We have used python, PYQT designer and PYQT5 to implement the project. We would like to thank our faculty mentor Dr Rutvij H Jhaveri for his guidance and support throughout the project, and our team mates whose constant effort to achieve excellence made this project possible.</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "Hardik Inani - 20BCP012"))
        self.label_3.setText(_translate("MainWindow", "Nilay Patel - 20BCP005"))
        self.label_4.setText(_translate("MainWindow", "Rahul Gulati - 20BCP024"))
        self.label_5.setText(_translate("MainWindow", "Shrey Makadiya - 20BCP028"))
        self.label_6.setText(_translate("MainWindow", "Drashti Bhavsar - 20BCP040"))
        self.label_7.setText(_translate("MainWindow", "Dhvanil Bhagat - 20BCP027"))
        self.label_9.setText(_translate("MainWindow", "Faculty Mentor"))
        self.label_8.setText(_translate("MainWindow", "Dr Rutvij H Jhaveri"))
class modifiedWindow(QtWidgets.QMainWindow):
    save_flag = None
    ui = None
    def __init__(self,ui):
        super().__init__()
        self.ui = ui
    def closeEvent(self, event):
        try:
            self.save_flag = self.ui.getSaveFlag()
        except:
            event.accept()
            return
        if(self.save_flag==True or self.save_flag==None):
            event.accept()
            return
        exit_msgbox = QMessageBox()
        exit_msgbox.setIcon(QMessageBox.Information)
        exit_msgbox.setText('Save or Close')
        exit_msgbox.setInformativeText('Result generated is not saved!                                      ')
        exit_msgbox.setWindowTitle('Save or Close')
        exit_msgbox.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ignore|QMessageBox.Save)
        cancel_button = exit_msgbox.button(QMessageBox.Cancel)
        ignore_button = exit_msgbox.button(QMessageBox.Ignore)
        cancel_button.setText('Back')
        ignore_button.setText("Ignore and Close")
        response = exit_msgbox.exec_()
        if(response==2048):
            event.accept()
            self.ui.file_save()
            self.ui.resetProcesses()
        elif(response==4194304):
            event.ignore()
        else:
            self.ui.closeActivePlots()
        
class window(QtWidgets.QMainWindow):
    def closeEvent(self,event):
        interface_closing_msgbox = QMessageBox()
        interface_closing_msgbox.setIcon(QMessageBox.Question)
        interface_closing_msgbox.setText('Exit')
        interface_closing_msgbox.setInformativeText("Are you sure you want to exit?")
        interface_closing_msgbox.setWindowTitle('Exit')
        interface_closing_msgbox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        response = interface_closing_msgbox.exec_()
        if(response==16384):
            event.accept()
            sys.exit(0)
        else:
            event.ignore()
           
class Ui_MainWindow(object):    
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.d = DocViewer()
        self.abt_us_win = About_Us_MainWindow()
        
    def instructionPopup(self,flag=False):
        instruction_box = QMessageBox()
        instruction_box.setIcon(QMessageBox.Information)
        instruction_box.setText('Instruction For Valid Input')
        if(flag):
            instruction_box.setInformativeText("""\n1. Time Quantum should be greater than 0 and less than 999.\n2. Time Quantum must be added while adding\n   first process after that time quantum will not change. \n3. Arrival Time & Burst Time must be Positive.\n4. Arrival Time & Burst Time must be Integer.\n5. Burst Time must be greater than 0.\n6. Input fields must not be empty.""")
        else:    
            instruction_box.setInformativeText("""\n1. Arrival Time & Burst Time must be Positive\n2. Arrival Time & Burst Time must be Integer\n3. Burst Time must be greater than 0\n4. Input fields must not be empty""")
        instruction_box.setWindowTitle('Instruction')
        instruction_box.setStandardButtons(QMessageBox.Ok)
        response = instruction_box.exec_()
    def openFCFSWin(self):
        self.ui = Ui_Execution_window()
        self.win = modifiedWindow(self.ui)
        self.ui.setupUi(self.win,"FCFS Simulator",False,0)
        self.ui.resetProcesses()
        self.ui.timequantum_input.setVisible(False)
        self.ui.timequantum_label.setVisible(False)
        self.instructionPopup()
        self.win.show()
    def openDocViewer(self):
        self.doc_obje_creater()
        self.d.show()
    def doc_obje_creater(self):
        self.d = DocViewer()
    def openAbtUsWin(self):
        self.ui = About_Us_MainWindow()
        self.win = modifiedWindow(self.ui)
        self.ui.setupUi(self.win)
        self.win.show()
    def openSJFWin(self):
        self.ui = Ui_Execution_window()
        self.win = modifiedWindow(self.ui)
        self.ui.setupUi(self.win,"SJF Simulator",False,1)
        self.ui.resetProcesses()
        self.ui.timequantum_input.setVisible(False)
        self.ui.timequantum_label.setVisible(False)
        self.instructionPopup()
        self.win.show()
    def openSRTFWin(self):
        self.ui = Ui_Execution_window()
        self.win = modifiedWindow(self.ui)
        self.ui.setupUi(self.win,"SRTF Simulator",False,2)
        self.ui.resetProcesses()
        self.ui.timequantum_input.setVisible(False)
        self.ui.timequantum_label.setVisible(False)
        self.instructionPopup()
        self.win.show()
    def openRRWin(self):
        self.ui = Ui_Execution_window()
        self.win = modifiedWindow(self.ui)
        self.ui.setupUi(self.win,"RR Simulator",True,3)
        self.ui.resetProcesses()
        self.ui.timequantum_input.setVisible(True)
        self.ui.timequantum_label.setVisible(True)
        self.instructionPopup(True)
        self.win.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 900)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setToolTipDuration(1)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.cpu_tab = QtWidgets.QWidget()
        self.cpu_tab.setObjectName("cpu_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.cpu_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cpu_Textbox = QtWidgets.QTextBrowser(self.cpu_tab)
        self.cpu_Textbox.setStyleSheet("")
        self.cpu_Textbox.setObjectName("cpu_Textbox")
        self.verticalLayout_2.addWidget(self.cpu_Textbox)
        self.fcfs_tab = QtWidgets.QWidget()
        self.fcfs_tab.setObjectName("fcfs_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.fcfs_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.fcfs_Textbox = QtWidgets.QTextBrowser(self.fcfs_tab)
        self.fcfs_Textbox.setStyleSheet("")
        self.fcfs_Textbox.setObjectName("fcfs_Textbox")
        self.verticalLayout_3.addWidget(self.fcfs_Textbox)
        self.frame = QtWidgets.QFrame(self.fcfs_tab)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.simulate_fcfs = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        self.simulate_fcfs.setFont(font)
        self.simulate_fcfs.setToolTip('Simulate FCFS Algorithm')
        self.simulate_fcfs.setObjectName("simulate_fcfs")
        self.verticalLayout_7.addWidget(self.simulate_fcfs)
        self.verticalLayout_3.addWidget(self.frame)
        self.simulate_fcfs.clicked.connect(self.openFCFSWin)
        self.tabWidget.addTab(self.cpu_tab, "")
        self.tabWidget.addTab(self.fcfs_tab, "")
        self.sjf_tab = QtWidgets.QWidget()
        self.sjf_tab.setObjectName("sjf_tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.sjf_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.sjf_Textbox = QtWidgets.QTextBrowser(self.sjf_tab)
        self.sjf_Textbox.setObjectName("sjf_Textbox")
        self.verticalLayout_4.addWidget(self.sjf_Textbox)
        self.frame_2 = QtWidgets.QFrame(self.sjf_tab)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.simulate_sjf = QtWidgets.QPushButton(self.frame_2)
        self.simulate_sjf.setToolTip('Simulate SJF Algorithm')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        self.simulate_sjf.setFont(font)
        self.simulate_sjf.setObjectName("simulate_sjf")
        self.verticalLayout_8.addWidget(self.simulate_sjf)
        self.verticalLayout_4.addWidget(self.frame_2)
        self.simulate_sjf.clicked.connect(self.openSJFWin)
        self.tabWidget.addTab(self.sjf_tab, "")
        self.srtf_tab = QtWidgets.QWidget()
        self.srtf_tab.setObjectName("srtf_tab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.srtf_tab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.srtf_Textbox = QtWidgets.QTextBrowser(self.srtf_tab)
        self.srtf_Textbox.setStyleSheet("")
        self.srtf_Textbox.setObjectName("srtf_Textbox")
        self.verticalLayout_5.addWidget(self.srtf_Textbox)
        self.frame_3 = QtWidgets.QFrame(self.srtf_tab)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.simulate_srtf = QtWidgets.QPushButton(self.frame_3)
        self.simulate_srtf.setToolTip('Simulate SRTF Algorithm')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        self.simulate_srtf.setFont(font)
        self.simulate_srtf.setObjectName("simulate_srtf")
        self.verticalLayout_9.addWidget(self.simulate_srtf)
        self.verticalLayout_5.addWidget(self.frame_3)
        self.simulate_srtf.clicked.connect(self.openSRTFWin)
        self.tabWidget.addTab(self.srtf_tab, "")
        self.rr_tab = QtWidgets.QWidget()
        self.rr_tab.setObjectName("rr_tab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.rr_tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.rr_Textbox = QtWidgets.QTextBrowser(self.rr_tab)
        self.rr_Textbox.setStyleSheet("")
        self.rr_Textbox.setObjectName("rr_Textbox")
        self.verticalLayout_6.addWidget(self.rr_Textbox)
        self.frame_4 = QtWidgets.QFrame(self.rr_tab)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.simulate_rr = QtWidgets.QPushButton(self.frame_4)
        self.simulate_rr.setToolTip('Simulate RR Algorithm')
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(12)
        self.simulate_rr.setFont(font)
        self.simulate_rr.setObjectName("simulate_rr")
        self.verticalLayout_10.addWidget(self.simulate_rr)
        self.simulate_rr.clicked.connect(self.openRRWin)
        self.verticalLayout_6.addWidget(self.frame_4)
        self.tabWidget.addTab(self.rr_tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 628, 18))
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.menuAlgorithms = QtWidgets.QMenu(self.menubar)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.menuAlgorithms.setFont(font)
        self.menuAlgorithms.setObjectName("menuAlgorithms")
        self.menuNon_Pre_emptive = QtWidgets.QMenu(self.menuAlgorithms)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.menuNon_Pre_emptive.setFont(font)
        self.menuNon_Pre_emptive.setObjectName("menuNon_Pre_emptive")
        self.menuPre_emptive = QtWidgets.QMenu(self.menuAlgorithms)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.menuPre_emptive.setFont(font)
        self.menuPre_emptive.setObjectName("menuPre_emptive")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.menuHelp.setFont(font)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.actionDeveloper_Documentation = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.actionDeveloper_Documentation.setFont(font)
        self.actionDeveloper_Documentation.setObjectName(
            "actionDeveloper_Documentation")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.actionAbout.setFont(font)
        self.actionAbout.setObjectName("actionAbout")
        self.actionFirst_Come_First_Serve_FCFS = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.actionFirst_Come_First_Serve_FCFS.setFont(font)
        self.actionFirst_Come_First_Serve_FCFS.setObjectName(
            "actionFirst_Come_First_Serve_FCFS")
        self.actionFirst_Come_First_Serve_FCFS.triggered.connect(
            self.openFCFSWin)
        self.actionShortest_Remaining_Job_First_SRTF = QtWidgets.QAction(
            MainWindow)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(10)
        self.actionShortest_Remaining_Job_First_SRTF.setFont(font)
        self.actionShortest_Remaining_Job_First_SRTF.setObjectName(
            "actionShortest_Remaining_Job_First_SRTF")
        self.actionShortest_Remaining_Job_First_SRTF.triggered.connect(
            self.openSRTFWin)
        self.actionRound_Robin_RR = QtWidgets.QAction(MainWindow)
        self.actionRound_Robin_RR.setObjectName("actionRound_Robin_RR")
        self.actionRound_Robin_RR.triggered.connect(self.openRRWin)
        self.actionShortest_Job_First_SJF = QtWidgets.QAction(MainWindow)
        self.actionShortest_Job_First_SJF.setObjectName(
            "actionShortest_Job_First_SJF")
        self.actionShortest_Job_First_SJF.triggered.connect(self.openSJFWin)
        self.menuNon_Pre_emptive.addAction(
            self.actionFirst_Come_First_Serve_FCFS)
        self.menuNon_Pre_emptive.addAction(self.actionShortest_Job_First_SJF)
        self.menuPre_emptive.addAction(
            self.actionShortest_Remaining_Job_First_SRTF)
        self.menuPre_emptive.addAction(self.actionRound_Robin_RR)
        self.menuAlgorithms.addAction(self.menuNon_Pre_emptive.menuAction())
        self.menuAlgorithms.addAction(self.menuPre_emptive.menuAction())
        self.actionDeveloper_Documentation.triggered.connect(self.openDocViewer)
        self.actionAbout.triggered.connect(self.openAbtUsWin)
        self.menuHelp.addAction(self.actionDeveloper_Documentation)
        self.menuHelp.addAction(self.actionAbout)
        # self.menubar.addAction(self.menuhome.menuAction())
        self.menubar.addAction(self.menuAlgorithms.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "CPU Scheduling Simulator"))
        self.tabWidget.setToolTip(_translate("MainWindow", "Simulate SJF"))
        self.tabWidget.setWhatsThis(_translate("MainWindow", "Simulate SRTF"))
        self.cpu_Textbox.setHtml(_translate("MainWindow", 
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Garamond\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">What is CPU Scheduling?</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">CPU Scheduling is a process of determining which process will own CPU for execution while another process is on hold. The main task of CPU scheduling is to make sure that whenever the CPU remains idle, the OS at least select one of the processes available in the ready queue for execution. The selection process will be carried out by the CPU scheduler. It selects one of the processes in memory that are ready for execution.</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Types of CPU Scheduling</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here are two kinds of Scheduling methods:</span><span style=\" font-size:14pt; color:#1a1a1a;\"> </span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 1.06.25 AM.png\" /></p>\n"
                                            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'.AppleSystemUIFont\'; font-size:14pt; background-color:#ffffff;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Preemptive Scheduling</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">In Preemptive Scheduling, the tasks are mostly assigned with their priorities. Sometimes it is important to run a task with a higher priority before another lower priority task, even if the lower priority task is still running. The lower priority task holds for some time and resumes when the higher priority task finishes its execution.</span></p>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Non-Preemptive Scheduling</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">In this type of scheduling method, the CPU has been allocated to a specific process. The process that keeps the CPU busy will release the CPU either by switching context or terminating. It is the only method that can be used for various hardware platforms. That’s because it doesn’t need special hardware (for example, a timer) like preemptive scheduling.</span></p>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">When scheduling is Preemptive or Non-Preemptive?</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">To determine if scheduling is preemptive or non-preemptive, consider these four parameters:</span></p>\n"
                                            "<ol style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">A process switches from the running to the waiting state.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Specific process switches from the running state to the ready state.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Specific process switches from the waiting state to the ready state.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Process finished its execution and terminated.</span></li></ol>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Only conditions 1 and 4 apply, the scheduling is called non-preemptive.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">All other scheduling is preemptive.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Important CPU scheduling Terminologies</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Burst Time/Execution Time: It is the time required by the process to complete execution. It is also called running time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Arrival Time: when a process enters in a ready state</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Finish Time: when process is complete and exit from a system</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Multiprogramming: Several programs that can be present in memory at the same time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Jobs: It is a type of program without any kind of user interaction.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">User: It is a kind of program having user interaction.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Process: It is the reference that is used for both job and user.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">CPU/IO burst cycle Characterizes process execution, which alternates between CPU and I/O activity. CPU times are usually shorter than the time of I/O.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">CPU Scheduling Criteria</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">A CPU scheduling algorithm tries to maximize and minimize the following:</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 1.06.56 AM.png\" /></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Maximize:</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">CPU utilization: CPU utilization is the main task in which the operating system needs to make sure that the CPU remains as busy as possible. It can range from 0 to 100 per cent. However, for the RTOS, it can be range from 40 per cent for low-level and 90 per cent for high-level systems.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Throughput: The number of processes that finish their execution per unit time is known Throughput. So, when the CPU is busy executing the process, at that time, work is being done, and the work completed per unit time is called Throughput.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Minimize:</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Waiting time: Waiting time is an amount that a specific process needs to wait in the ready queue.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Response time: It is the amount of time in which the request was submitted until the first response is produced.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Turnaround Time: Turnaround time is the amount of time to execute a specific process. It is the calculation of the total time spent waiting to get into the memory, waiting in the queue and, executing on the CPU. The period between the time of process submission to the completion time is the turnaround time.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Interval Timer</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Timer interruption is a method that is closely related to preemption. When a certain process gets the CPU allocation, a timer may be set to a specified interval. Both timer interruption and preemption force a process to return the CPU before its CPU burst is complete.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">The most multi-programmed operating system uses some form of a timer to prevent a process from tying up the system forever.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">What is Dispatcher?</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">It is a module that provides control of the CPU to the process. The Dispatcher should be fast so that it can run on every context switch. Dispatch latency is the amount of time needed by the CPU scheduler to stop one process and start another.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Functions performed by Dispatcher:</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Context Switching</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Switching to user mode</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Moving to the correct location in the newly loaded program.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a;\"><br /></span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Types of CPU scheduling Algorithm</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">There are mainly six types of process scheduling algorithms</span></p>\n"
                                            "<ol style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">First Come First Serve (FCFS)</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Shortest-Job-First (SJF) Scheduling</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Shortest Remaining Time</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Priority Scheduling</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round Robin Scheduling</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Multilevel Queue Scheduling</span></li></ol>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a;\"><br /></span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Scheduling Algorithms</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a;\"><br /></span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">The Purpose of using a Scheduling algorithm :</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The CPU uses scheduling to improve its efficiency.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It helps you to allocate resources among competing processes.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The maximum utilization of the CPU can be obtained with multi-programming.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The processes which are to be executed are in the ready queue.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Summary:</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">CPU scheduling is a process of determining which process will own CPU for execution while another process is on hold.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In Preemptive Scheduling, the tasks are mostly assigned with their priorities.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In the Non-preemptive scheduling method, the CPU has been allocated to a specific process.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The burst time is the time required for the process to complete execution. It is also called running time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">CPU utilization is the main task in which the operating system needs to ensure that the CPU remains as busy as possible.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The number of processes that finish their execution per unit time is known Throughput.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Waiting time is an amount that a specific process needs to wait in the ready queue.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is the amount of time in which the request was submitted until the first response is produced.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Turnaround time is the amount of time to execute a specific process.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Timer interruption is a method that is closely related to preemption.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">A dispatcher is a module that provides control of the CPU to the process.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Six types of process scheduling algorithms are: </span></li>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">1) First Come First Serve (FCFS), </span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">2) Shortest-Job-First (SJF) Scheduling,</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">3) Shortest Remaining Time, </span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">4) Priority Scheduling, </span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">5) Round Robin Scheduling,</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">6) Multilevel Queue Scheduling.</span></p>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In the First Come First Serve method, the process which requests the CPU gets the CPU allocation first.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In the Shortest Remaining time, the process will be allocated to the task closest to its completion.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In Priority Scheduling, the scheduler selects the tasks to work as per the priority.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin scheduling works on the principle that each person gets an equal share of something in turn.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In the Shortest job first, the shortest execution time should be selected for execution next.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The multilevel scheduling method separates the ready queue into various separate queues. In this method, processes are assigned to a queue based on a specific property.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The CPU uses scheduling to improve its efficiency.</span> </li></ul></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.cpu_tab), _translate("MainWindow", "CPU Scheduling"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(
            self.cpu_tab), _translate("MainWindow", "CPU Scheduling Algorithms"))
        self.fcfs_Textbox.setHtml(_translate("MainWindow", 
                                             "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                             "p, li { white-space: pre-wrap; }\n"
                                             "</style></head><body style=\" font-family:\'Garamond\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:10px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">What is First Come First Serve Method?</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">First Come First Serve (FCFS)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> is an operating system scheduling algorithm that automatically executes queued requests and processes in order of their arrival. It is the easiest and simplest CPU scheduling algorithm. In this type of algorithm, processes which request the CPU first get the CPU allocation. This is managed with a FIFO queue. The full form of FCFS is First Come First Serve.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a;\">As the process enters the ready queue, its PCB (Process Control Block) is linked with the tail of the queue and, when the CPU becomes free, it should be assigned to the process at the beginning of the queue.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; color:#000000;\"><br /></span></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Characteristics of FCFS method</span></p>\n"
                                             "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:18pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">It supports non-preemptive and pre-emptive scheduling algorithms.</span></li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Jobs are always executed on a first-come, first-serve basis.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is easy to implement and use.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This method is poor in performance, and the general wait time is quite high.</li></ul>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Example of FCFS scheduling</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a;\">A real-life example of the FCFS method is buying a movie ticket on the ticket counter. In this scheduling algorithm, a person is served according to the queue manner. The person who arrives first in the queue buys the ticket and then the next one. This will continue until the last person in the queue purchases the ticket. Using this algorithm, the CPU process works similarly.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; color:#1a1a1a;\"><br /></span></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Advantages of FCFS</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a;\">Here, are the pros/benefits of using the FCFS scheduling algorithm:</span></p>\n"
                                             "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The simplest form of a CPU scheduling algorithm </li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Easy to program </li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">First come first served </li></ul>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">How does FCFS Work? Calculating Average Waiting Time</span><span style=\" font-size:18pt;   color:#1a1a1a;\"> </span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a;\">Here is an example of five processes arriving at different times. Each process has a different burst time.</span></p>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#1a1a1a;\"><br /></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/images/Screenshot 2022-02-24 at 1.26.30 PM.png\" /><span style=\" color:#1a1a1a;\"> </span></p>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#1a1a1a;\"><br /></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#1a1a1a;\"> </span><span style=\" font-size:14pt; color:#1a1a1a;\">the FCFS scheduling algorithm, these processes are handled as follows.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 0)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> The process begins with P4, with an arrival time of 0.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 1)</span><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"> At time=1, P3 arrives. P4 is still executing. Hence, P3 is kept in a queue.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 2)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time= 2, P1 arrives which is kept in the queue.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 3)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time=3, the P4 process completes its execution.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 4)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time=4, P3, which is first in the queue, starts execution.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 5)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time =5, P2 arrives and is kept in a queue.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 6)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time 11, P3 completes its execution.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 7)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time=11, P1 starts execution. It has a burst time of 6. It completes execution at time interval 17.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 8)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time=17, P5 starts execution. It has a burst time of 4. It completes execution at time=21.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 9)</span><span style=\" font-size:14pt; color:#1a1a1a;\"> At time=21, P2 starts execution. It has a burst time of 2. It completes execution at time interval 23.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; font-weight:600; color:#1a1a1a;\">Step 10) </span><span style=\" font-size:14pt; color:#1a1a1a;\">Let’s calculate the average waiting time for the above example.</span></p>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-24 at 11.40.11 AM-2.png\" /></p>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'.AppleSystemUIFont\'; font-size:14pt; background-color:#ffffff;\"><br /></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a;\"> </span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Waiting time = Start time - Arrival time</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">P4 = 0-0 = 0</span><span style=\" font-size:14pt; color:#1a1a1a;\"> </span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">P3 = 3-1 = 2</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">PI = 11-2 = 9</span><span style=\" font-size:14pt; color:#1a1a1a;\"> </span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">P5= 17-4 = 12</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">P2= 21-5= 16</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Average Waiting Time</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">=0+29+12+15/5</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">= 40/5= 8</span></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Advantages of FCFS</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here, are the pros/benefits of using the FCFS scheduling algorithm:</span></p>\n"
                                             "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The simplest form of a CPU scheduling algorithm </span></li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Easy to program </span></li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">First come first served </span></li></ul>\n"
                                             "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Disadvantages of FCFS</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#1a1a1a;\">Here, are the cons/ drawbacks of using the FCFS scheduling algorithm:</span></p>\n"
                                             "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is a Non-Preemptive CPU scheduling algorithm, so after the process has been allocated to the CPU, it will never release the CPU until it finishes executing. </li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Average Waiting Time is high.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Short processes that are at the back of the queue have to wait for the long process at the front to finish.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Not an ideal technique for time-sharing systems.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Because of its simplicity, FCFS is not very efficient.</li></ul>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Summary</span></p>\n"
                                             "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Definition: FCFS is an operating system scheduling algorithm that automatically executes queued requests and processes by order of their arrival</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It supports non-preemptive and pre-emptive scheduling </li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">algorithm.</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">FCFS stands for First Come First Serve</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A real-life example of the FCFS method is buying a movie ticket on the ticket counter. </li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is the simplest form of a CPU scheduling algorithm</li>\n"
                                             "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is a Non-Preemptive CPU scheduling algorithm, so after the process has been allocated to the CPU, it will never release the CPU until it finishes executing. </li></ul></body></html>"))
        self.simulate_fcfs.setWhatsThis(
            _translate("MainWindow", "Simulate FCFS"))
        self.simulate_fcfs.setText(_translate(
            "MainWindow", "Simulate First Come First Serve (FCFS) Algorithm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.fcfs_tab), _translate("MainWindow", "FCFS"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(
            self.fcfs_tab), _translate("MainWindow", "First Come First Serve"))
        self.sjf_Textbox.setHtml(_translate("MainWindow", 
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Garamond\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">What is Shortest Job First Scheduling?</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Shortest Job First (SJF) is an algorithm in which the process having the smallest execution time is chosen for the next execution. This scheduling method can be preemptive or non-preemptive. It significantly reduces the average waiting time for other processes awaiting execution. The full form of SJF is Shortest Job First.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">There are two types of SJF methods:</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Non-Preemptive SJF</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Preemptive SJF</span></li></ul>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a;\"><br /></span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Characteristics of SJF Scheduling</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is associated with each job as a unit of time to complete.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This algorithm method is helpful for batch-type processing, where we’re waiting for jobs to be complete is not critical.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It can improve process throughput by making sure that shorter jobs are executed first, hence possibly having to have a short turnaround time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It improves job output by offering shorter jobs, which should be executed first, which mostly have a shorter turnaround time.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Non-Preemptive SJF</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">In non-preemptive scheduling, once the CPU cycle is allocated to process, the process holds it till it reaches a waiting state or is terminated.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Consider the following five processes each having its own unique burst time and arrival time.</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.55.26 AM.png\" /></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 0) At time=0, P4 arrives and starts execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 1) At time= 1, Process P3 arrives. But, P4 still needs 2 execution units to complete. It will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 2) At time =2, process P1 arrives and is added to the waiting queue. P4 will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 3) At time = 3, process P4 will finish its execution. The burst time of P3 and P1 is compared. Process P1 is executed because its burst time is less compared to P3.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 4) At time = 4, process P5 arrives and is added to the waiting queue. P1 will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 5) At time = 5, process P2 arrives and is added to the waiting queue. P1 will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 6) At time = 9, process P1 will finish its execution. The burst time of P3, P5, and P2 is compared. Process P2 is executed because its burst time is the lowest.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 7) At time=10, P2 is executing and P3 and P5 are in the waiting queue.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 8) At time = 11, process P2 will finish its execution. The burst time of P3 and P5 is compared. Process P5 is executed because its burst time is lower.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 9) At time = 15, process P5 will finish its execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 10) At time = 23, process P3 will finish its execution.</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.54.37 AM.png\" /></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 11) Let’s calculate the average waiting time for the above example.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">Wait time </span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P4= 0-0=0</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P1=  3-2=1</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P2= 9-5=4</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P5= 11-4=7</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P3= 15-1=12</span></p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">Average Waiting Time= 0+1+4+7+12/5 = 26/5 = 5.2</span><span style=\" font-family:\'.AppleSystemUIFont\'; font-size:14pt;\"> </span></p>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Preemptive SJF</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">In Preemptive SJF Scheduling, jobs are put into the ready queue as they come. A process with the shortest burst time begins execution. If a process with even a shorter burst time arrives, the current process is removed or preempted from execution, and the shorter job is allocated CPU cycle.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Consider the following five processes:</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.51.30 AM.png\" /></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 0) At time=0, P4 arrives and starts execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 1) At time= 1, Process P3 arrives. But, P4 has a shorter burst time. It will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 2) At time = 2, process P1 arrives with burst time = 6. The burst time is more than that of P4. Hence, P4 will continue execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 3) At time = 3, process P4 will finish its execution. The burst time of P3 and P1 is compared. Process P1 is executed because its burst time is lower.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 4) At time = 4, process P5 will arrive. The burst time of P3, P5, and P1 is compared. Process P5 is executed because its burst time is the lowest. Process P1 is preempted.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 5) At time = 5, process P2 will arrive. The burst time of P1, P2, P3, and P5 is compared. Process P2 is executed because its burst time is the least. Process P5 is preempted.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 6) At time =6, P2 is executing.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 7) At time =7, P2 finishes its execution. The burst time of P1, P3, and P5 is compared. Process P5 is executed because its burst time is lesser.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 8) At time =10, P5 will finish its execution. The burst time of P1 and P3 is compared. Process P1 is executed because its burst time is less.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 9) At time =15, P1 finishes its execution. P3 is the only process left. It will start execution.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 10) At time =23, P3 finishes its execution.</span></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.51.01 AM.png\" /></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 11) Let’s calculate the average waiting time for the above example.</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">Wait time </span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P4= 0-0=0</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P1=  (3-2) + 6 =7</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P2= 5-5 = 0</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P5= 4-4+2 =2</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">P3= 15-1 = 12</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#000000;\">Average Waiting Time = 0+7+0+2+12/5 = 23/5 =4.6</span><span style=\" font-family:\'.AppleSystemUIFont\'; font-size:14pt;\"> </span></p>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'.AppleSystemUIFont\'; font-size:14pt; background-color:#ffffff;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Advantages of SJF</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here are the benefits/pros of using the SJF method:</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF is frequently used for long term scheduling.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It reduces the average waiting time over FIFO (First in First Out) algorithm.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF method gives the lowest average waiting time for a specific set of processes.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is appropriate for the jobs running in batch, where run times are known in advance.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">For the batch system of long-term scheduling, a burst time estimate can be obtained from the job description.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">For Short-Term Scheduling, we need to predict the value of the next burst time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Probably optimal about average turnaround time.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Disadvantages/Cons of SJF</span></p>\n"
                                            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here are some drawbacks/cons of the SJF algorithm:</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Job completion time must be known earlier, but it is hard to predict.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is often used in a batch system for long term scheduling.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF can’t be implemented for CPU scheduling for the short term. It is because there is no specific method to predict the length of the upcoming CPU burst.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This algorithm may cause very long turnaround times or starvation.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Requires knowledge of how long a process or job will run.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It leads to starvation that does not reduce the average turnaround time.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is hard to know the length of the upcoming CPU request.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Elapsed time should be recorded, which results in more overhead on the processor.</span></li></ul>\n"
                                            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a; background-color:#ffffff;\">Summary</span></p>\n"
                                            "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF is an algorithm in which the process having the smallest execution time is chosen for the next execution.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF Scheduling is associated with each job as a unit of time to complete.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This algorithm method is helpful for batch-type processing, were waiting for jobs to complete is not critical.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">There are two types of SJF methods 1) Non-Preemptive SJF and 2) Preemptive SJF.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In non-preemptive scheduling, once the CPU cycle is allocated to process, the process holds it till it reaches a waiting state or is terminated.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In Preemptive SJF Scheduling, jobs are put into the ready queue as they come.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Although a process with a short burst time begins, the current process is removed or preempted from execution, and the shorter job is executed 1st.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF is frequently used for long term scheduling.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It reduces the average waiting time over FIFO (First in First Out) algorithm.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">In SJF scheduling, Job completion time must be known earlier, but it is hard to predict.</span></li>\n"
                                            "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">SJF can’t be implemented for CPU scheduling for the short term. It is because there is no specific method to predict the length of the upcoming CPU burst.</span> </li></ul></body></html>"))
        self.simulate_sjf.setWhatsThis(
            _translate("MainWindow", "Simulate SJF"))
        self.simulate_sjf.setText(_translate(
            "MainWindow", "Simulate Shortest Job First (SJF) Algorithm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.sjf_tab), _translate("MainWindow", "SJF"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(
            self.sjf_tab), _translate("MainWindow", "Shortest Job First"))#
        self.srtf_Textbox.setHtml(_translate("MainWindow", 
                                             "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                             "p, li { white-space: pre-wrap; }\n"
                                             "</style></head><body style=\" font-family:\'Garamond\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600; font-style:normal; color:#000000;\">What is Shortest Remaining Time First (SRTF) Scheduling Algorithm?</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">This Algorithm is the preemptive version of SJF scheduling. In SRTF, the execution of the process can be stopped after a certain amount of time. At the arrival of every process, the short term scheduler schedules the process with the least remaining burst time among the list of available processes and the running process.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">Once all the processes are available in the ready queue, No preemption will be done and the algorithm will work as SJF scheduling. The context of the process is saved in the Process Control Block when the process is removed from the execution and the next process is scheduled. This PCB is accessed on the next execution of this process. </span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#333333;\">Example</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">In this example, there are five jobs P1, P2, P3, P4, P5 and P6. Their arrival time and burst time are given below in the table.</span></p>\n"
                                             "<p align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"> </span><img src=\":/images/Screenshot 2022-02-24 at 12.03.56 PM.png\" /></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">Avg Waiting Time = 24/6</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">The Gantt chart is prepared according to the arrival and burst time given in the table.</span></p>\n"
                                             "<ol style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Since, at time 0, the only available process in P1 with CPU burst time 8. This is the only available process on the list therefore it is scheduled. </li>\n"
                                             "<li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The next process arrives at time unit 1. Since the algorithm we are using is SRTF which is a preemptive one, the current execution is stopped and the scheduler checks for the process with the least burst time.<br />Till now, there are two processes available in the ready queue. The OS has executed P1 for one unit of time till now; the remaining burst time of P1 is 7 units. The burst time of Process P2 is 4 units. Hence Process P2 is scheduled on the CPU according to the algorithm. </li>\n"
                                             "<li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The next process P3 arrives at time unit 2. At this time, the execution of process P3 is stopped and the process with the least remaining burst time is searched. Since the process P3 has 2 units of burst time hence it will be given priority over others.</li>\n"
                                             "<li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Next Process P4 arrives at time unit 3. At this arrival, the scheduler will stop the execution of P4 and check which process is having the least burst time among the available processes (P1, P2, P3 and P4). P1 and P2 are having the remaining burst time of 7 units and 3 units respectively. </li>\n"
                                             "<li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">P3 and P4 are having the remaining burst time of 1 unit each. Since both are equal hence the scheduling will be done according to their arrival time. P3 arrives earlier than P4 and therefore it will be scheduled again. The Next Process P5 arrives at time unit 4. Till this time, Process P3 has completed its execution and it is no more on the list. The scheduler will compare the remaining burst time of all the available processes. Since the burst time of the process, P4 is 1 which is the least among all hence this will be scheduled. </li>\n"
                                             "<li style=\" font-size:14pt; color:#000000;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Next Process P6 arrives at time unit 5, till this time, the Process P4 has completed its execution. We have 4 available processes till now, that are P1 (7), P2 (3), P5 (3) and P6 (2). The Burst time of P6 is the least among all hence P6 is scheduled. Since, now, all the processes are available hence the algorithm will now work the same as SJF. P6 will be executed till its completion and then the process with the least remaining time will be scheduled.</li></ol>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\">Once all the processes arrive, No preemption is done and the algorithm will work as SJF.</span></p>\n"
                                             "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#262626;\"><br /></span></p></body></html>"))
        self.simulate_srtf.setText(_translate(
            "MainWindow", "Simulate Shortest Remaining Time First (SRTF) Algorithm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.srtf_tab), _translate("MainWindow", "SRTF"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(
            self.srtf_tab), _translate("MainWindow", "Shortest Remaining Job First"))
        self.rr_Textbox.setHtml(_translate("MainWindow", 
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Garamond\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">What is Round-Robin Scheduling?</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">The name of this algorithm comes from the round-robin principle, where each person gets an equal share of something in turns. It is the oldest, simplest scheduling algorithm, which is mostly used for multitasking.</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">In Round-robin scheduling, each ready task runs turn by turn only in a cyclic queue for a limited time slice. This algorithm also offers starvation free execution of processes.</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"><br /></span></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Characteristics of Round-Robin Scheduling</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here are the important characteristics of Round-Robin Scheduling:</span></p>\n"
                                           "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin is a pre-emptive algorithm</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The CPU is shifted to the next process after fixed interval time, which is called time quantum/time slice.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The process that is preempted is added to the end of the queue.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin is a hybrid model which is clock-driven</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Time slice should be minimum, which is assigned for a specific task that needs to be processed. However, it may differ from OS to OS.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It is a real-time algorithm that responds to the event within a specific time limit.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin is one of the oldest, fairest, and easiest algorithms.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Widely used scheduling method in traditional OS.</span></li></ul>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#000000;\"><br /></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Example of Round-Robin Scheduling</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Consider the following three processes :</span></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.12.40 AM.png\" /></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 1) The execution begins with process P1, which has burst time 4. Here, every process executes for 2 seconds. P2 and P3 are still in the waiting queue.</span></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 2) At time =2, P1 is added to the end of the Queue and P2 starts executing.</span></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 3) At time=4, P2 is preempted and added at the end of the queue. P3 starts executing.</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 4) At time=6, P3 is preempted and added at the end of the queue. P1 starts executing</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 5) At time=8, P1 has a burst time of 4. It has completed execution. P2 starts execution.</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 6) P2 has a burst time of 3. It has already been executed for 2 intervals. At time=9, P2 completes execution. Then, P3 starts execution till it completes.</span></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><img src=\":/images/Screenshot 2022-02-25 at 12.18.45 AM.png\" /></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:21px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Step 7) Let’s calculate the average waiting time for the above example.</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#e9eff5;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#e9eff5;\">Wait time</span><span style=\" font-size:14pt; color:#1a1a1a;\"> </span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#e9eff5;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#e9eff5;\">P1= 0+ 4= 4</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#e9eff5;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#e9eff5;\">P2= 2+4= 6</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#e9eff5;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#e9eff5;\">P3= 4+3= 7</span><span style=\" font-family:\'.AppleSystemUIFont\'; font-size:14pt;\"> </span></p>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#1a1a1a; background-color:#ffffff;\"><br /></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"><br /></span></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Advantage of Round-Robin Scheduling</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here, are the pros/benefits of the Round-Robin scheduling method:</span></p>\n"
                                           "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It doesn’t face the issues of starvation or convoy effect.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">All the jobs get a fair allocation of CPU.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It deals with all processes without any priority</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">If you know the total number of processes on the run queue, then you can also assume the worst-case response time for the same process.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This scheduling method does not depend upon burst time. That’s why it is easily implementable on the system.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Once a process is executed for a specific set of periods, the process is preempted, and another process executes for that given time period.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Allows OS to use the Context switching method to save states of preempted processes.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">It gives the best performance in terms of average response time.</span></li></ul>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"><br /></span></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Disadvantages of Round-Robin Scheduling</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">Here, are the drawbacks/cons of using Round-Robin scheduling:</span></p>\n"
                                           "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">If the slicing time of OS is low, the processor output will be reduced.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This method spends more time on context switching</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Its performance heavily depends on time quantum.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Priorities cannot be set for the processes.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round-robin scheduling doesn’t give special priority to more important tasks.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Decreases comprehension</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Lower time quantum results in higher context switching overhead in the system.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Finding a correct time quantum is a quite difficult task in this system.</span></li></ul>\n"
                                           "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px; font-size:14pt; color:#1a1a1a;\"><br /></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Worst Case Latency</span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:14pt; color:#1a1a1a; background-color:#ffffff;\">This term is used for the maximum time taken for the execution of all the tasks.</span></p>\n"
                                           "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">dt = Denote detection time when a task is brought into the list</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">st = Denote switching time from one task to another</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">et = Denote task execution time</span></li></ul>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:18px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"> </span></p>\n"
                                           "<p align=\"center\" style=\" margin-top:0px; margin-bottom:9px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-size:18pt; font-weight:600;   color:#1a1a1a;\">Summary:</span></p>\n"
                                           "<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The name of this algorithm comes from the round-robin principle, where each person gets an equal share of something in turns.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin is one of the oldest, fairest, and easiest algorithms and widely used scheduling methods in traditional OS.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Round robin is a pre-emptive algorithm</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">The biggest advantage of the round-robin scheduling method is that If you know the total number of processes on the run queue, then you can also assume the worst-case response time for the same process.</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">This method spends more time on context switching</span></li>\n"
                                           "<li style=\" font-size:14pt; color:#1a1a1a;\" align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" background-color:#ffffff;\">Worst-case latency is a term used for the maximum time taken for the execution of all the tasks.</span></li></ul>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"><br /></span></p>\n"
                                           "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#000000;\"><br /></span><span style=\" font-family:\'.AppleSystemUIFont\'; font-size:14pt; color:#000000;\"><br /></span></p></body></html>"))
        self.simulate_rr.setWhatsThis(_translate("MainWindow", "Simulate RR"))
        self.simulate_rr.setText(_translate(
            "MainWindow", "Simulate Round Robin (RR) Algorithm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.rr_tab), _translate("MainWindow", "RR"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(
            self.rr_tab), _translate("MainWindow", "Round Robin"))
        self.menuAlgorithms.setTitle(_translate("MainWindow", "Algorithms"))
        self.menuNon_Pre_emptive.setWhatsThis(
            _translate("MainWindow", "Algorithms Drop Down"))
        self.menuNon_Pre_emptive.setTitle(
            _translate("MainWindow", "Non Pre-emptive"))
        self.menuPre_emptive.setTitle(_translate("MainWindow", "Pre-emptive"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionDeveloper_Documentation.setText(
            _translate("MainWindow", "Developer Documentation"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionFirst_Come_First_Serve_FCFS.setText(
            _translate("MainWindow", "First Come First Serve(FCFS) "))
        self.actionShortest_Remaining_Job_First_SRTF.setText(
            _translate("MainWindow", "Shortest Remaining Job First(SRTF)"))
        self.actionRound_Robin_RR.setText(
            _translate("MainWindow", "Round Robin(RR)"))
        self.actionShortest_Job_First_SJF.setText(
            _translate("MainWindow", "Shortest Job First(SJF)"))
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = window()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
