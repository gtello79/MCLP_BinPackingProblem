# Multiple Container Loading Problem using Bin Packing Problem
 
In this work we plan to solve the MCLP by combining two algorithms:a  state-of-the-art  beam-search-based  algorithm  for  solving  the  single  CLPfrom a set of defined boxes, and a bin-packing algorithm for selecting andswapping boxes among the containers

## Dataset

Using the present configuration, we can load different instances of each dataset:

```
total_ejecution = 1         # Total de ejecuciones por instancias
init_instance = 1           # Instancia desde donde comenzar
total_inst = 16             # Total de instancias para la clase
total_class = 2             # Total de clases de la instancia
t_boxes = 4000              # Cantidad de cajas a utilizar
```

1. **BR instances**

Instancia que estudia un conjunto de 100 cajas, las cuales están agrupadas de acuerdo a tipos de cajas (en la unica instancia contenida existen 30 tipos de cajas).
```
total_inst = 30             # Total de instancias para la clase
total_class = 1             # Total de clases de la instancia
t_boxes = [100]              # Cantidad de cajas a utilizar

file_name = f'BR{n_class}.txt'
L,W,H, boxes, id2box = load_BRinstance(filename, inst)
```

2. **BRKGA instance**
```
total_inst = 10             # Total de instancias para la clase
total_class = 8             # Total de clases de la instancia
t_boxes = [50, 100, 150, 200]              # Cantidad de cajas a utilizar

file_name = f'../benchs/class{i_class}/{i_boxes}.txt'
L,W,H, boxes, id2box = load_BRinstance(filename, inst)
```

3. **Data Large Instance**
```
total_inst = 15             # Total de instancias para la clase
t_boxes = [100, 250, 500, 750, 1000, 1250, 1500,..., 4750, 5000]   # Cantidad de cajas a utilizar

file_name = f'../benchs/Data_Large/L_{i_boxes}/L_{i_boxes}_{i_inst}.txt'
L,W,H,boxes,id2box = load_LargeInstance(filename=file_name_datalarge)

```

4. **Elhedhli Instance**

```
total_inst = 5                                    # Total de instancias para la clase
total_class = 4                                    # Total de clases de la instancia
t_boxes = [50,100,150,200,500, 1000,1500,2000]     # Cantidad de cajas a utilizar

file_name_column = f"../benchs/Instance_CG/{i_boxes}/bin_pack_instance_i({i_inst})_c({i_class}).txt"
L,W,H,boxes,id2box = load_instances_elhedhli(filename=file_name_column)

```
