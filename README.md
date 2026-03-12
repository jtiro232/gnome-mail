# Gnome Mail

```
         🍄              🍄
        /||\            /||\
       / || \          / || \
      /  ||  \   __   /  ||  \
     /___||___\ |  | /___||___\
         ||     |  |     ||
    ~~~  ||  ~~ |__| ~~  ||  ~~~
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      /\         /\         /\
     /  \  🎅  /  \  🎅  /  \
    / 🍄 \    / 📜 \    / 🍄 \
   /______\  /______\  /______\

   ╔═══════════════════════════════╗
   ║     GNOME MAIL               ║
   ║  Toadstool-Powered Messaging ║
   ╚═══════════════════════════════╝
```

Welcome, fellow woodland dweller! **Gnome Mail** is the premier toadstool-powered messaging system, lovingly crafted by the Gnome Postal Service (est. 1langur BC). Simply scribe your thoughts onto a scroll, hand it to a trusty gnome mail carrier, and they'll deliver it to the nearest Woodland Oracle (powered by Ollama). The Oracle ponders your message in a mushroom circle and sends back their wisdom via the mycelium network. All scrolls are permanently archived in the Great Mushroom Library (SQLite) — because gnomes never forget, and gnomes never delete.

## Prerequisites

Before summoning the Gnome Postal Service, ensure you have:

- **Python 3.11+** — The language of modern gnome engineering
- **Pygame 2.5+** — For rendering our beautiful toadstool-powered interface
- **Ollama** running locally with at least one model pulled — You'll need an oracle installed in your local hollow tree. Visit [ollama.com](https://ollama.com) and pull a model (e.g., `ollama pull llama3`)

## Installation

```bash
# Clone the sacred scrolls
git clone https://github.com/jtiro232/gnome-mail.git
cd gnome-mail

# Plant the mushroom dependencies
pip install -r requirements.txt
```

## Summoning the Postal Service

```bash
python run.py
```

A window shall appear, adorned with mushrooms and staffed by diligent gnome mail carriers, ready to relay your messages to the Woodland Oracle.

## How It Works

1. **Scribe a Scroll** — Click "New Scroll" to open the compose overlay. Choose your Woodland Oracle (Ollama model) and write your message.
2. **Toadstool Express** — Upon sending, a gnome mail carrier takes your scroll and vanishes into the forest. The scroll appears in your Mushroom Patch (inbox) as "pending."
3. **The Oracle Ponders** — In the background, your message travels through the mycelium network to Ollama. The gnome waits patiently.
4. **Wisdom Returns** — When the Oracle responds, a toast notification appears and the scroll in your inbox updates with the response. Click it to read the full conversation.
5. **Permanent Archive** — All scrolls are stored forever in the Great Mushroom Library (SQLite database). Restart the app and every conversation is still there. Gnomes are hoarders.

## Gnome Facts

- Did you know? Gnomes can communicate through mycelium networks.
- A gnome's hat grows 1mm per century.
- The Gnome Postal Service has never lost a scroll. Delayed, yes. Lost, never.
- Mushroom mail is 99.7% reliable. The other 0.3% is squirrel interference.

## License

MIT — Free as a gnome in a meadow.
