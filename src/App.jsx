import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [apiMessage, setApiMessage] = useState('')

  const [signToTextResult, setSignToTextResult] = useState('');
  const [textToSignResult, setTextToSignResult] = useState('');
  const [signToTextLoading, setSignToTextLoading] = useState(false);
  const [textToSignLoading, setTextToSignLoading] = useState(false);

  // Video recording state
  const [recording, setRecording] = useState(false);
  const [videoURL, setVideoURL] = useState('');
  const [videoBlob, setVideoBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((res) => res.json())
      .then((data) => setApiMessage(data.message))
      .catch(() => setApiMessage('Could not connect to backend.'))
  }, [])

  // Handler for sign-to-text form
  const handleSignToText = async (e) => {
    e.preventDefault();
    setSignToTextResult('');
    setSignToTextLoading(true);
    const fileInput = e.target.elements[0];
    if (!fileInput.files[0]) {
      setSignToTextResult('Please select a file.');
      setSignToTextLoading(false);
      return;
    }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    try {
      const res = await fetch('http://127.0.0.1:8000/predict-gloss', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setSignToTextResult(data.result?.gloss || data.result || 'No result');
    } catch (err) {
      setSignToTextResult('Error connecting to backend.');
    }
    setSignToTextLoading(false);
  };

  // Handler for text-to-sign form
  const handleTextToSign = async (e) => {
    e.preventDefault();
    setTextToSignResult('');
    setTextToSignLoading(true);
    const textInput = e.target.elements[0];
    if (!textInput.value) {
      setTextToSignResult('Please enter text.');
      setTextToSignLoading(false);
      return;
    }
    const formData = new FormData();
    formData.append('text', textInput.value);
    try {
      const res = await fetch('http://127.0.0.1:8000/text-to-sign', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setTextToSignResult(data.result || 'No result');
    } catch (err) {
      setTextToSignResult('Error connecting to backend.');
    }
    setTextToSignLoading(false);
  };

  // Start recording
  const startRecording = async () => {
    setVideoURL('');
    setVideoBlob(null);
    setRecording(true);
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
    mediaRecorderRef.current = new window.MediaRecorder(stream);
    const chunks = [];
    mediaRecorderRef.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setVideoBlob(blob);
      setVideoURL(URL.createObjectURL(blob));
      stream.getTracks().forEach(track => track.stop());
    };
    mediaRecorderRef.current.start();
  };

  // Stop recording
  const stopRecording = () => {
    setRecording(false);
    mediaRecorderRef.current.stop();
  };

  // Upload recorded video
  const handleVideoUpload = async () => {
    if (!videoBlob) return;
    setSignToTextResult('');
    setSignToTextLoading(true);
    const formData = new FormData();
    formData.append('file', videoBlob, 'recorded.webm');
    try {
      const res = await fetch('http://127.0.0.1:8000/predict-gloss', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setSignToTextResult(data.result?.gloss || data.result || 'No result');
    } catch (err) {
      setSignToTextResult('Error connecting to backend.');
    }
    setSignToTextLoading(false);
  };

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">Sign ↔ Text</h1>
        <p className="subtitle">Bidirectional Translation</p>
      </header>
      <main>
        <section className="hero">
          <div className="hero-content">
            <h2 className="hero-title">Welcome to Deafference MVP</h2>
            <p className="hero-desc">Easily translate sign language to text by recording a video. Start by clicking the button below!</p>
          </div>
        </section>
        <section className="sign-to-text">
          <h2>Sign-to-Text</h2>
          <h3>Let's Record a Video!</h3>
          <div className="video-controls">
            <video ref={videoRef} autoPlay muted width={320} height={240} className="video-preview" />
            <div className="record-buttons">
              {!recording && <button className="btn" onClick={startRecording}>🎥 Start Recording</button>}
              {recording && <button className="btn stop" onClick={stopRecording}>⏹️ Stop Recording</button>}
            </div>
          </div>
          {videoURL && (
            <div className="video-upload">
              <video src={videoURL} controls width={320} height={240} className="video-preview" />
              <button className="btn upload" onClick={handleVideoUpload} disabled={signToTextLoading}>
                {signToTextLoading ? 'Uploading...' : 'Upload & Translate'}
              </button>
            </div>
          )}
          {signToTextResult && <div className="result"><strong>Result:</strong> <pre>{signToTextResult}</pre></div>}
        </section>
      </main>
      <footer className="footer">
        <p>Made with <span style={{color: '#61dafb'}}>Deafference</span>.</p>
      </footer>
    </div>
  )
}

export default App
