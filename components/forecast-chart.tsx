import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { weatherApi, WeatherData } from '../lib/api-client';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ForecastChartProps {
  kiteSpotId: number;
  hours?: number;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ kiteSpotId, hours = 24 }) => {
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
    return <div className="p-4 text-center">Loading weather data...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  if (weatherData.length === 0) {
    return <div className="p-4 text-center">No weather data available</div>;
  }

  // Format data for chart
  const labels = weatherData.map(data => {
    const date = new Date(data.timestamp);
    return `${date.getHours()}:00`;
  });

  const windSpeedData = weatherData.map(data => data.wind_speed_10m);
  const temperatureData = weatherData.map(data => data.temperature);
  const humidityData = weatherData.map(data => data.humidity);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Wind Speed (m/s)',
        data: windSpeedData,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        yAxisID: 'y',
      },
      {
        label: 'Temperature (°C)',
        data: temperatureData,
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
        yAxisID: 'y1',
      },
      {
        label: 'Humidity (%)',
        data: humidityData,
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1,
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Wind Speed (m/s)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Temperature (°C) / Humidity (%)',
        },
      },
    },
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Weather Forecast</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}; 