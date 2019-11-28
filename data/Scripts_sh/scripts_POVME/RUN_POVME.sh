i#!/bin/bash
#BSUB -P project
#BSUB -J POVME_RICCI
#BSUB -a openmpi
#BSUB -n 128
#BSUB -q q_hpc
#BSUB -oo out_ricc.out
#BSUB -eo err_ricc.err

module purge
module load intel/2017_update4

# ambiente de python para ejecutar POVME
source /tmpu/aguila_g/aguila/joel_ricci/POV/miniconda2/bin/activate
start=`date +%s`

# PARÁMETROS
numCores=128

inputPDB=cdk2_crys_ensamble_385_TOTAL_RICCI.pdb
outputDir=./CDK2_VOL_RICCI
GridSpacing=1.0

sphCenterX=-11.7
sphCenterY=207.3
sphCenterZ=113.8

sphereRadius=12.0
seedSphRadius=4.0

ConvexHullExclusion=first

#*********** EJECUCIÓN ***********#
# Otros parámetros pueden ser modificados directamente
cat > ex_povme3_$LSB_JOBID.tcl << EOF
# Nombre de la trayectoria en formato pdb
PDBFileName                     $inputPDB

# Resolucion (tamaño de las sondas en A)
GridSpacing                     $GridSpacing
# Datos de la esfera de inclusión (centor X Y Z y radio en A)
InclusionSphere         $sphCenterX     $sphCenterY     $sphCenterZ     $sphereRadius

# CRITERIOS DE DEFINICIÓN DE LA CAVIDAD
DistanceCutoff                          1.09
# Método de exclusión automático que determina donde acaba el pocket
ConvexHullExclusion                     $ConvexHullExclusion
# Se dfine una esfera menor, que indica cual es la cavidad principal
# en caso de que un frame muestre cavidades discontinuas, así POVME
# sólo mide la principal
SeedSphere      $sphCenterX     $sphCenterY     $sphCenterZ     $seedSphRadius
# Número de puntos en común que determina si dos cavidades son continuas (una sola)
ContiguousPointsCriteria        3

# EJECUCIÓN
NumProcessors               $numCores
OutputFilenamePrefix        $outputDir/res_
EOF

# Ejecución
POVME3.py ex_povme3_$LSB_JOBID.tcl
wait
mv ex_povme3_$LSB_JOBID.tcl $outputDir/
cat > ex_time_$LSB_JOBID.txt << EOF
"Duration: $((($(date +%s)-$start)/60)) minutes"
EOF
mv ex_time_$LSB_JOBID.txt $outputDir/
wait
# Comprime los resultados
cd $outputDir/
mkdir res_trajectories
mv res_*pdb res_trajectories

tar -zcvf res_frameInfo.tar.gz res_frameInfo/
rm -r res_frameInfo/
wait
tar -zcvf res_trajectories.tar.gz res_trajectories/
rm -r res_trajectories/


 
