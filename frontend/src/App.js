// src/App.js
import React, { useEffect, useState } from "react";
import "./App.css";
import GitHubCalendar from "react-github-calendar";

import Confetti from "react-confetti";

const motivationalQuotes = [
  "You got this! 💪",
  "Take a breath and crush the next bug 🐛",
  "Remember to blink! 👀",
  "Every great developer was once a beginner.",
  "Stretch it out! You've earned it. 🧨‍♂️"
];

const App = () => {
  const [showConfetti, setShowConfetti] = useState(false);
  const [burnout, setBurnout] = useState(50);
  const [quote, setQuote] = useState("");
  const [windowDimensions, setWindowDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [tasks, setTasks] = useState([{ text: "Finish feature implementation", done: false }]);
  const [newTask, setNewTask] = useState("");
  const [showJournal, setShowJournal] = useState(false);
  const [showTasks, setShowTasks] = useState(false);
  const [showQuoteBox, setShowQuoteBox] = useState(false);
  const [isPlayingMusic, setIsPlayingMusic] = useState(false);
  const [showGame, setShowGame] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowDimensions({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const waterReminder = setInterval(() => {
      alert("💧 Time to drink water!");
      setBurnout(prev => Math.min(prev + 5, 100));
    }, 30 * 60 * 1000);

    return () => clearInterval(waterReminder);
  }, []);

  const handleDrinkWater = () => {
    alert("Nice! Hydration helps focus 🌊");
    setBurnout(prev => Math.max(prev - 10, 0));
  };

  const handleMotivation = () => {
    const random = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];
    setQuote(random);
    setShowQuoteBox(true);
  };

  const handleGameMode = () => {
    setShowGame(prev => !prev);
  };

  const handleAddTask = () => {
    if (newTask.trim()) {
      setTasks([...tasks, { text: newTask, done: false }]);
      setNewTask("");
    }
  };

  const toggleTask = (index) => {
    const updatedTasks = [...tasks];
    updatedTasks[index].done = !updatedTasks[index].done;
    setTasks(updatedTasks);
    if (updatedTasks[index].done) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    }
  };

  const deleteTask = (index) => {
    const updatedTasks = [...tasks];
    updatedTasks.splice(index, 1);
    setTasks(updatedTasks);
  };

  const toggleMusic = () => {
    const audio = document.getElementById("calmMusic");
    if (isPlayingMusic) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlayingMusic(!isPlayingMusic);
  };

  return (
    <div className="App">
      <div className="main-layout">
        <div className={`left-panel ${showGame ? 'with-game' : ''}`}>
          <div className="hero-section">
            <div className="splineWrapper">
              <iframe
                src="https://my.spline.design/miniroomremakecopyprogrammerroom-O554V1QxaQp9RyugP82jjp7B/"
                width="100%"
                height="100%"
                title="3D Burnout Scene"
              ></iframe>
            </div>

            <h1 className="animated-header">🧠 Burnout Buddy</h1>

            <div className="burnout-meter">
              Burnout Level: <span>{burnout}/100</span>
              <div className="burnout-bar" style={{ backgroundColor: burnout > 75 ? "red" : burnout > 50 ? "orange" : burnout > 25 ? "yellow" : "green" }} />
              <span role="img">
                {burnout > 75 ? "🙵‍♋️" : burnout > 50 ? "😰" : burnout > 25 ? "😌" : "😎"}
              </span>
            </div>
          </div>

          <div className="fab-group">
            <button className="fab" onClick={handleDrinkWater} title="Water Reminder">💧</button>
            <button className="fab" onClick={handleMotivation} title="Motivational Quote">✨</button>
            <button className="fab" onClick={handleGameMode} title="Game Mode">🎮</button>
            <button className="fab" onClick={() => setShowJournal(prev => !prev)} title="Journal">📓</button>
            <button className="fab" onClick={() => setShowTasks(prev => !prev)} title="Tasks">📋</button>
            <button className={`fab ${isPlayingMusic ? "playing" : ""}`} onClick={toggleMusic}>🎵</button>
          </div>

          {showJournal && (
            <div className="journal">
              <h3>📓 Journal Entry</h3>
              <textarea placeholder="How are you feeling today?" rows="6" cols="60" />
            </div>
          )}

          {showTasks && (
            <div className="tasks">
              <h3>📋 Task List</h3>
              <input type="text" value={newTask} onChange={(e) => setNewTask(e.target.value)} placeholder="New Task" />
              <button onClick={handleAddTask}>Add Task</button>
              <ul>
                {tasks.map((task, idx) => (
                  <li key={idx}>
                    <input type="checkbox" checked={task.done} onChange={() => toggleTask(idx)} /> {task.text}
                    <button onClick={() => deleteTask(idx)}>❌</button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {showQuoteBox && (
            <div className="quote-popup">
              <p>{quote}</p>
              <button onClick={() => setShowQuoteBox(false)}>Close</button>
            </div>
          )}
        </div>

        {showGame && (
          <div className="right-panel">
            <iframe
              id="subwayGame"
              src="https://subway-surfers.org/winter-holiday/"
              title="Subway Surfers"
              width="100%"
              height="100%"
              style={{ border: "none" }}
            ></iframe>
          </div>
        )}
      </div>

      <audio id="calmMusic" loop>
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>

      {showConfetti && (
        <Confetti width={windowDimensions.width} height={windowDimensions.height} />
      )}
      <div className="dashboard">
        <h3>📊 GitHub Contributions</h3>
        {/* <GitHubCalendar username="CSin007" /> */}

      </div>
    </div>
  );
};

export default App;
