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

start_import = time.process_time()

# ------------initialization setting-------------
# import data
wip = pd.read_excel("./semiconductor_data.xlsx", sheet_name=2, dtype=str)
eqp = pd.read_excel("./semiconductor_data.xlsx", sheet_name=0, dtype=str)
tool = pd.read_excel("./semiconductor_data.xlsx", sheet_name=1, dtype=str)
setup_time = pd.read_excel("./semiconductor_data.xlsx", sheet_name=3, index_col=0) #index can sue

# Normal


population_size=10

## GA
num_iteration =3
crossover_rate=1    
mutation_rate=1     

## PSO
w=0.5
c1=2
c2=2

PSO_size = int(population_size/2)
GA_size = population_size -PSO_size

# Selection setting (roulette_wheel) 
elite_selection_size=int(population_size*0.2) 
rank_selection_size= population_size*2 - elite_selection_size 
rank_selection_num= population_size- elite_selection_size
proba_list = rank_selection_get_proba_list(rank_selection_size) 

# ------------------Initialize the population & velocity--------------------
# create jobs
jobs = []
for i in range(len(wip.values)): #job len (100)
    jobs.append(Job(wip.iloc[i], eqp))

# create chromosomes(first gen)
chromosomes = []
for i in range(population_size):
    chromosomes.append(Chromosome(len(jobs))) #input ()

# create machines
machines=[]
for i in range(len(tool.values)):
    machines.append(Machine(tool.iloc[i]))

# initialize the velocity
v1 = np.zeros((population_size,len(jobs)*2))
v2 =np.copy(v1)
#-------------------- fitness value -------------------------------------
def fitness(chromosomes,jobs,machines):
    for k in range(len(chromosomes)):
        chromosomes[k].clear_values()

        # job set_probability
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
    
    # caculate targetvalue
    for t in range(len(chromosomes)):
        chromosomes[t].target_value= 0.01* chromosomes[t].makespan + 0.99*chromosomes[t].tardiness_num

    return chromosomes

#---------initialize fitness-----------
chromosomes=fitness(chromosomes,jobs,machines)
#排序，依target_value
sorted_chromosomes = sorted(chromosomes, key=lambda e:e.target_value, reverse = False) #小到大
pbest=deepcopy(chromosomes)
gbest=deepcopy(sorted_chromosomes[0])

# for i in range(5):
#     print(pbest[i].probability)
# print("---")
# print(gbest.target_value)
# print("---")

#----------------Termination Criteria -----------------------------------
MakespanRecord=[] 

for x in range(num_iteration-1): # minus first time

#--------------Update v & x -----------

    chromosomes2 =deepcopy(chromosomes)

    # 前半PSO
    for i in range(PSO_size):
        for j in range(len(jobs)*2):
            x1 = chromosomes[i].probability[j]
            x2 = chromosomes2[i].probability[j]
            v2[i][j] = w * v1[i][j] + c1 *random.random()* (pbest[i].probability[j] - x1) + c2*random.random()*( gbest.probability[j] - x1)
            x2=x1+v2[i][j]
            if x2<=0 :
                x2=0.00001
            elif x2>=1 :
                x2=0.99999
            chromosomes2[i].probability[j] =x2

    # 後半 crossover & mutation 

        # GA_size
        for i in range(GA_size):
            pass

    # combine two of above 
    chromosomes=[]
    v1 =np.copy(v2)

    for i in range(population_size):
        chromosomes.append(chromosomes2[i])
    
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
  
    MakespanRecord.append(gbest.target_value)

# #--------------------------------------------------
# # 迭代
# MakespanRecord=[]        

# for x in range(num_iteration):
#     parent_list = deepcopy(chromosomes)
#     offspring_list= deepcopy(chromosomes)

#     #------------------------Crossover------------------------------------
#     offspring_list = Crossover(parent_list,offspring_list,population_size,len(jobs),crossover_rate)

#     #------------------------Mutation------------------------------------
#     offspring_list = mutation(population_size,offspring_list,mutation_rate,len(jobs))

#     #-------------------- fitness value -------------------------------------
#     total_chromosomes=deepcopy(parent_list)+deepcopy(offspring_list)

#     for k in range(len(total_chromosomes)):
#         total_chromosomes[k].clear_values()

#         # job set_probability
#         for j in range(len(jobs)):
#             jobs[j].set_probability(total_chromosomes[k].get_probability(j)) 

