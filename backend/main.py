from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import openai
import json

app = FastAPI()

PROJECT_ROOT = Path("projects")
PROJECT_ROOT.mkdir(exist_ok=True)

# Configure OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/create-project")
async def create_project(request: Request):
    data = await request.json()
    name = data.get("name", "default_project")
    folders = data.get("folders", ["src", "tests", "docs"])
    
    project_path = PROJECT_ROOT / name
    project_path.mkdir(exist_ok=True)
    for folder in folders:
        (project_path / folder).mkdir(parents=True, exist_ok=True)
    return {"status": "created", "project": name}

@app.post("/generate-code")
async def generate_code(request: Request):
    data = await request.json()
    prompt = data["prompt"]
    language = data.get("language", "python")

    messages = [
        {"role": "system", "content": f"You are a senior {language} developer."},
        {"role": "user", "content": prompt},
    ]
    
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return {"code": completion.choices[0].message.content}

@app.post("/write-file")
async def write_file(request: Request):
    data = await request.json()
    file_path = PROJECT_ROOT / data["project"] / data["relative_path"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(data["content"])
    return {"status": "file written", "path": str(file_path)}

@app.get("/read-file")
async def read_file(project: str, relative_path: str):
    file_path = PROJECT_ROOT / project / relative_path
    if not file_path.exists():
        return {"error": "File not found"}
    with open(file_path, "r") as f:
        return {"content": f.read()}

@app.get("/list-files")
async def list_files(project: str):
    project_path = PROJECT_ROOT / project
    file_list = []
    for path in project_path.rglob("*"):
        if path.is_file():
            file_list.append(str(path.relative_to(project_path)))
    return {"files": file_list}
