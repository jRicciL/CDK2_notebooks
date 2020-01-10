import argparse
import sys
import os, subprocess

parser = argparse.ArgumentParser(description='Preparación de sistemas para dinámcia molecular con amber.')

def check_pdb_file(protein):
    if not os.path.isfile(F'./{protein}'):
        raise argparse.ArgumentTypeError("Se requiere un archivo '.pdb' válido.")
    return protein
def check_ion(ion):
    if ion not in ['Cl-', 'Na+']:
        raise argparse.ArgumentTypeError("Los iones aceptados son 'Cl-' o 'Na+'")
    return ion
def check_solvent(solvent):
    solvent = solvent.upper()
    if solvent not in ['WAT', 'ETA']:
        raise argparse.ArgumentTypeError("Por ahora el solvente aceptado es 'WAT' y 'ETA'")
    return solvent

# Argumentos del parser
# Archivo pdb de la proteína
parser.add_argument('-p', '--protein', required=True, type=check_pdb_file,
    help = 'Archivo pdb de la proteína con todos los átomos. Usar PD2PQR y pdb4amber previamente.')
parser.add_argument('-o', '--output_name', required=True, 
    help = 'Nombre de lso archivos de salida para la proteína: ej. "sa_dm_3pxf"')
parser.add_argument('-io', '--ion', default='Cl-', type=check_ion,
    help = "Ion para la neutralización del sistema: 'Cl-' o 'Na+'")
parser.add_argument('-s', '--solvatation', default='WAT', type=check_solvent,
    help = "Tipo de solvatación del sistema: 'WAT' = TIP3PBOX o 'ETA' = ETAWAT20")
parser.add_argument('-pb', '--padding_box', default=12.0,
    help = "Distancia de 'padding' para solvatar el sistema. Def: 12A")
# TODO: Implementar sistemas de caja y oct

args = vars(parser.parse_args())
# Asignación de las variables
PROT = args['protein'][:-4]
ION = args['ion']
CUTOFF = args['padding_box']
SOLVENT = 'TIP3PBOX' if args['solvatation'] == 'WAT' else 'ETAWAT20'
OUTPUT = args['output_name']

if SOLVENT == 'ETAWAT20':
    if os.path.isfile('./ETAWAT20.off'): pass
    else:
        sys.exit("Se requiere la librería 'ETAWAT20.off' en el presente directorio.")

# Genera el archivo de ejecuación de tleap
_comment = '#' if SOLVENT != 'ETAWAT20' else ''
with open('leap.temp.in', 'w') as f:
    f.write(F'''
source oldff/leaprc.ff99SB
# Carga de la libreria del solvente mixto
# tiene que estar en la carpeta de trabajo
{_comment}loadoff ./ETAWAT20.off
# Para solvatar con TIP3P
source leaprc.water.tip3p

# Carga de la proteina
system = loadpdb ./{PROT}.pdb

# Solvatamos el sistema en OCT
solvateOct system {SOLVENT} {CUTOFF}

# Neutralizar
addions system {ION} 0

check system

# Guardar los parametros
saveamberparm system {OUTPUT}.prmtop {OUTPUT}.rst7
savepdb system PDB_{OUTPUT}.pdb
quit
    ''')

# ejecutamos tleap para preparar el sistema
subprocess.Popen('tleap -f leap.temp.in'.split())

# Crea los archivos de ejecución para minimización en miztli y en xiu
with open('RUN_GPU_min_miztli.sh', 'w') as f:
    f.write('''
#!/bin/bash 
#BSUB -P project
#BSUB -J %s
#BSUB -a openmpi
#BSUB -q q_gpu     
#BSUB -n 1
#BSUB -eo err.err
#BSUB -oo err.out

module purge
module load intel/2017_update4
module load amber/16
module load cuda/7.5

export AMBER_PREFIX="/opt/SC/amber-16"
export AMBERHOME=/opt/SC/amber-16

PROT="%s"

# Para ejecutar cada paso se ha establecido como una función que debe ser llamada al final del archivo
# Comentar los pasos que no desean realizarse


###############################
# Minimización solvente
minimizacion() {
	$AMBERHOME/bin/pmemd.cuda -O -i ./1_min/min_solv.in -o ./1_min/"$PROT"_min_solv.out -p ./"$PROT".prmtop -c ./"$PROT".rst7 -ref ./"$PROT".rst7 -r ./1_min/"$PROT"_min_solv.rst7 -inf "$PROT"_min_solv.mdinfo
	wait

	# Análisis 1 min_solv
	process_mdout.perl ./1_min/"$PROT"_min_solv.out
	mkdir ./1_min/"$PROT"_min_solv
	mv summary* ./1_min/"$PROT"_min_solv
	wait

	# Minimización total
	$AMBERHOME/bin/pmemd.cuda -O -i ./1_min/min_all.in -o ./1_min/"$PROT"_min_all.out -p ./"$PROT".prmtop -c ./1_min/"$PROT"_min_solv.rst7 -r ./1_min/"$PROT"_min_all.rst7 -inf "$PROT"_min_all.mdinfo
	wait

	# Análisis 2 min_solv
	process_mdout.perl ./1_min/"$PROT"_min_all.out
	mkdir ./1_min/"$PROT"_min_all
	mv summary* ./1_min/"$PROT"_min_all
	wait

	# Para covertir el rst a pdb
	ambpdb -p ./"$PROT".prmtop -c ./1_min/"$PROT"_min_all.rst7 > ./1_min/"$PROT"_min_all.pdb
}

minimizacion
''' % (OUTPUT, OUTPUT))

