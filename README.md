# Bitcamp2025

## Problem: 

As students juggling deadlines, hackathons, internships, and side projects, we’ve all felt the creeping burnout that’s hard to name but even harder to fight. Most mental
health apps felt too serious or clinical, we wanted something fun, light, and proactive. After too many late nights debugging and forgetting what sunlight looks like, we
realized burnout doesn’t announce itself, it just quietly takes over. We wanted to build something that could catch us slipping before we spiral, using the very data we
already generate: our steps, our sleep, our GitHub commits, and our tired faces. 


## Idea: 
Burnout Buddy became our goofy, 3D self-care sidekick, combining real-world signals, AI, and playful visuals to remind us to hydrate, vibe, and breathe before burnout hits too hard. Burnout Buddy is a personal wellbeing dashboard that tracks signs of burnout and helps you bounce back. It:

* Tracks physical and mental exhaustion using Fitbit data, GitHub commits, and real-time webcam fatigue detection.
* Calculates a personalized burnout score using sleep, steps, commits, and drowsiness levels.
* Offers timely interventions like hydration reminders, lo-fi Spotify tracks, and AI-generated motivational quotes.
* Provides journaling and task tracking to support mindful productivity.
* Visualizes burnout trends over time with interactive graphs.
* Encourages self-care before self-combustion — because burnout doesn’t announce itself, it just sneaks in.


## Stack: 
* Frontend: React.js with custom CSS for styling, Chart.js for data visualization, and Spline for 3D embedding. Didn't forget Confetti (because vibes).
* Backend: Flask API to serve burnout score, quotes (via Google Gemini API), Fitbit and GitHub data.
* Data Pipelines: Python scripts to fetch Fitbit step/sleep data and GitHub commits, stored in MongoDB atlas.
* Fatigue Detection: Real-time drowsiness detection using OpenCV, MediaPipe, and dlib for webcam-based eye tracking
* Database: MongoDB Atlas stores time-series Fitbit/GitHub data and user journal entries securely
* Spotify Integration: Lo-fi music player powered by randomized Spotify Web Player embeds
* Burnout Scoring: Custom burnout score calculated from sleep, activity, commits, and fatigue using a weighted formula


