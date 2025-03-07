import React, { useState, useEffect } from 'react';

const DiscordWidget = () => {
  const [discordData, setDiscordData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Replace with your actual Render.com API URL
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://your-render-service.onrender.com';
  
  useEffect(() => {
    const fetchDiscordData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${apiUrl}/api/realtime`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setDiscordData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching Discord data:', err);
        setError('Failed to load Discord data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    // Fetch data immediately
    fetchDiscordData();
    
    // Then fetch every 60 seconds
    const intervalId = setInterval(fetchDiscordData, 60000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [apiUrl]);
  
  if (loading && !discordData) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg shadow-lg text-white">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-700 rounded"></div>
              <div className="h-4 bg-gray-700 rounded w-5/6"></div>
            </div>
          </div>
        </div>
        <p className="text-center mt-4 text-gray-400">Loading Discord data...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg shadow-lg text-white">
        <h3 className="text-xl font-bold text-red-400">Error</h3>
        <p className="mt-2">{error}</p>
      </div>
    );
  }
  
  return (
    <div className="p-4 bg-gray-800 rounded-lg shadow-lg text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">{discordData?.guild_name || 'Discord Server'}</h3>
        <span className="px-2 py-1 bg-green-600 rounded-full text-xs">
          {discordData?.online_members?.length || 0} online
        </span>
      </div>
      
      {/* Online Members */}
      <div className="mb-4">
        <h4 className="text-md font-semibold text-gray-300 mb-2">Online Members</h4>
        <div className="grid grid-cols-2 gap-2">
          {discordData?.online_members?.slice(0, 6).map((member) => (
            <div key={member.id} className="flex items-center space-x-2">
              <div className="relative">
                <img 
                  src={member.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'} 
                  alt={member.display_name} 
                  className="w-8 h-8 rounded-full"
                />
                <span className={`absolute bottom-0 right-0 w-3 h-3 rounded-full ${
                  member.status === 'online' ? 'bg-green-500' : 
                  member.status === 'idle' ? 'bg-yellow-500' : 
                  member.status === 'dnd' ? 'bg-red-500' : 'bg-gray-500'
                } border-2 border-gray-800`}></span>
              </div>
              <span className="text-sm truncate">{member.display_name}</span>
            </div>
          ))}
        </div>
        {discordData?.online_members?.length > 6 && (
          <p className="text-xs text-gray-400 mt-2">
            +{discordData.online_members.length - 6} more online
          </p>
        )}
      </div>
      
      {/* Active Channels */}
      <div className="mb-4">
        <h4 className="text-md font-semibold text-gray-300 mb-2">Active Channels</h4>
        <div className="space-y-2">
          {discordData?.active_text_channels?.slice(0, 3).map((channel) => (
            <div key={channel.id} className="flex items-center space-x-2">
              <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 16 16">
                <path d="M2 2.5a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"/>
              </svg>
              <span className="text-sm">#{channel.name}</span>
              <span className="text-xs text-gray-400">
                {new Date(channel.last_message_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Voice Channels */}
      {discordData?.active_voice_channels?.length > 0 && (
        <div>
          <h4 className="text-md font-semibold text-gray-300 mb-2">Voice Channels</h4>
          <div className="space-y-2">
            {discordData.active_voice_channels.map((channel) => (
              <div key={channel.id} className="bg-gray-700 rounded p-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
                      <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z"/>
                    </svg>
                    <span className="text-sm">{channel.name}</span>
                  </div>
                  <span className="text-xs bg-gray-600 px-2 py-1 rounded-full">
                    {channel.member_count} {channel.member_count === 1 ? 'user' : 'users'}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {channel.members.map((member) => (
                    <span key={member.id} className="text-xs bg-gray-600 px-2 py-1 rounded-full">
                      {member.name}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 text-xs text-gray-400 text-center">
        Last updated: {discordData ? new Date(discordData.timestamp).toLocaleString() : 'Never'}
      </div>
    </div>
  );
};

export default DiscordWidget;
