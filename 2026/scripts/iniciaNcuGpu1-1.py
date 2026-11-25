import os
import argparse


maquina = '1-1' # maquina que vai executar os jobs, pode ser 1-0 ou 1-1
benchmarks = ['bt.C','cg.C','ep.C','ft.C','is.C','lu.C','mg.C','sp.C']
mig = 'GPU'
roteiro_path = '/home/pabloh/2026/roteiros/ncuExecGpu'

try:
    os.system(f'mkdir /home/pabloh/2026/relatorios/{mig}/ -p')
    os.system(f'mkdir /home/pabloh/2026/saidas/{maquina}/{mig}/out/ -p')
    os.system(f'mkdir /home/pabloh/2026/saidas/{maquina}/{mig}/err/ -p')
except:
    pass


for i in range(0,1):
    for benchmark in benchmarks:
        benchmark_name = benchmark.replace('.C', '')
        roteiro = f'''
#!/bin/bash

# Job name
#PBS -N ncu_{benchmark_name}_{mig}_{i}

# Name of stdout output files
#PBS -o /home/pabloh/2026/saidas/{maquina}/{mig}/out/{benchmark_name}_{mig}_{i}.out
#PBS -e /home/pabloh/2026/saidas/{maquina}/{mig}/err/{benchmark_name}_{mig}_{i}.err


#PBS -l walltime=23:30:00

#PBS -l select=1:ncpus=128:mem=32gb:ngpus=5:host=compute-{maquina}

# Change to submission directory
cd $PBS_O_WORKDIR
cat $PBS_NODEFILE

# Launch 
CUDA_VISIBLE_DEVICES='GPU-fd7e14c3-91ce-6c4b-e736-393c0d0537ef' /opt/nvidia/nsight-compute/2025.2.1/ncu --section SpeedOfLight --section MemoryWorkloadAnalysis -o /home/pabloh/2026/relatorios/GPU/relatorio_{benchmark_name}_{mig}_{i} --clock-control none /home/pabloh/NPB-GPU/CUDA/bin/{benchmark}
'''

        with open(roteiro_path, 'w+') as f:
            f.write(roteiro)

        os.system(f'qsub {roteiro_path}')
