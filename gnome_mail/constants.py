"""Gnome-themed strings and app settings for Gnome Mail."""

APP_NAME = "Gnome Mail"
COMPOSE_TITLE = "Scribe a Scroll \U0001f344"
SEND_BUTTON = "Send by Toadstool Express \U0001f33f"
INBOX_TITLE = "The Mushroom Patch"
EMPTY_INBOX = "No scrolls yet! The gnomes are resting..."
PENDING_SUBTITLE = "A gnome is delivering your scroll..."
ERROR_SUBTITLE = "The gnome got lost in the forest!"
MODEL_DROPDOWN_LABEL = "Choose Your Woodland Oracle"
MESSAGE_BODY_LABEL = "Your Message to the Oracle"
YOU_LABEL = "\U0001f344 You whispered"
RESPONSE_LABEL_TEMPLATE = "\U0001f385 {} responded from the hollow tree"
LOAD_MORE = "Dig deeper in the mushroom patch..."
TOAST_ERROR_TEMPLATE = "Oh no! The gnome couldn't reach {} \U0001f342"
TOAST_RECEIVED_TEMPLATE = "A new scroll arrived from {} \U0001f344\u2728"
WAITING_RESPONSE = "The oracle is pondering in the mushroom circle..."
EMPTY_MESSAGE_WARNING = "The scroll is blank! A gnome cannot deliver nothing. \U0001f344"
COMPOSE_PLACEHOLDER = "Write your message to the woodland oracle..."
NEW_SCROLL_BUTTON = "New Scroll"
CANCEL_BUTTON = "Cancel"
OLLAMA_UNAVAILABLE = "Ollama unavailable"
DELETE_BUTTON = "Burn Scroll"
DELETE_CONFIRM = "The scroll has been cast into the fire!"
RESEND_BUTTON = "Resend by Owl Post"
RESEND_TOAST = "A fresh gnome has been dispatched with your scroll!"
ERROR_DETAIL = "Alas! The gnome stumbled and dropped your scroll!"

DB_DIR = "gnome-mail"
DB_NAME = "messages.db"
INBOX_PAGE_SIZE = 20

# Gnome names for Ollama models — each model gets a woodland persona
GNOME_NAMES = {
    "llama3": "Bramblethorne",
    "llama3.1": "Bramblethorne the Elder",
    "llama3.2": "Bramblethorne the Wise",
    "llama3.3": "Bramblethorne III",
    "llama2": "Old Rootbeard",
    "mistral": "Mistwick Fogweaver",
    "mixtral": "The Mycelium Council",
    "codellama": "Rune Scrollkeeper",
    "gemma": "Gemstone Glintcap",
    "gemma2": "Gemstone Glintcap II",
    "phi3": "Philbert Toadstool",
    "phi": "Little Philbert",
    "qwen": "Qwenwick Hollow",
    "qwen2": "Qwenwick the Younger",
    "qwen2.5": "Qwenwick Oakenshield",
    "deepseek-r1": "Deepdelve the Miner",
    "deepseek-coder": "Deepdelve Runesmith",
    "command-r": "Captain Acornbeard",
    "command-r-plus": "Admiral Acornbeard",
    "wizard-math": "Fibonacci Mosscap",
    "neural-chat": "Neuralynx the Whisper",
    "dolphin-mistral": "Delphin of the Pond",
    "stablelm2": "Steadyoak Stumpsworth",
    "orca-mini": "Little Orca of the Brook",
    "vicuna": "Vincenzo Vineroot",
    "tinyllama": "Tiny Bramble",
    "openchat": "Oakenmouth the Chatty",
    "solar": "Solarius Sundew",
    "nous-hermes2": "Hermes Swift Courier",
    "yi": "Yi the Eastern Sage",
    "falcon": "Falconrest Treewatcher",
}

# Default gnome names for unknown models
DEFAULT_GNOME_NAMES = [
    "Thistlewick", "Mosscap", "Fernwhisper", "Acornbottom", "Dewdrop",
    "Rootknuckle", "Pebbleskip", "Twigsnap", "Barkheart", "Cloverfoot",
    "Mushroomcap", "Lichentooth", "Pinecone Pete", "Stumpy Oaksworth",
    "Willowbark", "Puddle Jumper", "Dustymoss", "Cobblestone Carl",
]


# Runtime cache of model -> assigned gnome name (populated at startup)
_assigned_names = {}
_base_name_index = {}  # base model name -> gnome name (for tag-variant matching)


