
# Re-Addition Modeler

A python based GUI to model kinetic data that contains re-additions.


## Install
- make sure COPASI is installed (https://copasi.org/Download/)
- Create and activate a dedicated environment
- `pip install re_add_modeler`
- download and unzip 'python implementation of COPASI':
https://drive.google.com/file/d/1cVNLU4SBsz0JhC48MO69wVSLH-RpyIt6/view?usp=sharing
- OR clone github repo of 'python implementation of COPASI' `https://gitlab.com/heingroup/py_copasi`


- create a text file named `copasi_path.txt` in the folder you want to run the GUI from
- add the path to the previously downloaded 'python implementation of COPASI' to `copasi_path.txt`
- create a folder named `output` in the folder you want to run the GUI from
- open cmd in the folder you want to run the GUI from
- `python`
- `import re_add_modeler`

This should open the GUI. All relevant information will be stored in the previously created output folder sorted by date and time.

## How to use
- drag and drop csv files to be modeled into the csv field
- for re-additions either manually or from json click the additions button for the correct csv file
- type out mechanisms the names of the species must match the names in the csv file
- all non-zero starting concentrations need to be defined in the csv file (for unknow concentrations such as catalyst only give it the initial value and leave all other entries blank)
- to exclude a k-value from optimization (remove backwards reaction for irreversible processes) add a "$" in front of the known value
- add complete mechanisms with the "+" button on the top right

- switch to modeling tab on the top
- confirm the text box on the left does not indicate an error (it is red)
- set the species COPASI uses for fitting on the bottom right. Species names must match the names in the csv file separated by a comma (",")
- set number of generations and population size for COPASI to use on the bottom left
- click "Run Evaluation"
- wait for optimization to finish

- swap to results tab on the top
- click through data and mechanisms



## Known issues
- only accepts csv files and not excel for now
- deleting files you want to model on requires a restart of the GUI




