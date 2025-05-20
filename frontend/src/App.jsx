import React, { useState, useEffect } from 'react';
import MonacoEditor from 'react-monaco-editor';
import axios from 'axios';
import './App.css';

function App() {
  const [project, setProject] = useState("sample_project");
  const [file, setFile] = useState("main.py");
  const [prompt, setPrompt] = useState("");
  const [code, setCode] = useState("");
  const [files, setFiles] = useState([]);

  const fetchFiles = async () => {
    const res = await axios.get(`http://localhost:8000/list-files?project=${project}`);
    setFiles(res.data.files);
  };

  const loadFile = async (filename) => {
    const res = await axios.get(`http://localhost:8000/read-file?project=${project}&relative_path=${filename}`);
    setFile(filename);
    setCode(res.data.content);
  };

  const handleGenerate = async () => {
    const res = await axios.post("http://localhost:8000/generate-code", {
      prompt: prompt,
      language: "python"
    });
    setCode(res.data.code);
  };

  const handleSave = async () => {
    await axios.post("http://localhost:8000/write-file", {
      project: project,
      relative_path: file,
      content: code
    });
    fetchFiles();
  };

  useEffect(() => {
    fetchFiles();
  }, [project]);

  return (
    <div className="ide-container">
      <div className="sidebar">
        <h2>Files</h2>
        <ul className="file-list">
          {files.map(f => (
            <li key={f} onClick={() => loadFile(f)}>{f}</li>
          ))}
        </ul>
        <hr />
        <h2>AI Tools</h2>
        <textarea
          placeholder="Enter your prompt to generate code..."
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
        />
        <button onClick={handleGenerate}>Generate</button>
        <button onClick={handleSave}>Save</button>
      </div>
      <div className="editor">
        <MonacoEditor
          height="100vh"
          width="100%"
          language="python"
          value={code}
          onChange={setCode}
        />
      </div>
    </div>
  );
}

export default App;
