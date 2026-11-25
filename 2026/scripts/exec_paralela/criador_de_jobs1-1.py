import argparse
import os
from time import time
import threading
import subprocess

# exemplo: python criador_de_jobs.py MIG-effedeec-21b5-5ad2-904d-f4d06708ac4d
parser = argparse.ArgumentParser(description='Executa o teste de corrida em uma GPU')
parser.add_argument('maquina', type=str, help='numeração da maquina (1-0, 1-1)')
parser.add_argument('tamanho_mig', type=str, help='tamanho do mig (ex: 1g.20gb. Precisa ser o tamanho exato)')
args = parser.parse_args()

maquina = args.maquina # maquina que vai executar os jobs, pode ser 1-0 ou 1-1
tamanho_mig = args.tamanho_mig # perfil do mig

mig_ou_gpu = 'mig' if tamanho_mig != 'gpu' else 'gpu'

devices = [ # id dos migs
'MIG-365f9ce1-c091-57a7-8ef3-4cbb45dcca47',
'MIG-40144944-d4a9-585d-978e-1ace55172139',
'MIG-0ebc0c9f-adc4-59a6-af10-200d49046bb5',
'MIG-effedeec-21b5-5ad2-904d-f4d06708ac4d'
]

device_locks = {
    device_id: threading.Lock()
    for device_id in devices
}

tempo_por_device_por_benchmark = {
    # Algo como: 'MIG-1863a8f0-4adf-5c21-b055-78502a027492_BT_THREAD_0': 123.45,
}

num_exec = 168
num_exec_por_gpu = int(num_exec / len(devices)) 

benchmarks = ['bt.C','cg.C','ep.C','ft.C','is.C','lu.C','mg.C','sp.C']

caminho = f'/home/pabloh/2026/saidas/compute-{maquina}/exec_paralela/{tamanho_mig}'

def rodar_gpu(id, benchmark, exec):
    lock = device_locks[id]

    with lock:
        inicio = time()
        for i in range(0, num_exec_por_gpu):
            arquivo_saida = f'{caminho}/{benchmark.replace(".C","")}/{mig_ou_gpu}-{benchmark.replace(".C","")}-{id}-{i}-exec-{exec}'
            with open(arquivo_saida, "w+") as f:
                #comando = f'CUDA_VISIBLE_DEVICES={id} /home/pabloh/NPB-GPU/CUDA/bin/{benchmark}'# >> /home/pabloh/2025/saidas/compute-{maquina}/{tamanho_mig}/{benchmark.replace(".C","")}/{mig_ou_gpu}-{benchmark.replace(".C","")}-{id}-{i}'
                subprocess.run(
                    [f'/home/pabloh/NPB-GPU/CUDA/bin/{benchmark}'],
                    env={**os.environ, "CUDA_VISIBLE_DEVICES": id},
                    stdout=f,
                    stderr=subprocess.STDOUT
                )
                #os.system(comando)

        # marca o tempo de cada thread em um dicionario para esse benchmark
        tempo_por_device_por_benchmark[f"{id}_{benchmark.replace('.C','').upper()}_{threading.current_thread().name}"] = time() - inicio



threads = []

for e in range(0, 10):
    for benchmark in benchmarks: 
        tempo_por_device_por_benchmark = {}
        inicio_geral = time()
    
        for i in range(0, len(devices)): 
            thread = threading.Thread(target=rodar_gpu, args=(devices[i], benchmark, e, ), name=f"THREAD_{i}")
            thread.start()
            threads.append(thread)


        for thread in threads:
            thread.join()
        threads = []

        fim_geral = time()

        try:
            os.system(f'mkdir {caminho}')
        except:
            pass
        name = f'{caminho}/tempo_de_fila_{e}'

        with open(name, 'a+') as tempo_file:
            msg = f'== TEMPO {benchmark.replace(".C","")} - {len(devices)}x{tamanho_mig} dispositivos ==\n'
            msg += f'Tempo total (inicio das threads até a sincronização delas): {fim_geral - inicio_geral} segundos\n'
            msg += str(tempo_por_device_por_benchmark)
            msg += '\n'
            tempo_file.write(msg)

        with open(f'{caminho}/tempo_de_fila_{benchmark}_{e}', 'a+') as individual_file:
            msg = f'Tempo total: {fim_geral - inicio_geral} segundos\n'
            msg += str(tempo_por_device_por_benchmark)
            individual_file.write(msg)
