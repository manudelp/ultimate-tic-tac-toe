# Ultimate Tic Tac Toe

![Ultimate Tic Tac Toe Logo](/frontend/public/og_img.jpg)

Ultimate Tic Tac Toe is an advanced strategy game that adds a challenging twist to the classic Tic Tac Toe.

**[Play the game live →](https://utictactoe.online)**

## Project Structure

```
ultimate-tic-tac-toe/
├── frontend/    # Next.js (React) web app
├── backend/     # Flask + SocketIO Python server
├── render.yaml  # Render deployment config (backend)
└── package.json # Monorepo convenience scripts
```

## Getting Started

### Prerequisites

- Node.js (v14 or newer)
- Python 3.11+
- npm, yarn, or pnpm

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs on [http://localhost:5000](http://localhost:5000).

### Monorepo Scripts

```bash
npm run dev:frontend    # Start Next.js dev server
npm run dev:backend     # Start Flask dev server
npm run build:frontend  # Build Next.js for production
```

## Deployment

- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Render (see `render.yaml`)

## How to Play

1. The game starts with Player X making a move on any small board.
2. The position of that move determines which board the next player must play in.
3. If a player is sent to a board that is already won or full, they can play in any open board.
4. Win three small boards in a row (horizontally, vertically, or diagonally) to win the game.

## Technologies Used

- **Frontend**: Next.js, React, Tailwind CSS, Framer Motion, Socket.IO Client
- **Backend**: Flask, Flask-SocketIO, Gunicorn + Gevent, Supabase
- **Deployment**: Vercel (frontend), Render (backend)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
