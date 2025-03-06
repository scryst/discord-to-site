# Coffee Chat Ventures - Discord Data Frontend

This is a Next.js frontend for displaying Discord server data from your Discord bot's API. This project is designed to be deployed to Vercel and connected to your Discord bot's API.

## Getting Started

1. Clone this repository
2. Install dependencies: `npm install`
3. Create a `.env.local` file with your API URL: `NEXT_PUBLIC_API_URL=https://your-discord-bot-api-url.com`
4. Run the development server: `npm run dev`
5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

1. Push this code to a GitHub repository
2. Connect the repository to Vercel
3. Set the environment variable `NEXT_PUBLIC_API_URL` to your Discord bot's API URL
4. Deploy!

## Features

- Displays Discord server information
- Shows channels, roles, members, and events
- Responsive design for mobile and desktop
- Real-time updates when new data is available

## API Endpoints

The following API endpoints are available from your Discord bot:

- `/api/summary` - Get the latest export summary
- `/api/channels` - Get the latest channels data
- `/api/roles` - Get the latest roles data
- `/api/members` - Get the latest members data
- `/api/events` - Get the latest events data
- `/api/all` - Get all data in a single response
- `/api/health` - Health check endpoint
