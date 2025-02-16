# TrailArt

## Introduction
TrailArt: Generate a route on the map based on the prompt words

## Expected results
Enter the prompt words, and the system will generate a related route on the map. People can walk along it and generate a walking trajectory.

![Expected results](docs/images/expected_results.png)

## Architecture
![Architecture](docs/images/architecture.png)


## Setup

### 1.Clone source code
```
git clone https://github.com/sunmh207/trail-art.git
cd trail-art
```

### 2.  Install dependent packages
```
pip install -r requirements.txt
```

### 3.  Download chinese-clip-vit-base-patch16

Download https://huggingface.co/OFA-Sys/chinese-clip-vit-base-patch16 and put it in the `models` folder.

### 3.  Run
```
python app.py
```
Select the action number to be performed

1.Traverse all paths on the map and save them as images.

2.Generate a route based on the prompt words.

3.Generate a walking trajectory based on the generated route.

You need to execute in order.
## Notes
This is just an experimental project. It only provides an idea and basic code. It has not yet achieved the expected results. Everyone is welcome to provide comments and suggestions.