# Archivo para ejecutar la dinámica en xiu
with open('RUN_XIU_GPU.sh', 'w') as f:
    f.write('''
## Para correr una tarea con el PBS hay que ejecutar
## qsub <nombre del script>

#PBS -N %s_r1
#PBS -l nodes=1:ppn=12
#PBS -q CGPUK80
#PBS -M jricci@cicese.edu.mx

### Comandos para la ejecucion de la tarea

##Levantando el entorno
cd  $PBS_O_WORKDIR;

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/gpu/7.5/lib64/
source /opt/gpu/cudavars.sh 7.5


# Determina el numero de procesadores para ejecutar la tarea
NP=$(($PBS_NUM_NODES * $PBS_NUM_PPN))
#NP=1

## Ejecutar la tarea en todos los procesadores asignados con MPI
cat $PBS_NODEFILE |sort|uniq> mpd.hosts

NM=$(cat mpd.hosts|wc -l |awk '{print $1}')

###Creacion del direactorio de admministracion 
mkdir $PBS_O_WORKDIR/admon-$PBS_JOBID;
cat mpd.hosts > $PBS_O_WORKDIR/admon-$PBS_JOBID/lista-nodos-$PBS_JOBID.txt
env      > $PBS_O_WORKDIR/admon-$PBS_JOBID/entorno-$PBS_JOBNAME.txt;
export CUDA_VISIBLE_DEVICES=0

###############################################
# Comienza el script

PROT="%s"

###############################

##############################
# Comienza la termalizacion
termalizacion() {
	mpirun -np $NP pmemd.cuda.MPI -O  -i ./2_term/term.in -o ./2_term/"$PROT"_term.out -p ./"$PROT".prmtop -c ./1_min/"$PROT"_min_all.rst7 -r ./2_term/"$PROT"_term.rst7 -x ./2_term/"$PROT"_term.nc -inf "$PROT"_term.mdinfo
	wait
}

##############################
# Comienza el equilibrado
equilibrado() {
	mpirun -np $NP pmemd.cuda.MPI -O  -i ./3_eq/eq.in -o ./3_eq/"$PROT"_eq.out -p ./"$PROT".prmtop -c ./2_term/"$PROT"_term.rst7 -r ./3_eq/"$PROT"_eq.rst7 -x ./3_eq/"$PROT"_eq.nc -inf "$PROT"_eq.mdinfo
	wait

	# Analisis con ccptraj
	mpirun -np $NP cpptraj.MPI.cuda -i ./3_eq/rmsd_eq.cpptraj
}

##############################
# Comienza la producción
produccion() {
	mpirun -np $NP pmemd.cuda.MPI -O  -i ./4_prod/prod.in -o ./4_prod/"$PROT"_prod.out -p ./"$PROT".prmtop -c ./3_eq/"$PROT"_eq.rst7 -r ./4_prod/"$PROT"_prod.rst7 -x ./4_prod/"$PROT"_prod.nc -inf "$PROT"_prod.mdinfo
	wait

	# Extrae la trayectoria con ccptraj
	mpirun -np $NP cpptraj.MPI.cuda -i ./4_prod/rmsd_prod.cpptraj
}


###################

# EJECUCION

###################

termalizacion
wait
equilibrado
wait
produccion

###############################################

echo Termina de Ejecutar a las: ;
rm -f mpd.hosts
exit 0
'''% (OUTPUT, OUTPUT))