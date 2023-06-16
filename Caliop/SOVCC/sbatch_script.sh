#!bin/bash
#SBATCH --partition=par-single
#SBATCH --job-name=caliop_ash
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --time=15:00:00
#SBATCH --mem=32000

YEAR=$1
python ash_thickness_extraction_v2.py $YEAR