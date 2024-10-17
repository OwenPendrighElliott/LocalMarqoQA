# Local Marqo Q&A

This project is a small demo of a knowledge question and answering system that uses Marqo with LLaMa to perform question answering. This can run locally on an M1 or M2 Mac or with a CUDA capable GPU on linux or windows. If you want to run this on an M1 or M2 Mac please be sure to have the ARM64 version of Python installed, this will make `llama.cpp` builds for ARM64 and utilises Metal for inference rather than building for an x86 CPU and being emulated with Rosetta.

## Project Structure

### `frontend/`

This folder contains the code for the frontend of the application, the frontend is written with NextJS and TypeScript.

### `backend/`

This folder contains the backend code, the backend is written as a webserver using flask.

## Running for development

### Frontend

```
cd frontend
npm i
npm run dev
```

### Backend

You will need to get the models to run this locally. If you have 16GB of RAM I recommend starting with 7B parameter LLaMa GGML models, 13B parameter models do work but you must limit the memory usage of Marqo with Docker and remove the ViT-L/14 model from the pre-loading. 32GB RAM will give you enough headroom for 13B or potentially more.

There are a number of models that are commented out in the code, you can find them on hugging face by searching the name. I recommend starting with [llama-2-7b-chat.Q4_K_M.gguf](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main).

Download the model and place it in a new directory `backend/models/7B/`.

#### Install Dependencies
```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Download NLTK Data
```
python3
```
```python
import nltk
nltk.download("all")
```

#### Run the Webserver
```
python3 -m flask run --debug -p 5001
```

### Run Marqo

```bash
docker run --name marqo -it -p 8882:8882 marqoai/marqo:2.12
```

If you have a GPU then you should add the `--gpus all` flag to the docker run command.

```bash
docker run --name marqo -it -p 8882:8882 --gpus all marqoai/marqo:2.12
```

## Formatting code

### Frontend

```
cd frontend
npm run format
```

### Backend

```
cd backend
black .
```
