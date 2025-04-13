import React, { useEffect, useState } from "react";
import { Bar, Line } from "react-chartjs-2";
import "chart.js/auto";

const VisualizationPanel = () => {
  const [fitbitData, setFitbitData] = useState([]);
  const [githubData, setGithubData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/fitbit/sleep")
      .then((res) => res.json())
      .then((data) => setFitbitData(data))
      .catch((err) => console.error("Error fetching Fitbit data:", err));

    fetch("http://localhost:5000/api/github/commits")
      .then((res) => res.json())
      .then((data) => setGithubData(data))
      .catch((err) => console.error("Error fetching GitHub data:", err));
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const fitbitDates = fitbitData.map((d) => formatDate(d.date));
  const steps = fitbitData.map((d) => d.steps);
  const sleep = fitbitData.map((d) => d.totalMinutesAsleep);

  const githubDates = githubData.map((d) => formatDate(d.date));
  console.log("GitHub Dates:", githubDates);

  const commits = githubData.map((d) => d.commit_count);

  return (
    <div className="viz-grid">
      <div className="viz-card">
        <h4>GitHub Contributions</h4>
        <Line
          data={{
            labels: githubDates,
            datasets: [
              {
                label: "Commits",
                data: commits,
                borderColor: "#10b981",
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                tension: 0.3,
                fill: true,
              },
            ],
          }}
          options={{
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true },
              x: { reverse: true 
                ,
                ticks: {
                  maxRotation: 40,
                  minRotation: 40,
                },
              },
              
            },
          }}
        />
      </div>

      <div className="viz-card">
        <h4>Sleep Schedule (min)</h4>
        <Bar
          data={{
            labels: fitbitDates,
            datasets: [
              {
                label: "Sleep",
                data: sleep,
                backgroundColor: "#6366f1",
              },
            ],
          }}
          options={{
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true },
              x: { reverse: true 

                ,
                ticks: {
                  maxRotation: 40,
                  minRotation: 40,
                },
              },
              
            },
          }}
        />
      </div>

      <div className="viz-card full-width">
        <h4>Daily Steps</h4>
        <Bar
          data={{
            labels: fitbitDates,
            datasets: [
              {
                label: "Steps",
                data: steps,
                backgroundColor: "#22c55e",
              },
            ],
          }}
          options={{
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true },
              x: { reverse: true
                ,
                ticks: {
                  maxRotation: 40,
                  minRotation: 40,
                },

               },
            },
          }}
        />
      </div>
    </div>
  );
};

export default VisualizationPanel;
