import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import './ScoreBreakdownChart.css';

const ScoreBreakdownChart = ({ scores, chartType = 'pie' }) => {
  if (!scores) {
    return (
      <div className="score-breakdown-empty">
        <p>No score data available</p>
      </div>
    );
  }

  // Prepare data for pie chart
  const pieData = [
    { name: 'Skills', value: scores.skill_score || 0, color: '#8884d8' },
    { name: 'Experience', value: scores.experience_score || 0, color: '#82ca9d' },
    { name: 'Education', value: scores.education_score || 0, color: '#ffc658' },
    { name: 'Match', value: scores.match_score || 0, color: '#ff7300' }
  ].filter(item => item.value > 0);

  // Prepare data for bar chart
  const barData = [
    { category: 'Skills', score: scores.skill_score || 0 },
    { category: 'Experience', score: scores.experience_score || 0 },
    { category: 'Education', score: scores.education_score || 0 },
    { category: 'Match', score: scores.match_score || 0 },
    { category: 'Overall', score: scores.overall_score || 0 }
  ];

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00'];

  return (
    <div className="score-breakdown-chart">
      <h3>Score Breakdown</h3>
      
      {chartType === 'pie' ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="score" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      )}

      <div className="score-summary">
        <div className="score-item">
          <span className="score-label">Overall Score:</span>
          <span className="score-value">{scores.overall_score?.toFixed(1) || 'N/A'}%</span>
        </div>
        <div className="score-details">
          <div className="detail-item">
            <span>Skills:</span>
            <span>{scores.skill_score?.toFixed(1) || 'N/A'}%</span>
          </div>
          <div className="detail-item">
            <span>Experience:</span>
            <span>{scores.experience_score?.toFixed(1) || 'N/A'}%</span>
          </div>
          <div className="detail-item">
            <span>Education:</span>
            <span>{scores.education_score?.toFixed(1) || 'N/A'}%</span>
          </div>
          <div className="detail-item">
            <span>Match:</span>
            <span>{scores.match_score?.toFixed(1) || 'N/A'}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreBreakdownChart;

