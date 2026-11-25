import os
import argparse

parser = argparse.ArgumentParser(description='Executa o teste de corrida em uma GPU')
parser.add_argument('maquina', type=str, help='numeração da maquina (1-0, 1-1)')
parser.add_argument('tamanho_mig', type=str, help='tamanho do mig (ex: 1g.20gb ou "gpu". Precisa ser o tamanho exato)')
args = parser.parse_args()

maquina = args.maquina # maquina que vai executar os jobs, pode ser 1-0 ou 1-1
tamanho_mig = args.tamanho_mig # perfil do mig ou "gpu"
benchmarks = ['bt.C','cg.C','ep.C','ft.C','is.C','lu.C','mg.C','sp.C']

outputDir = f'/home/pabloh/2026/saidas/compute-{maquina}/exec_paralela/{tamanho_mig}'
# criar os diretórios:
for benchmark in benchmarks:
    try:
        os.system(f'mkdir {outputDir}/{benchmark.replace(".C","")} -p')
        os.system(f'mkdir /home/pabloh/2026/saidas/lixeira/exec_paralela/{maquina}/{tamanho_mig}/out -p')
        os.system(f'mkdir /home/pabloh/2026/saidas/lixeira/exec_paralela/{maquina}/{tamanho_mig}/err -p')
        
    except:
        continue

roteiro = f'''
#!/bin/bash

# Job name
#PBS -N mig_test_{maquina}_{tamanho_mig}

# Name of stdout output files
#PBS -o /home/pabloh/2026/saidas/lixeira/exec_paralela/{maquina}/{tamanho_mig}/out/
#PBS -e /home/pabloh/2026/saidas/lixeira/exec_paralela/{maquina}/{tamanho_mig}/err/


#PBS -l walltime=10:30:00

#PBS -l select=1:ncpus=128:mem=32gb:ngpus=5:host=compute-{maquina}

# Change to submission directory
cd $PBS_O_WORKDIR
cat $PBS_NODEFILE

# Launch 
python /home/pabloh/2026/scripts/criador_de_jobs1-1.py {maquina} {tamanho_mig}
'''

with open('/home/pabloh/2026/roteiros/roteiro_paralelo', 'w+') as f:
    f.write(roteiro)

os.system('qsub /home/pabloh/2026/roteiros/roteiro_paralelo')
