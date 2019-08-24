# Computer Vision Brain CT Scans  
Repo for a Computer Vision project to detect abnormatlities in brain CT scans.  
Link to website and original study: [Qure.ai](http://headctstudy.qure.ai/#dataset)

## Download the Dataset  
Total size of all downloaded zip folder is roughly 80-90GB  
The urls for the downloads are found in `docs/cq500_files.txt`  

Run one of these commands from bash or zsh.  If you are using OSX you can use install wget with  
```bash
brew install wget
```
Then run:
```bash
wget -i cq500_files.txt # If you have wget
aria2c -x5 -i cq500_files.txt # If you have aria2, recommended
```
