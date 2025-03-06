import { useState, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';

// API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [serverData, setServerData] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/api/all`);
        setServerData(response.data);
        setError('');
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load server data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const renderSummary = () => {
    if (!serverData || !serverData.summary) return null;
    const { summary } = serverData;
    
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">{summary.server_name}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-lg font-semibold mb-2">Server Details</h3>
            <p><strong>ID:</strong> {summary.server_id}</p>
            <p><strong>Export Time:</strong> {new Date(summary.export_time).toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-lg font-semibold mb-2">Stats</h3>
            <p><strong>Channels:</strong> {serverData.channels?.length || 0}</p>
            <p><strong>Roles:</strong> {serverData.roles?.length || 0}</p>
            <p><strong>Members:</strong> {serverData.members?.length || 0}</p>
            <p><strong>Events:</strong> {serverData.events?.length || 0}</p>
          </div>
        </div>
      </div>
    );
  };

  const renderChannels = () => {
    if (!serverData || !serverData.channels) return null;
    const { channels } = serverData;
    
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Channels ({channels.length})</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 text-left">Name</th>
                <th className="py-2 px-4 text-left">Type</th>
                <th className="py-2 px-4 text-left">Category</th>
              </tr>
            </thead>
            <tbody>
              {channels.map((channel) => (
                <tr key={channel.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-4">{channel.name}</td>
                  <td className="py-2 px-4">{channel.type}</td>
                  <td className="py-2 px-4">{channel.category?.name || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderRoles = () => {
    if (!serverData || !serverData.roles) return null;
    const { roles } = serverData;
    
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Roles ({roles.length})</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 text-left">Name</th>
                <th className="py-2 px-4 text-left">Color</th>
                <th className="py-2 px-4 text-left">Mentionable</th>
                <th className="py-2 px-4 text-left">Displayed Separately</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => (
                <tr key={role.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-4">{role.name}</td>
                  <td className="py-2 px-4">
                    <div className="flex items-center">
                      <div 
                        className="w-4 h-4 mr-2 rounded" 
                        style={{ backgroundColor: role.color !== '#000000' ? role.color : 'transparent' }}
                      ></div>
                      {role.color}
                    </div>
                  </td>
                  <td className="py-2 px-4">{role.mentionable ? 'Yes' : 'No'}</td>
                  <td className="py-2 px-4">{role.hoist ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderMembers = () => {
    if (!serverData || !serverData.members) return null;
    
    // Check if there's an error message in the members data
    if (serverData.members.length === 1 && serverData.members[0].error) {
      return (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Members</h2>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-yellow-700">{serverData.members[0].error}</p>
            <p className="text-yellow-700 mt-2">Member Count: {serverData.members[0].member_count}</p>
          </div>
        </div>
      );
    }
    
    const { members } = serverData;
    
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Members ({members.length})</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 text-left">Name</th>
                <th className="py-2 px-4 text-left">Display Name</th>
                <th className="py-2 px-4 text-left">Joined At</th>
                <th className="py-2 px-4 text-left">Bot</th>
                <th className="py-2 px-4 text-left">Roles</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-4">{member.name}</td>
                  <td className="py-2 px-4">{member.display_name}</td>
                  <td className="py-2 px-4">{member.joined_at ? new Date(member.joined_at).toLocaleDateString() : '-'}</td>
                  <td className="py-2 px-4">{member.bot ? 'Yes' : 'No'}</td>
                  <td className="py-2 px-4">
                    <div className="flex flex-wrap gap-1">
                      {member.roles?.map(role => (
                        <span key={role.id} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {role.name}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderEvents = () => {
    if (!serverData || !serverData.events) return null;
    
    // Check if there's an error message in the events data
    if (serverData.events.length === 1 && serverData.events[0].error) {
      return (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Events</h2>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-yellow-700">{serverData.events[0].error}</p>
          </div>
        </div>
      );
    }
    
    const { events } = serverData;
    
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Events ({events.length})</h2>
        {events.length === 0 ? (
          <p>No scheduled events found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {events.map((event) => (
              <div key={event.id} className="border rounded-lg p-4 hover:shadow-md">
                <h3 className="text-lg font-semibold">{event.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{event.description}</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <strong>Start:</strong> {event.start_time ? new Date(event.start_time).toLocaleString() : 'N/A'}
                  </div>
                  <div>
                    <strong>End:</strong> {event.end_time ? new Date(event.end_time).toLocaleString() : 'N/A'}
                  </div>
                  <div>
                    <strong>Location:</strong> {event.location}
                  </div>
                  <div>
                    <strong>Status:</strong> {event.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'summary':
        return renderSummary();
      case 'channels':
        return renderChannels();
      case 'roles':
        return renderRoles();
      case 'members':
        return renderMembers();
      case 'events':
        return renderEvents();
      default:
        return renderSummary();
    }
  };

  return (
    <>
      <Head>
        <title>Coffee Chat Ventures - Discord Server Info</title>
        <meta name="description" content="View Discord server information for Coffee Chat Ventures" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-100">
        <header className="bg-blue-600 text-white shadow">
          <div className="container mx-auto px-4 py-6">
            <h1 className="text-3xl font-bold">Coffee Chat Ventures</h1>
            <p className="text-blue-100">Discord Server Information</p>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading server data...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <p className="text-red-700">{error}</p>
            </div>
          ) : (
            <>
              <div className="mb-6 flex overflow-x-auto">
                <nav className="flex space-x-4">
                  {['summary', 'channels', 'roles', 'members', 'events'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 rounded-lg font-medium ${
                        activeTab === tab
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </nav>
              </div>

              {renderContent()}
            </>
          )}
        </main>

        <footer className="bg-gray-800 text-white py-6">
          <div className="container mx-auto px-4">
            <p className="text-center">
              &copy; {new Date().getFullYear()} Coffee Chat Ventures. All rights reserved.
            </p>
            <p className="text-center text-gray-400 text-sm mt-2">
              Data last updated: {serverData?.summary?.export_time 
                ? new Date(serverData.summary.export_time).toLocaleString() 
                : 'Unknown'}
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
