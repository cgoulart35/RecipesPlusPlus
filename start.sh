#!/bin/sh

#cd <INSERT-YOUR-PATH-HERE>/RecipesPlusPlus

python 'RecipesPlusPlusApi/api.py' &
python 'RecipesPlusPlusWebApp/app.py' &
