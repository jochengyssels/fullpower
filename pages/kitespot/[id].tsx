import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { ForecastChart } from '../../components/forecast-chart';
import { GoldenTimeWindowChart } from '../../components/golden-time-window-chart';
import { weatherApi, KiteSpot } from '../../lib/api-client';

const KiteSpotPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [kiteSpot, setKiteSpot] = useState<KiteSpot | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchKiteSpot = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        // In a real app, you would have an API endpoint to get a single kitespot
        // For now, we'll fetch all kitespots and find the one with matching ID
        const kitespots = await weatherApi.getKiteSpots();
        const spot = kitespots.find(spot => spot.id === Number(id));
        
        if (spot) {
          setKiteSpot(spot);
          setError(null);
        } else {
          setError('Kitespot not found');
        }
      } catch (err) {
        console.error('Error fetching kitespot:', err);
        setError('Failed to load kitespot data');
      } finally {
        setLoading(false);
      }
    };

    fetchKiteSpot();
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center">Loading kitespot data...</div>;
  }

  if (error || !kiteSpot) {
    return <div className="p-8 text-center text-red-500">{error || 'Kitespot not found'}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{kiteSpot.name}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">Location</h2>
          <p>{kiteSpot.location}, {kiteSpot.country}</p>
          <p className="text-sm text-gray-600">Coordinates: {kiteSpot.latitude}, {kiteSpot.longitude}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">Details</h2>
          <p>Difficulty: {kiteSpot.difficulty || 'Not specified'}</p>
          <p>Water Type: {kiteSpot.water_type || 'Not specified'}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <ForecastChart kiteSpotId={kiteSpot.id} hours={24} />
        <GoldenTimeWindowChart kiteSpotId={kiteSpot.id} hours={24} />
      </div>
    </div>
  );
};

export default KiteSpotPage; 