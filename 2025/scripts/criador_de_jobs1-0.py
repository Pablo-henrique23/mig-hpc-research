import argparse
import os
from time import time
import threading

# exemplo: python criador_de_jobs.py MIG-effedeec-21b5-5ad2-904d-f4d06708ac4d
parser = argparse.ArgumentParser(description='Executa o teste de corrida em uma GPU')
parser.add_argument('maquina', type=str, help='numeração da maquina (1-0, 1-1)')
parser.add_argument('tamanho_mig', type=str, help='tamanho do mig (ex: 1g.20gb. Precisa ser o tamanho exato)')
args = parser.parse_args()

maquina = args.maquina # maquina que vai executar os jobs, pode ser 1-0 ou 1-1
tamanho_mig = args.tamanho_mig # perfil do mig

mig_ou_gpu = 'mig' if tamanho_mig != 'gpu' else 'gpu'

devices = [ # id dos migs
    'MIG-bbc0f904-20ba-5ff0-aa76-754fa93730ba',
    'MIG-5e5f0459-057d-5c61-b065-68892d1d27df',
    'MIG-6d453f0c-ca44-53ae-947c-52497b81d66b',
    'MIG-fad1c2a5-0979-5cbb-b4db-06a50630487c'
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

def rodar_gpu(id, benchmark):
    lock = device_locks[id]

    with lock:
        inicio = time()
        for i in range(0, num_exec_por_gpu):
            comando = f'time CUDA_VISIBLE_DEVICES={id} /home/pabloh/NPB-GPU/CUDA/bin/{benchmark}' #>> /home/pabloh/2025/saidas/compute-{maquina}/{tamanho_mig}/{benchmark.replace(".C","")}/{mig_ou_gpu}-{benchmark.replace(".C","")}-{id}-{i}'
            os.system(comando)

        # marca o tempo de cada thread em um dicionario para esse benchmark
        tempo_por_device_por_benchmark[f"{id}_{benchmark.replace('.C','').upper()}_{threading.current_thread().name}"] = time() - inicio



threads = []
for benchmark in benchmarks: 
    tempo_por_device_por_benchmark = {}
    inicio_geral = time()
    
    for i in range(0, len(devices)): 
        thread = threading.Thread(target=rodar_gpu, args=(devices[i], benchmark, ), name=f"THREAD_{i}")
        thread.start()
        threads.append(thread)


    for thread in threads:
        thread.join()
    threads = []

    fim_geral = time()

    caminho = ''
    name = ''

    caminho = f'/home/pabloh/2025/saidas/compute-{maquina}/{tamanho_mig}'

    try:
        os.system(f'mkdir {caminho}')
    except:
        pass
    name = f'{caminho}/tempo_de_fila_{num_exec}'

    with open(name, 'a+') as tempo_file:
        msg = f'== TEMPO {benchmark.replace(".C","")} - {len(devices)}x{tamanho_mig} dispositivos ==\n'
        msg += f'Tempo total (inicio das threads até a sincronização delas): {fim_geral - inicio_geral} segundos\n'
        msg += str(tempo_por_device_por_benchmark)
        msg += '\n'
        tempo_file.write(msg)

    with open(f'{caminho}/tempo_de_fila_{num_exec}_{benchmark}', 'a+') as individual_file:
        msg = f'Tempo total: {fim_geral - inicio_geral} segundos\n'
        msg += str(tempo_por_device_por_benchmark)
        individual_file.write(msg)
