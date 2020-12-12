#!/bin/bash 
#BSUB -P project
#BSUB -J cdk2_min
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

###############################
# Minimización solvente

minimizacion() {
	$AMBERHOME/bin/pmemd.cuda -O -i ./1_min/min_solv.in -o ./1_min/"$1"_min_solv.out -p ./"$1".prmtop -c ./"$1".rst7 -ref ./"$1".rst7 -r ./1_min/"$1"_min_solv.rst7 -inf "$1"_min_solv.mdinfo
	wait
	# Análisis 1 min_solv
	process_mdout.perl ./1_min/"$1"_min_solv.out
	mkdir ./1_min/"$1"_min_solv
	mv summary* ./1_min/"$1"_min_solv
	wait
	# Minimización total
	$AMBERHOME/bin/pmemd.cuda -O -i ./1_min/min_all.in -o ./1_min/"$1"_min_all.out -p ./"$1".prmtop -c ./1_min/"$1"_min_solv.rst7 -r ./1_min/"$1"_min_all.rst7 -inf "$1"_min_all.mdinfo
	wait
	# Análisis 2 min_solv
	process_mdout.perl ./1_min/"$1"_min_all.out
	mkdir ./1_min/"$1"_min_all
	mv summary* ./1_min/"$1"_min_all
	wait
	# Para covertir el rst a pdb
	cpptraj -p ./"$1".prmtop -c ./1_min/"$1"_min_all.rst7 -y ./1_min/"$1"_min_all.rst7 -x ./1_min/"$1"_min.pdb -i protein_cpptraj.in
}


############################################
# EJECUCION

EXC_DIR='..'

for i in */;
do 
cd $i;
minimizacion $i;
cd $EXC_DIR;
done