#         # machine action
#         for i in range(len(machines)):
#             machines[i].add_job(jobs)
#             machines[i].sort_job()     
#             machines[i].calculate_process_time(setup_time)     
  
#             # record makespan & tardiness_num
#             # record makespan
#             if machines[i].endTime > total_chromosomes[k].makespan :
#                 total_chromosomes[k].makespan=machines[i].endTime
#             # record tardiness_num
#             for j in range(len(machines[i].sorted_jobs)): 
#                 if  machines[i].sorted_jobs[j].startTime > float(machines[i].sorted_jobs[j].R_QT)*60:
#                     total_chromosomes[k].tardiness_num+=1

#             machines[i].clear_job()            


#     #print("-------")
#     #-----------------Selection----------------------

#     for t in range(len(total_chromosomes)):
#         #print(total_chromosomes[t].makespan,total_chromosomes[t].tardiness_num)
#         total_chromosomes[t].target_value= 0.01* total_chromosomes[t].makespan + 0.99*total_chromosomes[t].tardiness_num
#        # print(total_chromosomes[t].target_value)

#     #排序，依target_value
#     sorted_total_chromosomes = sorted(total_chromosomes, key=lambda e:e.target_value, reverse = False) #小到大

#     #rank_selection(consider elite)
#     select_index= rank_selection_get_select_index(proba_list,rank_selection_num)

#     #next Gen(elite & rank)
#     chromosomes=[]
#     for i in range(elite_selection_size):
#         chromosomes.append(sorted_total_chromosomes[i])
#         print(sorted_total_chromosomes[i].makespan,sorted_total_chromosomes[i].tardiness_num,sorted_total_chromosomes[i].target_value)
#     for j in select_index:
#         chromosomes.append(sorted_total_chromosomes[elite_selection_size + j])
#         print(sorted_total_chromosomes[j].makespan,sorted_total_chromosomes[j].tardiness_num,sorted_total_chromosomes[j].target_value)

#     print("------")

#     #收斂圖record
#     MakespanRecord.append(chromosomes[0].target_value)
  


# # -----------------Result----------------------

# ## final job & machine condition
# chromosomes[0].tardiness_num=0
# job set_probability
for j in range(len(jobs)):
    jobs[j].set_probability(gbest.get_probability(j)) 

# machine action
for i in range(len(machines)):
    machines[i].add_job(jobs)
    machines[i].sort_job()     
    machines[i].calculate_process_time(setup_time)    

print("tardiness=",gbest.tardiness_num)
print("makespan=",gbest.makespan)
print("target_value=",gbest.target_value)

#     # record makespan & tardiness_num
#     # record makespan
#     if machines[i].endTime > chromosomes[0].makespan :
#         chromosomes[0].makespan=machines[i].endTime
#     # record tardiness_num
#     for j in range(len(machines[i].sorted_jobs)): 
#         if  machines[i].sorted_jobs[j].startTime > float(machines[i].sorted_jobs[j].R_QT)*60:
#             chromosomes[0].tardiness_num+=1


end_import = time.process_time()
process_import=end_import-start_import

print("執行時間:",process_import)


#收斂圖
# "%d" %i
plt.plot([i for i in range(len(MakespanRecord))],MakespanRecord,'b') #x,y為list資料
plt.ylabel('target_value',fontsize=15)
plt.xlabel('generation',fontsize=15)
plt.show()

# #甘特圖
# #時間限制(超過24hr:1440 分)
# df=[]
# for i in range(len(machines)):
#     for j in range(len(machines[i].sorted_jobs)): 

#         # if  machines[i].sorted_jobs[j].startTime > float(machines[i].sorted_jobs[j].R_QT)*60:
#         #     df.append(
#         #     dict(Task=str(machines[i].sorted_jobs[j].LOT_ID), 
#         #     Start='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].startTime)),
#         #     Finish='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].endTime)),
#         #     Recipe='broken',
#         #     Machine=machines[i].EQP_ID))
    
#         # else:
#         df.append(
#         dict(Task=str(machines[i].sorted_jobs[j].LOT_ID), 
#         Start='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].startTime)),
#         Finish='2020-11-07 %s'%datetime.timedelta(seconds=float(machines[i].sorted_jobs[j].endTime)),
#         Recipe=machines[i].sorted_jobs[j].RECIPE,
#         Machine=machines[i].EQP_ID))


# #呈現圖表
# fig1 = px.timeline(df, x_start="Start", x_end="Finish", y="Machine", color="Recipe",text="Task")
# fig1.show()