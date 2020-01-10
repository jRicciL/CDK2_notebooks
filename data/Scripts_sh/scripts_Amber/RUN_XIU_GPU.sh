## Para correr una tarea con el PBS hay que ejecutar
## qsub <nombre del script>

#PBS -N 3pxf_lig_r
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

PROT="3pxf_PROT_LIG"

###############################

##############################
# Comienza la termalizacion
termalizacion() {
	mpirun -np $NP pmemd.cuda.MPI -O  -i ./2_term/term.in -o ./2_term/"$PROT"_term.out -p ./"$PROT".prmtop -c ./1_min/"$PROT"_min_all.rst7 -r ./2_term/"$PROT"_term.rst7 -x ./2_term/"$PROT"_term.nc -inf "$PROT"_term.mdinfo
	wait
}

##############################
# Comienza el equi:librado
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
