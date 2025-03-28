VERBOSE = False

# Algorithm settings
min_fr = 0.99               # minimo porcentaje ocupado para considerar la generación de un bloque
# maxima cantidad de bloques a generar por bsg
max_bl = 10000
min_bin = 1000

instances_name = "martello"
MAX_ITER = 100           # Valor de persistencia del Swap
bsg_time = 5
r_param = 1.5
n_runs = 5
max_no_improvements = 50
MIN_BOXES_TO_POP = 8
swaps = "--swaps"


# Connection params
#host = "158.251.88.197"
#host_2 = "158.251.93.9"
#port = 22
#username = "iaraya"
#password = "lunyta22"

LOCAL_EXECUTION = False

# SWAP CONFIG
MAX_VOL_ACCEPT = 0.65
TOLERANCE = 0.3
N_TO_SWAP = 2
DIFF_ACCEPT = 1e-7