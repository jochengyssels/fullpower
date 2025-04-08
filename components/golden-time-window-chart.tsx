import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { weatherApi, WeatherData } from '../lib/api-client';

interface GoldenTimeWindowChartProps {
  kiteSpotId: number;
  hours?: number;
}

export const GoldenTimeWindowChart: React.FC<GoldenTimeWindowChartProps> = ({ kiteSpotId, hours = 24 }) => {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        const data = await weatherApi.getKiteSpotWeather(kiteSpotId, hours);
        setWeatherData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching weather data:', err);
        setError('Failed to load weather data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, [kiteSpotId, hours]);

  if (loading) {
    return <div className="p-4 text-center">Loading golden window data...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  if (weatherData.length === 0) {
    return <div className="p-4 text-center">No weather data available</div>;
  }

  // Calculate golden window score (0-100) based on wind speed
  // Ideal wind speed is between 15-25 knots (7.7-12.9 m/s)
  const calculateGoldenWindowScore = (windSpeed: number): number => {
    if (windSpeed < 5) return 0; // Too light
    if (windSpeed > 30) return 0; // Too strong
    
    // Optimal range is 15-25 knots (7.7-12.9 m/s)
    if (windSpeed >= 7.7 && windSpeed <= 12.9) {
      return 100; // Perfect conditions
    }
    
    // Calculate score based on distance from optimal range
    if (windSpeed < 7.7) {
      return Math.round((windSpeed - 5) / (7.7 - 5) * 100);
    } else {
      return Math.round((30 - windSpeed) / (30 - 12.9) * 100);
    }
  };

  // Format data for chart
  const labels = weatherData.map(data => {
    const date = new Date(data.timestamp);
    return `${date.getHours()}:00`;
  });

  const goldenWindowScores = weatherData.map(data => 
    calculateGoldenWindowScore(data.wind_speed_10m)
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Golden Window Score',
        data: goldenWindowScores,
        backgroundColor: goldenWindowScores.map(score => {
          if (score >= 80) return 'rgba(75, 192, 192, 0.8)'; // Green for optimal
          if (score >= 50) return 'rgba(255, 206, 86, 0.8)'; // Yellow for good
          return 'rgba(255, 99, 132, 0.8)'; // Red for poor
        }),
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Golden Window Score (0-100)',
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const index = context.dataIndex;
            const windSpeed = weatherData[index].wind_speed_10m;
            return [
              `Score: ${context.parsed.y}`,
              `Wind Speed: ${windSpeed.toFixed(1)} m/s`,
            ];
          },
        },
      },
    },
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Golden Time Window</h2>
      <p className="text-sm text-gray-600 mb-4">
        Score based on optimal wind conditions (15-25 knots)
      </p>
      <Bar data={chartData} options={options} />
    </div>
  );
}; 