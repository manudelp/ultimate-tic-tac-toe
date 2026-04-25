# Ultimate Tic Tac Toe

![Ultimate Tic Tac Toe Logo](/frontend/public/og_img.jpg)

Ultimate Tic Tac Toe is an advanced strategy game that adds a challenging twist to the classic Tic Tac Toe.

**[Play the game live →](https://utictactoe.online)**

## Project Structure

```
ultimate-tic-tac-toe/
├── frontend/          # Next.js (React) web app
├── backend/
│   ├── app.py         # Flask entry point
│   ├── core/          # Game engine, board utils, hash lookups, SocketIO
│   ├── api/           # Flask routes + SocketIO game namespace
│   ├── bots/          # AI bot agents (Randy, Greedy, Jardinerito, Jardinero)
│   ├── data/          # Precomputed hash tables for board evaluation
│   └── dev/           # Dev-only tests, profilers, heuristic experiments
├── render.yaml        # Render deployment config (backend)
└── package.json       # Monorepo convenience scripts
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

## AI Bots

| File | ID | Name | Icon | Difficulty | Status |
|------|---:|------|------|:----------:|--------|
| randy.py | 0 | Randy | 🎲 | 1 | ✅ Active |
| greedy.py | 1 | Greedy | 🤑 | 2 | ✅ Active |
| jardito.py | 2 | Jardinerito | ☘️ | 3 | ✅ Active |
| jardishow.py | 3 | Jardinero | 🍀 | 4 | ✅ Active |
| arthy.py | 4 | Arthy | 💎 | 4 | 🗑️ Removed (WIP) |
| monkey.py | 5 | Monkey | 🙈 | 1 | 🗑️ Removed (WIP) |
| santa.py | 112 | Santa | 🎅🏻 | 1 | 🗑️ Removed (WIP) |
| foofinder.py | -1 | Foo Finder | 👑 | 5 | 🗑️ Removed (WIP) |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
