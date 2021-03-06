# importing required modules
from Job import * 
from Machine import * 
from Chromosome import * 

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import random
import plotly.express as px
import datetime
from copy import deepcopy
import time
import openpyxl                      
from openpyxl import Workbook

# 用python建立一個Excel空白活頁簿
excel_file = Workbook()
# 建立一個工作表
sheet = excel_file.active

# 先填入第一列的欄位名稱
sheet['A1'] = '次數'
sheet['B1'] = 'Makespan'
sheet['C1'] = '代數'
sheet['D1'] = '時間'


# 實驗30次
for z in range(30):
    start_import = time.process_time()
    pt =180
    # ------------initialization setting-------------
    # import data
    wip = pd.read_excel("./semiconductor_data(50,5).xlsx", sheet_name=2, dtype=str)
    eqp = pd.read_excel("./semiconductor_data(50,5).xlsx", sheet_name=0, dtype=str)
    tool = pd.read_excel("./semiconductor_data(50,5).xlsx", sheet_name=1, dtype=str)
    setup_time = pd.read_excel("./semiconductor_data(50,5).xlsx", sheet_name=3, index_col=0) #index can sue

    ## PSO parameter
    population_size=50
    num_iteration =2000
    w=0.5
    c1=2
    c2=2

    # ------------------Initialize the population & velocity--------------------
    # create jobs
    jobs = []
    for i in range(len(wip.values)): #job len (100)
        jobs.append(Job(wip.iloc[i], eqp))

    # create chromosomes(first gen)
    chromosomes = []
    for i in range(population_size):
        chromosomes.append(Chromosome(len(jobs))) #input()

    # create machines
    machines=[]
    for i in range(len(tool.values)):
        machines.append(Machine(tool.iloc[i]))

    # initialize the velocity(v1.v2 is array)
    v1 = np.zeros((population_size,len(jobs)*2))  #  initialize v to zero
    v2 =np.copy(v1)
    #-------------------- Fitness value Function -------------------------------------
    def fitness(chromosomes,jobs,machines):
        for k in range(len(chromosomes)):
            chromosomes[k].clear_values()

            # job set_probability (job get gene & machine ID)
            for j in range(len(jobs)):
                jobs[j].set_probability(chromosomes[k].get_probability(j)) 

            # machine action & record makespan & tardiness_num
            for i in range(len(machines)):
                machines[i].add_job(jobs)
                machines[i].sort_job()     
                machines[i].calculate_process_time(setup_time)     
                # record makespan & tardiness_num
                # record makespan
                if machines[i].endTime > chromosomes[k].makespan :
                    chromosomes[k].makespan=machines[i].endTime
                # record tardiness_num
                for j in range(len(machines[i].sorted_jobs)): 
                    if  machines[i].sorted_jobs[j].startTime > float(machines[i].sorted_jobs[j].R_QT)*60:
                        chromosomes[k].tardiness_num+=1

                machines[i].clear_job()    
        
            # caculate target_value(w1,w2)
            chromosomes[k].target_value= 1 * chromosomes[k].makespan + 0*chromosomes[k].tardiness_num

        return chromosomes

    #---------initialize fitness-----------
    chromosomes=fitness(chromosomes,jobs,machines)
    #排序，依target_value
    sorted_chromosomes = sorted(chromosomes, key=lambda e:e.target_value, reverse = False) #小到大
    pbest=deepcopy(chromosomes) 
    gbest=deepcopy(sorted_chromosomes[0])

    #----------------Termination Criteria -----------------------------------
    MakespanRecord=[] 

    for x in range(num_iteration-1): # minus first time

    #--------------Update v & x -----------

        temp_chromosomes =deepcopy(chromosomes)

        for i in range(population_size):
            for j in range(len(jobs)*2):
                x1 = chromosomes[i].probability[j]
                x2 = temp_chromosomes[i].probability[j]
                v2[i][j] = w * v1[i][j] + c1 *random.random()* (pbest[i].probability[j] - x1) + c2*random.random()*( gbest.probability[j] - x1)
                x2=x1+v2[i][j]
                if x2<=0 :
                    x2=0.00001
                elif x2>=1 :
                    x2=0.99999
                temp_chromosomes[i].probability[j] =x2

        # reset & next 
        chromosomes=[]
        v1 =np.copy(v2)

        for i in range(population_size):
            chromosomes.append(temp_chromosomes[i])
        
        #--------caculate fitness-------------
        chromosomes=fitness(chromosomes,jobs,machines)
        #排序，依target_value
        sorted_chromosomes = sorted(chromosomes, key=lambda e:e.target_value, reverse = False) #小到大

        # compare pbest & update
        for p in range(len(chromosomes)):
            if chromosomes[p].target_value< pbest[p].target_value :
                pbest[p] = deepcopy(chromosomes[p])
        # compare gbest & update
        if sorted_chromosomes[0].target_value< gbest.target_value :
            gbest = sorted_chromosomes[0]
        
        # record
        MakespanRecord.append(gbest.target_value)

        end_import = time.process_time()
        process_import=end_import-start_import
        # 停止條件
        if gbest.target_value == 462:
            break
        elif process_import>=pt:
            break

    # # -----------------Result----------------------

    # ## final job & machine condition

    # job set_probability
    for j in range(len(jobs)):
        jobs[j].set_probability(gbest.get_probability(j)) 

    # machine action
    for i in range(len(machines)):
        machines[i].add_job(jobs)
        machines[i].sort_job()     
        machines[i].calculate_process_time(setup_time)    

    # print("PSO_main.py")
    # print(x,"代")
    # print("tardiness=",gbest.tardiness_num)
    # print("makespan=",gbest.makespan)
    # print("target_value=",gbest.target_value)
    # print("執行時間:",process_import)

    #record excel data
    columnA = str(z+1)
    columnB = str(gbest.makespan)
    columnC = str(x+2)
    columnD = str(process_import)
    sheet.append([columnA, columnB, columnC, columnD])

excel_file.save('PSO_case2.xlsx')    


# #收斂圖
# # "%d" %i
# plt.plot([i for i in range(len(MakespanRecord))],MakespanRecord,'b') #x,y為list資料
# plt.ylabel('target_value',fontsize=15)
# plt.xlabel('generation',fontsize=15)
# plt.show()

# #甘特圖
# #時間限制(超過24hr:1440 分)
# df=[]
# for i in range(len(machines)):
#     for j in range(len(machines[i].sorted_jobs)): 
   
#         df.append(
#         dict(Task=str(machines[i].sorted_jobs[j].LOT_ID), 
#         Start='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].startTime)),
#         Finish='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].endTime)),
#         Recipe=machines[i].sorted_jobs[j].RECIPE,
#         Machine=machines[i].EQP_ID))


# #呈現圖表
# fig1 = px.timeline(df, x_start="Start", x_end="Finish", y="Machine", color="Recipe",text="Task")
# fig1.show()