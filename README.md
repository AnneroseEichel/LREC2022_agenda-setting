### Investigating Independence vs. Control: Agenda-Setting in Russian News Coverage on Social Media

This is the supplementary material and companion code for the experiments reported in the paper:

"Investigating Independence vs. Control: Agenda-Setting in Russian News Coverage on Social Media" by Annerose Eichel, Gabriella Lapesa and Sabine Schulte im Walde (to be) published at LREC 2022.

The code allows users to reproduce the results reported in the paper and potentially extend the models to new datasets and configurations. Please cite the above paper when reporting, reproducing or extending the results.

### Setup
For setting up an environment, you can run the following commands:
```bash
conda create -n agenda-setting python=3.10 -y
conda activate agenda-setting
pip install -r requirements.txt
```

### Data
The used corpus is described in the following paper:

**Judina, Darja & Platonov, Konstantin. (2018). Measuring Agenda Setting and Public Concern in Russian Social Media**: 5th International Conference, INSCI 2018, St. Petersburg, Russia, October 24–26, 2018, Proceedings. 10.1007/978-3-030-01437-7_17. 

We are grateful to the authors for providing the dataset.

### Experiments
To run the experiments, please place the VK corpus CSV data file inside of code/data/.

Then, you can run the following commands to preprocess the posts and calculate metrics and percent change values.
```bash
bash code/src/utils/run_preprocessing.sh
bash code/src/utils/run_calculations.sh
```
To then run the correlation analysis experiments, you can use the following command:
```bash
bash code/src/analyses/correlation_analysis/run_correlation_analysis.sh
```

Lastly, to run the regression analysis, open the file in a corresponding IDE and run the notebook.

### Supplementary Material

The supplementary material includes additional results for the statistical analyses (*§4.1 Correlation Analysis* and *§4.2 Regression Analysis*). It also features a sample of the posts that serve as supportive material for the qualitative analysis (*§4.3 Qualitative Analysis*).

Specifically, the PDF file `supplementary_material.pdf` contains additional statistics and regression analysis results. 

A sample of the material used for the qualitative analyses can be found in the following file:
- A CSV file `(posts_ukraine_samples_with_translation.csv)` encompassing a sample portion of the posts (130 posts). Post texts are provided with English translations.
Note that for reasons of feasibility, the posts have been automatically pre-translated using Google translate and post-edited where necessary. In some cases, explanations have been added in squared brackets.  

The IDs specified in columns 1-3 `(ID, from_ID, owner_ID)` refer to VK IDs and encode the following:

VK ID        | News Outlet
-------------|-------------
`"-76982440`"| Meduza 
`"-25232578`"| RBC 
`"-40316705"`| Russia Today 
`"-26284064"`| TASS

Note that when downloading and viewing this data in a given editor, cyrillic characters might not be displayed correctly in every text editor.
Using an editor, where the encoding (UTF-8) can be specified, might aid in correctly displaying all characters. 

All posts are part of the VK corpus (for details, see _Data_).

### License
The above code is open-sourced under the AGPL-3.0 license. See the LICENSE file for details.

Note that the code in this repository was developed for research purposes only and will not be maintained. 
