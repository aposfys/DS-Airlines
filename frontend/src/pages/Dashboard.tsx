import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import { useNavigate } from 'react-router-dom';

interface Flight {
  unique_code: string;
  departure: string;
  destination: string;
  date: string;
  time: string;
  cost: number;
}

interface Booking {
  _id: string;
  flight_code: string;
  full_name: string;
  passport_num: string;
  departure: string;
  destination: string;
  flight_date: string;
}

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [flights, setFlights] = useState<Flight[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Search state
  const [departureSearch, setDepartureSearch] = useState('');
  const [destinationSearch, setDestinationSearch] = useState('');

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

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) return (
    <div className="min-h-screen bg-accent flex items-center justify-center">
      <div className="text-primary text-xl font-bold animate-pulse">Loading flights...</div>
    </div>
  );

  const filteredFlights = flights.filter(f => 
    f.departure.toLowerCase().includes(departureSearch.toLowerCase()) &&
    f.destination.toLowerCase().includes(destinationSearch.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-accent font-sans text-dark">
      {/* Navigation Bar */}
      <nav className="bg-primary text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0 flex items-center cursor-pointer">
              <span className="text-2xl font-bold tracking-wider">DS Airlines</span>
              <span className="ml-2 text-sm font-light uppercase opacity-80">Clone</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium">Welcome, {user?.fullname}</span>
              <button 
                onClick={handleLogout} 
                className="bg-transparent border border-white hover:bg-white hover:text-primary px-4 py-1.5 rounded-full text-sm font-semibold transition-colors duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-primary relative overflow-hidden pb-12 pt-8">
        <div className="absolute inset-0 opacity-10 bg-[url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')] bg-cover bg-center"></div>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 text-center shadow-sm">
            Where to next?
          </h1>
          
          {/* Search Widget */}
          <div className="bg-white rounded-xl shadow-float p-6 md:p-8 mt-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">From</label>
                <input 
                  type="text" 
                  placeholder="Departure city" 
                  className="w-full text-lg border-b-2 border-gray-200 focus:border-secondary focus:outline-none py-2 transition-colors text-primary font-semibold placeholder-gray-400"
                  value={departureSearch}
                  onChange={e => setDepartureSearch(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">To</label>
                <input 
                  type="text" 
                  placeholder="Destination city" 
                  className="w-full text-lg border-b-2 border-gray-200 focus:border-secondary focus:outline-none py-2 transition-colors text-primary font-semibold placeholder-gray-400"
                  value={destinationSearch}
                  onChange={e => setDestinationSearch(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          
          {/* Flights List */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-primary mb-6 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              Available Flights
            </h2>
            
            {filteredFlights.length === 0 ? (
              <div className="bg-white rounded-lg p-8 text-center text-gray-500 shadow-card">
                No flights found matching your search.
              </div>
            ) : (
              <div className="space-y-4">
                {filteredFlights.map((flight) => (
                  <div key={flight.unique_code} className="bg-white rounded-xl shadow-card p-6 flex flex-col sm:flex-row justify-between items-center hover:shadow-float transition-shadow duration-300 border border-gray-100">
                    <div className="flex-1 w-full mb-4 sm:mb-0">
                      <div className="flex items-center justify-between sm:justify-start mb-2">
                        <div className="text-2xl font-bold text-primary">{flight.departure}</div>
                        <div className="mx-4 text-gray-400 flex-1 sm:flex-none text-center">
                          <div className="border-t-2 border-dashed border-gray-300 w-16 sm:w-24 inline-block relative top-[-5px]"></div>
                          <svg className="w-4 h-4 inline-block text-secondary transform rotate-90 mx-1" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
                        </div>
                        <div className="text-2xl font-bold text-primary">{flight.destination}</div>
                      </div>
                      <div className="text-sm text-gray-500 font-medium">
                        {flight.date} • {flight.time}
                      </div>
                    </div>
                    
                    <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto sm:ml-6 border-t sm:border-t-0 sm:border-l border-gray-100 pt-4 sm:pt-0 sm:pl-6">
                      <div className="text-2xl font-bold text-secondary mb-0 sm:mb-3">${flight.cost}</div>
                      <button 
                        onClick={async () => {
                          try {
                              await api.post('/bookings', { 
                                  flight_code: flight.unique_code,
                                  full_name: user?.fullname || 'User',
                                  passport_num: user?.passport_num || 'N/A',
                                  credit_card: '1234567812345678' // Mocking input for demo
                              });
                              alert('Booking successful!');
                              window.location.reload();
                          } catch (e: any) {
                              alert(e.response?.data?.detail || 'Booking failed');
                          }
                        }}
                        className="bg-secondary text-white px-6 py-2 rounded-full font-semibold hover:bg-primary transition-colors shadow-md"
                      >
                        Book Now
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* My Bookings */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-card p-6 border-t-4 border-secondary sticky top-6">
              <h2 className="text-xl font-bold text-primary mb-6">My Itineraries</h2>
              {bookings.length === 0 ? (
                <div className="text-center py-8">
                  <div className="inline-block p-4 rounded-full bg-accent mb-3 text-secondary">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                  </div>
                  <p className="text-gray-500 text-sm">You haven't booked any flights yet.</p>
                </div>
              ) : (
                <ul className="space-y-4">
                  {bookings.map((booking) => (
                    <li key={booking._id} className="bg-accent rounded-lg p-4 border border-gray-100">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-bold text-primary text-lg">{booking.departure} → {booking.destination}</div>
                          <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider font-semibold">{booking.flight_date}</div>
                        </div>
                        <span className="bg-green-100 text-success text-xs font-bold px-2 py-1 rounded">Confirmed</span>
                      </div>
                      <div className="mt-4 pt-3 border-t border-gray-200 text-right">
                        <button 
                          onClick={async () => {
                              if (confirm('Are you sure you want to cancel this booking?')) {
                                  await api.delete(`/bookings/${booking._id}`);
                                  window.location.reload();
                              }
                          }}
                          className="text-danger hover:text-red-700 text-sm font-semibold inline-flex items-center"
                        >
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                          Cancel Booking
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
