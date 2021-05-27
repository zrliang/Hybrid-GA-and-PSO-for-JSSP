from Job import *
import json
class Machine(object):
    def __init__(self,configure):
        self.configure=configure #
        self.recoverTime = int(self.configure["RECOVER_TIME"])
        for i in self.configure.index:   #LOT_ID、OPE_NO... to object
            setattr(self, i, self.configure[i])
        self.startTime= int(self.configure["RECOVER_TIME"])

        self.jobs = [] #未排
        self.sorted_jobs=[]
        self.endTime=0

    def add_job(self,jobs):
        for i in range(len(jobs)):
            if self.configure["EQP_ID"]==jobs[i].machineID:
                self.jobs.append(jobs[i])
    

    def sort_job(self):
        self.sorted_jobs = sorted(self.jobs, key=lambda e:e.probability[1], reverse = True) #二維排序(x[1]針對 jobs物件 的prob[1]) 由大到小
        #self.sorted_jobs = sorted(self.jobs, key=lambda e:float(e.R_QT), reverse = False) #二維排序(x[1]針對 jobs物件 的prob[1]) 用R_QT

    def calculate_process_time(self,setuptime_Table):
        currentTime = int(self.configure["RECOVER_TIME"])
        #print(currentTime)
        # set start & end Time
        for i in range(len(self.sorted_jobs)):
           
            self.sorted_jobs[i].set_start_time(currentTime)

            # 0~-2個
            if i != len(self.sorted_jobs)-1:
                p1= int(self.sorted_jobs[i].LOT_ID[3:6]) #LOT030 >>30
                p2= int(self.sorted_jobs[i+1].LOT_ID[3:6])

                currentTime = self.sorted_jobs[i].get_end_time() + setuptime_Table.at[p1,p2]

            #the last
            else: 
                currentTime = self.sorted_jobs[i].get_end_time()
               
        self.endTime=currentTime

    def clear_job(self):
        self.jobs = [] 
        self.sorted_jobs=[]
        self.endTime=0