import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rshub import load_file 
from rshub import submit_jobs
import time

token = 'Enter Your token here'

project_name = 'Vegetation Validation'
task_name1 = 'Layered Vegetation'
scenario_flag = 'veg'
algorithm = 'rt'
output_var = 'tb'
inc_angle = 40
fGHz = 17.2
task_name = task_name1 + ' Date' +str(1)

while True:
    result=submit_jobs.check_completion(token, project_name, task_name1)
    status = result.get("task_status", None)  # safe access

    print(f"Status: {status}")

    if status == "completed":
        print("Job completed. Moving to next step...")
        break
    
    if status is None:
        scatters1=[[]]
        # Branch
        types = 1 # 1: cylinder; 0: disc
        VM = 0.37 # Volumetric Moisture 
        L = 7.85 # Length of the scatterer [m]
        D = 0.15 # Diameter of the scatterer [m]
        beta1 = 0 # lower bound of orientation range of the scatterer (degree)
        beta2 = 10 # upper bound of orientation range of the scatterer (degree)
        disbot = 0 # lower bound of vertical distribution range of the scatterer
        distop = 8 # upper bound of vertical distribution range of the scatterer
        NA = 0.24 # density of the scatterer
        scatters1[0]=[types, VM, L, D, beta1, beta2, disbot, distop, NA]

        # Primary branch
        types = 1 # 1: cylinder; 0: disc
        VM = 0.501 # Volumetric Moisture 
        L = 1.41 # Length of the scatterer [m]
        D = 0.0288 # Diameter of the scatterer [m]
        beta1 = 30 # lower bound of orientation range of the scatterer (degree)
        beta2 = 90 # upper bound of orientation range of the scatterer (degree)
        disbot = 2 # lower bound of vertical distribution range of the scatterer
        distop = 3.5 # upper bound of vertical distribution range of the scatterer
        NA = 3.12 # density of the scatterer
        scatters1.append([types, VM, L, D, beta1, beta2, disbot, distop, NA])

        # Secondary branch
        types = 1 # 1: cylinder; 0: disc
        VM = 0.444 # Volumetric Moisture 
        L = 0.555 # Length of the scatterer [m]
        D = 0.0112 # Diameter of the scatterer [m]
        beta1 = 35 # lower bound of orientation range of the scatterer (degree)
        beta2 = 90 # upper bound of orientation range of the scatterer (degree)
        disbot = 2 # lower bound of vertical distribution range of the scatterer
        distop = 5 # upper bound of vertical distribution range of the scatterer
        NA = 34.32 # density of the scatterer
        scatters1.append([types, VM, L, D, beta1, beta2, disbot, distop, NA])

        # Leaf
        types = 0 # 1: cylinder; 0: disc
        VM = 0.58 # Volumetric Moisture 
        L = 0.0001 # thickness of the scatterer [m]
        D = 0.04 # Diameter of the scatterer [m]
        beta1 = 0 # lower bound of orientation range of the scatterer (degree)
        beta2 = 90 # upper bound of orientation range of the scatterer (degree)
        disbot = 2 # lower bound of vertical distribution range of the scatterer
        distop = 8 # upper bound of vertical distribution range of the scatterer
        NA = 7712.64 # density of the scatterer
        scatters1.append([types, VM, L, D, beta1, beta2, disbot, distop, NA])

        data1 = {
            'scenario_flag': scenario_flag,
            'output_var': output_var,'fGHz': fGHz,
            'algorithm':algorithm,
            'scatters': scatters1,'core_num':2,
            'project_name':project_name,
            'task_name':task_name1,
            'token': token,
        }
        result1=submit_jobs.run(data1)

    # If not completed, wait 30 seconds
    time.sleep(30)
    
data = load_file(token, project_name, task_name, fGHz,scenario_flag,algorithm,output_var,inc_angle)
# data_multi = data.load_error_message()
data_multi = data.list_files()
# data_multi = data.load_outputs(force_method='disk')

print(data_multi)
