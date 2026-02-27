import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [flights, setFlights] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const flightRes = await api.get('/flights');
        const bookingRes = await api.get('/bookings');
        setFlights(flightRes.data);
        setBookings(bookingRes.data);
      } catch (err) {
        console.error('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };
    if (user) fetchData();
  }, [user]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="flex justify-between items-center bg-white p-4 shadow mb-6 rounded-lg">
        <h1 className="text-2xl font-bold text-gray-800">DS Airlines</h1>
        <div>
          <span className="mr-4 text-gray-600">Welcome, {user?.fullname}</span>
          <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition">Logout</button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-primary">Available Flights</h2>
          <ul className="space-y-4">
            {flights.map((flight) => (
              <li key={flight.unique_code} className="border-b pb-2 flex justify-between items-center">
                <div>
                  <div className="font-bold">{flight.departure} → {flight.destination}</div>
                  <div className="text-sm text-gray-500">{flight.date} at {flight.time}</div>
                  <div className="text-sm font-semibold text-accent">${flight.cost}</div>
                </div>
                <button
                  onClick={async () => {
                    try {
                        await api.post('/bookings', {
                            flight_code: flight.unique_code,
                            full_name: user.fullname,
                            passport_num: user.passport_num,
                            credit_card: '1234567812345678' // Mocking input for quick demo
                        });
                        alert('Booking successful!');
                        window.location.reload();
                    } catch (e) {
                        alert(e.response?.data?.detail || 'Booking failed');
                    }
                  }}
                  className="bg-secondary text-white px-3 py-1 rounded hover:bg-green-600 text-sm"
                >
                  Book
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-primary">My Bookings</h2>
          {bookings.length === 0 ? <p className="text-gray-500">No bookings yet.</p> : (
            <ul className="space-y-4">
              {bookings.map((booking) => (
                <li key={booking._id} className="border-b pb-2 flex justify-between items-center">
                  <div>
                    <div className="font-bold">{booking.departure} → {booking.destination}</div>
                    <div className="text-sm text-gray-500">{booking.flight_date}</div>
                  </div>
                  <button
                    onClick={async () => {
                        if (confirm('Cancel booking?')) {
                            await api.delete(`/bookings/${booking._id}`);
                            window.location.reload();
                        }
                    }}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Cancel
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
