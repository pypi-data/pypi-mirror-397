# vidrl-hiv
HIV analysis pipeline using Micall

<img width="2292" height="991" alt="HIV-MiCall-analysis" src="https://github.com/user-attachments/assets/0daf05dc-531f-4a56-9d5d-4c682663e1b7" />


## install

```
git clone https://github.com/abcdtree/vidrl-hiv.git
cd vidrl-hiv
conda env create -f conda.yaml
conda activate vidrl-hiv
pip install dist/vidrl_hiv-0.0.2.tar.gz
```

## Usage

> [!CAUTION]
> this pipeline only works on VIDRL dgx server

### Input

vidrl-hiv accept a folder of paired fastq files or a samplesheet.csv as input

samplesheet.csv

| #name | r1 | r2 | reference |
| :---: | :---: | :---:| :---:|
| sample1 | sample1_R1.fastq.gz | sample1_R2.fastq.gz | hxb2 |
| ... | ... | ... | ... |

### Run Command

```
vidrl-hiv samplesheet.csv --cpu 10 -maxjob 10
```


