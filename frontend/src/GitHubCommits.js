import React, { useEffect, useState } from "react";
import "./GitHubCommits.css";

const GitHubCommits = ({ username }) => {
  const [commitData, setCommitData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCommits = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch user repositories
        const reposRes = await fetch(`https://api.github.com/users/${username}/repos`);
        if (!reposRes.ok) {
          throw new Error(`GitHub API error: ${reposRes.status}`);
        }
        const repos = await reposRes.json();
        
        // Filter to only include non-forked repositories
        const filtered = repos
          .filter(repo => !repo.fork)
          .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
          .slice(0, 5); // Limit to 5 most recently updated repos

        if (filtered.length === 0) {
          throw new Error("No repositories found");
        }

        const commitCounts = {};

        // Fetch commits for each repository
        for (const repo of filtered) {
          try {
            const commitsRes = await fetch(
              `https://api.github.com/repos/${username}/${repo.name}/commits?per_page=100`
            );
            
            if (!commitsRes.ok) {
              console.warn(`Skipping repo ${repo.name} due to error`);
              continue;
            }
            
            const commits = await commitsRes.json();
            
            for (const commit of commits) {
              if (commit.commit?.author?.date) {
                const date = new Date(commit.commit.author.date).toISOString().split("T")[0];
                commitCounts[date] = (commitCounts[date] || 0) + 1;
              }
            }
          } catch (repoError) {
            console.error(`Error processing repo ${repo.name}:`, repoError);
          }
        }

        setCommitData(commitCounts);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching GitHub data:", err);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchCommits();
    }
  }, [username]);

  const getMonthLabels = () => {
    const today = new Date();
    const months = [];
    
    for (let i = 0; i < 5; i++) {
      const date = new Date(today);
      date.setMonth(today.getMonth() - i);
      months.push(date.toLocaleString('default', { month: 'short' }));
    }
    
    return months.reverse();
  };

  const renderGrid = () => {
    const today = new Date();
    const days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (29 - i)); // Show last 30 days
      const iso = date.toISOString().split("T")[0];
      return {
        date: iso,
        count: commitData[iso] || 0,
      };
    });

    return (
      <>
        <div className="commit-grid">
          {days.map(({ date, count }, i) => (
            <div
              key={i}
              title={`${date}: ${count} commit${count !== 1 ? "s" : ""}`}
              className={`commit-day ${
                count >= 10 
                  ? "very-high" 
                  : count >= 5 
                    ? "high" 
                    : count >= 2 
                      ? "medium" 
                      : count >= 1 
                        ? "low" 
                        : ""
              }`}
            />
          ))}
        </div>
        <div className="month-labels">
          {getMonthLabels().map((month, i) => (
            <span key={i}>{month}</span>
          ))}
        </div>
        <div className="legend">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#ebedf0" }} />
            <span>No commits</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#9be9a8" }} />
            <span>1-2</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#40c463" }} />
            <span>2-5</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#30a14e" }} />
            <span>5-10</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#216e39" }} />
            <span>10+</span>
          </div>
        </div>
      </>
    );
  };

  if (loading) {
    return <div className="loading">Loading GitHub activity...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="dashboard">
      <h3>📊 GitHub Activity for {username}</h3>
      {renderGrid()}
    </div>
  );
};

export default GitHubCommits;