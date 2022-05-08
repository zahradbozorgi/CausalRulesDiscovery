# Process Mining Meets Causal Machine Learning: Discovering Causal Rules from Event Logs

This repository contains the code for the experiments conducted in the article
"Process Mining Meets Causal Machine Learning: Discovering Causal Rules from Event Logs"
by Zahra Dasht Bozorgi, Irene Teinemaa, Marlon Dumas, Marcello La Rosa, and Artem Polyvyanyy.

## Setup

The dataset used for the experiment can be found [here](https://www.dropbox.com/sh/9agus6uvwp4plgh/AADe8ZXJipFQf_7x13osu9vza?dl=0).
They need to be added to the data folder.

Environment MacOS
```shell
conda env create -n CausalRulesDiscovery --file environment_macos.yml
conda activate CausalRulesDiscovery
```

Environment Windows
```shell
conda env create -n CausalRulesDiscovery --file environment_windows.yml
conda activate CausalRulesDiscovery
```


## Usage
To replicate the experiment with the default settings run:

```shell
python causal_rules.py
```

## Citation

If you find this code useful for your research, please use the following BibTeX entry.

```
@INPROCEEDINGS{9230023,
  author={Bozorgi, Zahra Dasht and Teinemaa, Irene and Dumas, Marlon and La Rosa, Marcello and Polyvyanyy, Artem},
  booktitle={2020 2nd International Conference on Process Mining (ICPM)}, 
  title={Process Mining Meets Causal Machine Learning: Discovering Causal Rules from Event Logs}, 
  year={2020},
  volume={},
  number={},
  pages={129-136},
  doi={10.1109/ICPM49681.2020.00028}}
}
```