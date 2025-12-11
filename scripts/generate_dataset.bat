@echo off
cd /d "%~dp0\.."
set PYTHONPATH=src

REM Generate the full dataset (100 instances per combination of n, k, p)
REM This creates graphs for n=[50,100,150,200,300,400,500,600,700,800,900,1000]
REM k=[2,3,4], p=[0.05,0.1,0.2,0.3]
REM Total: 12 * 3 * 4 * 100 = 14,400 graph instances

echo Generating dataset...
echo This will create ~14,400 graph instances and may take several minutes.
echo.

python -m comp6651.main --prepare-dataset --dataset-dir data/dataset/ --N_dataset 100 --seed 917

echo.
echo Dataset generation complete!
echo Files stored in data/dataset/
