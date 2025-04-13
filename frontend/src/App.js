// src/App.js
import React, { useEffect, useState } from "react";
import "./App.css";
import VisualizationPanel from "./VisualizationPanel";

import Confetti from "react-confetti";

const motivationalQuotes = [
    "You got this! 💪",
    "Take a breath and crush the next bug 🐛",
    "Remember to blink! 👀",
    "Every great developer was once a beginner.",
    "Stretch it out! You've earned it. 🧘‍♂️"
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
    const [showWaterPopup, setShowWaterPopup] = useState(false);
    const [journalEntries, setJournalEntries] = useState([]);
    const [newJournal, setNewJournal] = useState("");
    const [showJournalHistory, setShowJournalHistory] = useState(false);
    const [currentSong, setCurrentSong] = useState(null);
    const [showSpotifyPlayer, setShowSpotifyPlayer] = useState(false);
    const [motivationalQuotes, setMotivationalQuotes] = useState([]);
    const [cameraOn, setCameraOn] = useState(false);

    const spotifyTracks = [
        "https://open.spotify.com/embed/track/3sK8wGT43QFpWrvNQsrQya", // DTMF
        "https://open.spotify.com/embed/track/6koKhrBBcExADvWuOgceNZ", // Open Arms
        "https://open.spotify.com/embed/track/0o9ivTBX7mjTnaUYF4Gk6t", // The Imitation Game
        "https://open.spotify.com/embed/track/3ATRPvWFMu2F1U8b1Bh7ep", // Ceiling Games
        "https://open.spotify.com/embed/track/5rpCUsEfBLIumvrxrahnKF"  // Wishes
    ];

    useEffect(() => {
        fetch("http://127.0.0.1:5000/api/burnout")
          .then((res) => res.json())
          .then((data) => {
            if (data.burnout_score !== undefined) {
              setBurnout(data.burnout_score); // 👈 sets the initial burnout level
              console.log("🔥 Burnout score loaded from backend:", data.burnout_score);
            } else {
              console.warn("⚠️ No burnout_score found in response:", data);
            }
          })
          .catch((err) => {
            console.error("❌ Failed to fetch burnout score:", err);
          });
      }, []);
      
    useEffect(() => {
        const fetchQuotes = async () => {
          try {
            const response = await fetch("http://127.0.0.1:5000/api/quotes");
            const data = await response.json();
            const quotesOnly = (data.funny_burnout_quotes || []).map(q => q.quote);
            console.log("✅ Quotes only:", quotesOnly);
            quotesOnly.forEach(q => motivationalQuotes.push(q));
            console.log("✅ Motivational Quotes:", motivationalQuotes);
          } catch (error) {
            console.error("Error fetching from /api/quotes:", error);
          }
        };
      
        fetchQuotes();
      }, []);

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
        setShowWaterPopup(true);
        setBurnout(prev => Math.max(prev - 1, 0));
        setTimeout(() => setShowWaterPopup(false), 3000);
    };

    const handleMotivation = () => {
        const random = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];
        setBurnout(prev => Math.max(prev + 3, 0));
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
            setTimeout(() => setShowConfetti(false), 6000);
        }
    };

    const deleteTask = (index) => {
        const updatedTasks = [...tasks];
        updatedTasks.splice(index, 1);
        setTasks(updatedTasks);
    };

    const toggleMusic = () => {
        if (showSpotifyPlayer) {
            // If it's already showing, hide it
            setShowSpotifyPlayer(false);
            setCurrentSong(null);
            setIsPlayingMusic(false); // music is not playing
        } else {
            // Otherwise, pick a random song and show it
            const randomIndex = Math.floor(Math.random() * spotifyTracks.length);
            setCurrentSong(spotifyTracks[randomIndex]);
            setShowSpotifyPlayer(true);
            setIsPlayingMusic(true); // music not playing
        }
        // const audio = document.getElementById("calmMusic");
        // if (isPlayingMusic) {
        //     audio.pause();
        // } else {
        //     audio.play();
        // }
        // setIsPlayingMusic(!isPlayingMusic);
    };

    const handleCamera = async () => {
        const action = cameraOn ? "stop" : "start";
      
        try {
          const res = await fetch("http://127.0.0.1:5000/api/toggle-camera", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ action })
          });
      
          const data = await res.json();
          console.log("📸 Camera response:", data);
      
          setCameraOn(!cameraOn); // toggle UI state
        } catch (err) {
          console.error("Error toggling camera:", err);
        }
      };

    return (
        <div className="App">
            <div className="top-bar">
                <h2 className="logo-text">🧠 Burnout Buddy</h2>
            </div>

            <div className="main-layout">
                <div className={`left-panel ${showGame ? 'with-game' : ''}`}>
                    {/* Hero section */}
                    <div className="hero-section row-layout">
                        <div className="hero-left">
                            <p className="tagline">
                                <span className="tag-main">Overworked? 💻</span><br />
                                <span className="tag-sub">Burnout Buddy’s got your back — hydration, vibes, and a 3D brain spa. ☕🧠</span>
                            </p>

                            <div className="burnout-meter">
                                Burnout Level: <span>{burnout}/100</span>
                                <div
                                    className="burnout-bar"
                                    style={{
                                        backgroundColor:
                                            burnout > 75 ? "red" : burnout > 50 ? "orange" : burnout > 25 ? "yellow" : "green",
                                        width: `${burnout}%`
                                    }}
                                />
                                <span style={{ fontSize: "1.5rem", display: "block", marginTop: "1rem" }}>
                                    {burnout > 75 ? "🔥 Send help" : burnout > 50 ? "😰 Hanging in there" : burnout > 25 ? "😌 Vibing" : "🕺 Thriving"}
                                </span>
                                <div className="burnout-details">
                                    <div className="burnout-tip">
                                        🌿 Tip: Since you're vibing, try a 3-minute breathing break to keep that energy flowing.
                                    </div>
                                    <button className="cta-button" onClick={handleMotivation}>🧘 Fix My Brain (Gently)</button>
                                </div>
                            </div>

                            {burnout > 80 && (
                                <div className="alert-box">
                                    🔥 Woah there! Might be time to touch grass 🌱
                                </div>
                            )}
                        </div>

                        <div className="splineWrapper">
                            <iframe
                                src="https://my.spline.design/miniroomremakecopyprogrammerroom-O554V1QxaQp9RyugP82jjp7B/"
                                width="100%"
                                height="100%"
                                title="3D Burnout Scene"
                            ></iframe>
                        </div>
                    </div>


                    {/* Floating Buttons */}
                    <div className="fab-group">
                       <button className="fab" onClick={handleCamera} title="Camera 📸">📸</button>
                        <button className="fab" onClick={handleDrinkWater} title="Water Reminder 💧">💧</button>
                        <button className="fab" onClick={handleMotivation} title="Motivational Quote ✨">✨</button>
                        <button className="fab" onClick={handleGameMode} title="Game Mode 🎮">🎮</button>
                        <button className="fab" onClick={() => setShowJournal(prev => !prev)} title="Journal 📓">📓</button>
                        <button className="fab" onClick={() => setShowTasks(prev => !prev)} title="Tasks 📋">📋</button>
                        <button className={`fab ${isPlayingMusic ? "playing" : ""}`} onClick={toggleMusic} title="Lo-fi saves lives 🎵">🎵</button>
                    </div>

                    {/* Journal */}
                    {showJournal && (
                        <div className="journal">
                            <div className="journal-header">
                                <h3 className="journal-title">📓 Journal Entry</h3>
                                <button className="close-btn" onClick={() => setShowJournal(false)}>✖️</button>
                            </div>

                            <textarea placeholder="How are you feeling today?" rows="6" />
                            <button onClick={() => {
                                if (newJournal.trim()) {
                                    setJournalEntries([...journalEntries, { text: newJournal, time: new Date().toLocaleString() }]);
                                    setNewJournal("");
                                    setShowJournal(false);
                                }
                            }}>Save</button>
                        </div>
                    )}

                    {/* Task List */}
                    {showTasks && (
                        <div className="tasks">
                            <div className="tasks-header">
                                <h3 className="tasks-title">📋 Task List</h3>
                                <button className="close-btn" onClick={() => setShowTasks(false)}>✖️</button>
                            </div>

                            <input
                                type="text"
                                value={newTask}
                                onChange={(e) => setNewTask(e.target.value)}
                                placeholder="New Task"
                            />
                            <button onClick={handleAddTask}>Add Task</button>

                            <ul>
                                {tasks.map((task, idx) => (
                                    <li key={idx}>
                                        <input type="checkbox" checked={task.done} onChange={() => toggleTask(idx)} /> {task.text}
                                        <button className="task-delete-btn" onClick={() => deleteTask(idx)}>✖️</button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {showJournalHistory && (
                        <div className="journal">
                            <div className="journal-header">
                                <h3 className="journal-title">📜 Journal History</h3>
                                <button className="close-btn" onClick={() => setShowJournalHistory(false)}>✖️</button>
                            </div>
                            <ul>
                                {journalEntries.map((entry, idx) => (
                                    <li key={idx} style={{ marginBottom: "1rem", textAlign: "left" }}>
                                        <strong>{entry.time}</strong><br />{entry.text}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}


                    {/* Quote Popup */}
                    {showQuoteBox && (
                        <div className="quote-popup">
                            <p>{quote}</p>
                            <button onClick={() => setShowQuoteBox(false)}>Close</button>
                        </div>
                    )}
                </div>

                {/* Game Panel */}
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

            {/* Music */}
            {showSpotifyPlayer && currentSong && (
                <div className="spotify-embed">
                    <iframe
                        style={{ borderRadius: "12px" }}
                        src={`${currentSong}?utm_source=generator`}
                        width="300"
                        height="80"
                        frameBorder="0"
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        loading="lazy"
                        title="Spotify Player"
                    ></iframe>
                </div>
            )}



            {/* Confetti */}
            {showConfetti && (
                <Confetti
                    width={windowDimensions.width}
                    height={windowDimensions.height}
                    numberOfPieces={500} // default is 200
                    recycle={false}      // only show once
                    gravity={0.3}         // controls fall speed
                    tweenDuration={8000} // animation duration
                />
            )}

            {showWaterPopup && (
                <div className="water-popup">
                    <strong>Time to hydrate!💧</strong><br />
                    Drink a glass of water. Your brain will thank you.
                </div>
            )}
            {/* Dashboard */}
      
    <div className="dashboard">
              <h3>📊 Visualizations</h3>
              <VisualizationPanel />          </div>
        </div>
    );
};

export default App;
