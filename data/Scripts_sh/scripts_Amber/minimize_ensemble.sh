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


# El directorio de trabajo
WDIR=`pwd`

# Ion a utilizar para la solvatacion
ION='Cl-'

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
	cpptraj -p ./"$1".prmtop -c ./1_min/"$1"_min_all.rst7 -y ./1_min/"$1"_min_all.rst7 -x ./1_min/"$1"_min.pdb -i ./1_min/protein_cpptraj.in
}

# para cada archivo PROT en la carpeta PREP_PH_7
for i in $WDIR/PREP_PH_7/*;
do
# Obtenemos el nombre del ligando
i=${i##*/}
i=${i%_*}
echo $i
# Se crean los directorios necesarios
mkdir $WDIR/EXECT/$i/
mkdir $WDIR/EXECT/$i/1_min

# Copiamos los archivos input a utilizar para procesar la porteina
cp $WDIR/*in $WDIR/EXECT/$i/1_min

# Copiamos el archivo de la proteína
cp $WDIR/PREP_PH_7/$i*pdb $WDIR/EXECT/$i

# Entramos al directorio de la proteina
cd $WDIR/EXECT/$i/
# Se crea el archivo tleap y cpptraj
cat > ./leap_prep.in << EOF
source leaprc.gaff
source leaprc.protein.ff14SB
loadoff atomic_ions.lib
source leaprc.water.tip3p

#Reading protein file
protein = loadpdb ./${i}_PROT.pdb
# Solvatation
solvateOct protein TIP3PBOX 12
# Neutralization
addions protein $ION 0
saveamberparm protein ${i}_PROT.prmtop ${i}_PROT.rst7
quit
EOF

# Se ejecuta tleap para generar el sistema
tleap -f ./leap_prep.in

# Se lleva a cabo la minimizacion
minimizacion "$i"_PROT
wait

# Al finalizar copia el pdb minimizado a MIN
cp ./1_min/*_min.pdb $WDIR/MIN/

# Volvemos al directorio de trabajo original
cd $WDIR
done