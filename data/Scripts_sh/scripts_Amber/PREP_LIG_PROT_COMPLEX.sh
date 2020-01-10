
# PARSER
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
	-p|--protein)
	PROT="$2"
    shift # past argument
    shift # past value
    ;;

    -l|--ligand)
	LIG="$2"
	shift # past argument
    shift # past value
    ;;
	-i|--ion)
	ION="$2"
	shift # past argument
    shift # past value
    ;;
    *)
    POSITIONAL+=("$1") 
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" 
	

#**********************************************
# CARGA DEL LIGANDO
cat > GET_CHARGE.py << EOF
from chimera import openModels, Molecule
from AddCharge import estimateNetCharge
from OpenSave import osOpen
from chimera import runCommand as rc

# Carga estimada de cada ligando
output_names = osOpen("./carga_lig.txt", "w")
#output_charge = osOpen("./carga.txt", "w")

for m in openModels.list(modelTypes=[Molecule]):
	rc("addh")
	rc("write %d  %s" % (m.id, str(m.name)))
	print>>output_names, m, m.name, estimateNetCharge(m.atoms)
	#print>>output_charge, estimateNetCharge(m.atoms)        
	print m.name, estimateNetCharge(m.atoms)
#output_charge.close()
output_names.close()
EOF

#*********************************************
# Agregar hidrógenos con chimera y obtiene la carga neta del ligando
/home/joel/.local/UCSF-Chimera64-1.14rc/bin/chimera --nogui --nostatus --script GET_CHARGE.py $LIG
wait
# Obtiene el valor de la carga
lig_name=${LIG%%.*}
x=`grep $lig_name carga_lig.txt`
CHAR=${x##* }

# ********************************************
# Crea el script de LeAP 1
cat > leap_prep1.in << EOF
source leaprc.gaff
loadamberparams LIG.frcmod
LIG = loadmol2 LIG.mol2 
saveoff LIG LIG.lib 
quit
EOF

# ********************************************
# Crea el script de LeAP 2
cat > leap_prep2.in << EOF
source leaprc.gaff
source leaprc.protein.ff14SB

loadoff atomic_ions.lib #Load the library for atomic ions
#loadamberparams frcmod.ions1lsm_hfe_tip3p #Load the frcmod file for monovalent metal ions

source leaprc.water.tip3p
loadamberparams LIG.frcmod

#CARGAR LIBRERIA DEL LIGANDO
loadoff LIG.lib
#CREACION DE COMPLEJO
protein=loadpdb ./$PROT
LIG = loadmol2 LIG.mol2
mol = combine {protein LIG}

savepdb mol ${PROT%%.pdb}-LIG.pdb
charge mol # Te da la carga de la molecula
#****** Solvatar
solvateOct mol TIP3PBOX 12
#****** Neutralizar
addions mol $ION 0 
#****** Si la carga es negativa, agrega Cl
#****** Guardar los parametros
saveamberparm mol ${PROT%%.pdb}_LIG.prmtop ${PROT%%.pdb}_LIG.rst7
quit
EOF


#PARAMETRIZACION DE LIGANDO
#CALCULO DE CARGAS CON METODO AM1
echo '------------'
echo $lig_name
antechamber -i $LIG -fi mol2 -o LIG.mol2 -fo mol2 -c bcc -s 2 -rn LIG -nc $CHAR
#BUSQUEDA DE PARAMETROS FALTANTES
# actualizado para ejecutar parmchk2
parmchk2 -i LIG.mol2 -f mol2 -o LIG.frcmod
#CREACION DE LIBRERIA LIG.LIB
tleap -f leap_prep1.in
#CREACION DE ARCHIVO DE PARAMETROS CON LA PROTEINA
tleap -f leap_prep2.in

mkdir PREPARACION_outputs
mv ANTECHAMBER* ATOMTYPE* carga_lig* leap* LIG* PREPARACION_outputs
rm sqm* GET_CHARGE*