def _load_assigned_names():
    """Load custom gnome names from the database into the runtime cache.

    Also builds a base-name index so models with different tags
    (e.g. phi3:latest vs phi3:3.8b) share the same saved name.
    """
    global _assigned_names, _base_name_index
    try:
        from gnome_mail import db
        _assigned_names = db.get_all_gnome_names()
    except Exception:
        _assigned_names = {}
    # Build base name -> gnome name index from saved assignments
    _base_name_index = {}
    for model_key, gnome_name in _assigned_names.items():
        base = model_key.split(":")[0] if ":" in model_key else model_key
        # First saved entry for a base name wins (preserves custom renames)
        if base not in _base_name_index:
            _base_name_index[base] = gnome_name


def get_gnome_name(model_name):
    """Return a unique gnome name for a given Ollama model name.

    Names are persisted in the DB so models keep the same name across restarts.
    Also matches on base name (without :tag) so 'phi3:latest' reuses 'phi3's name.
    """
    # Direct match (includes custom renames loaded from DB)
    if model_name in _assigned_names:
        return _assigned_names[model_name]

    # Check if the base name (without :tag) already has a saved name
    base = model_name.split(":")[0] if ":" in model_name else model_name
    if base in _base_name_index:
        name = _base_name_index[base]
        _assigned_names[model_name] = name
        _save_name(model_name, name)
        return name

    # Try the explicit mapping first
    candidate = GNOME_NAMES.get(model_name) or GNOME_NAMES.get(base)

    used = set(_assigned_names.values())

    if candidate and candidate not in used:
        _assigned_names[model_name] = candidate
        _save_name(model_name, candidate)
        return candidate

    # Pick from default names, avoiding duplicates
    for name in DEFAULT_GNOME_NAMES:
        if name not in used:
            _assigned_names[model_name] = name
            _save_name(model_name, name)
            return name

    # All defaults exhausted — generate a numbered name
    i = 1
    while True:
        name = f"Gnome #{i}"
        if name not in used:
            _assigned_names[model_name] = name
            _save_name(model_name, name)
            return name
        i += 1


def set_custom_gnome_name(model_name, new_name):
    """Set a custom gnome name for a model, updating both cache and DB.

    Also updates the base-name index so all tag variants of this model
    will use the new custom name.
    """
    _assigned_names[model_name] = new_name
    _save_name(model_name, new_name)
    # Update base name index so tag variants pick up the rename
    base = model_name.split(":")[0] if ":" in model_name else model_name
    _base_name_index[base] = new_name
    # Also update any other tag variants already in the cache
    for key in list(_assigned_names.keys()):
        key_base = key.split(":")[0] if ":" in key else key
        if key_base == base and key != model_name:
            _assigned_names[key] = new_name
            _save_name(key, new_name)


def _save_name(model_name, gnome_name):
    """Persist a gnome name assignment to the database."""
    try:
        from gnome_mail import db
        db.set_gnome_name(model_name, gnome_name)
    except Exception:
        pass


def get_all_assigned_names():
    """Return the current model -> gnome name mapping."""
    return dict(_assigned_names)

RANDOM_GNOME_FACTS = [
    "Did you know? Gnomes can communicate through mycelium networks.",
    "A gnome's hat grows 1mm per century.",
    "The average garden gnome reads 340 scrolls per year.",
    "Mushroom mail is 99.7% reliable. The other 0.3% is squirrel interference.",
    "Gnomes invented email in 1langur BC. Langur is gnome for 'a long time ago'.",
    "The tallest gnome hat ever recorded was 47cm. Its owner needed a doorway extension.",
    "Gnomes prefer to write with quills plucked from friendly owls.",
    "A toadstool can relay up to 12 messages per hour during peak season.",
    "Garden gnomes hold their breath when humans walk by. They're very good at it.",
    "The Gnome Postal Service has never lost a scroll. Delayed, yes. Lost, never.",
    "Mushroom spores contain tiny encrypted messages only gnomes can read.",
    "Gnomes measure distance in 'toadstool hops' — roughly 23cm each.",
    "The first gnome computer was powered entirely by bioluminescent fungi.",
    "Gnome beards grow faster during full moons. Science cannot explain this.",
    "Underground gnome cities have better Wi-Fi than most human apartments.",
    "A gnome's favorite data structure is a tree. Obviously.",
    "Gnomes consider it rude to point at mushrooms. Always gesture with an open palm.",
    "The gnome word for 'debugging' translates to 'removing beetles from the code scroll'.",
    "Toadstool Express has maintained a 99.97% uptime since the Mushroom Ages.",
    "Gnomes backup their scrolls by whispering them to ancient oaks.",
]
