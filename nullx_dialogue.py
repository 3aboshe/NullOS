# nullx_dialogue.py

# Dialogue text and image associations for the NullX character.

NULLX_DIALOGUE = {
    1: [ # Level 1: EXIF / Metadata
        {'image': 'NullX_explaining.png',
         'text': "Hey Agent! NullX here. Ready to dive into Digital Forensics? Your first mission involves 'metadata' - data *about* data."},
        {'image': 'NullX_speaking.png',
         'text': "Think of it like the label on a file folder. Image files have EXIF data: camera model, date taken, GPS coordinates... juicy stuff!"},
        {'image': 'NullX_explaining.png',
         'text': "Why care? Because sometimes this metadata contains hidden clues or comments directly embedded by someone... maybe our target?"},
        {'image': 'NullX_speaking.png',
         'text': "Real story: Tech personality John McAfee was hiding out. A journalist posted a photo of him online. Oops! The photo's EXIF data still had the GPS coordinates, revealing his location to the world!"},
        {'image': 'NullX_speaking.png', # << Changed from Happy
         'text': "Metadata matters! Use the 'exif' command on that image file. Find the hidden flag. Click the prompt below when you're ready to proceed!"},
    ],
    2: [ # Level 2: Strings / File Analysis
        {'image': 'NullX_explaining.png',
         'text': "Good job finding that metadata! Now, let's look *inside* files, specifically executable programs."},
        {'image': 'NullX_explaining.png',
         'text': "Programs are mostly machine code, but often contain readable text snippets called 'strings'. These can be error messages, file paths, URLs, or even accidentally left-in secrets!"},
        {'image': 'NullX_speaking.png',
         'text': "The 'strings' command scans a file for sequences of readable characters. It's like fishing for plaintext hints in a sea of binary."},
        {'image': 'NullX_speaking.png',
         'text': "Real world? Malware analysts use 'strings' constantly! They find C&C server addresses, hidden messages from the malware author, or clues about what the program does, all embedded as plain text."},
        {'image': 'NullX_Cheering.png', # << Changed from Happy (Cheering might fit?)
         'text': "Run 'strings' on that suspicious program file. See what text treasures you uncover! Ready? Click below!"},
    ],
    3: [ # Level 3: Base64 Decoding
        {'image': 'NullX_explaining.png',
         'text': "You're getting good at this! Sometimes, data isn't hidden, just... disguised. Ever seen long gibberish text with letters, numbers, maybe '+' and '/'?"},
        {'image': 'NullX_explaining.png',
         'text': "That might be Base64 encoding! It turns binary data into safe-to-transmit text characters. Crucially, it's *not* encryption, just a common way to make data look like plain text. Often ends with '=' padding."},
        {'image': 'NullX_speaking.png',
         'text': "Phishing attacks love Base64! They encode malicious website links or script commands. A simple text filter might miss 'aHR0cHM6Ly9ldmlsLnNpdGU=', but decoding it reveals 'https://evil.site'!"},
         {'image': 'NullX_speaking.png',
         'text': "Think of it as a substitution code, not a secret code. We just need the right tool to reverse it."},
        {'image': 'NullX_speaking.png', # << Changed from Happy
         'text': "Check out that log file. Spot any Base64-looking strings? Use the 'decode64' command! Let's crack it. Click when ready!"},
    ],
    4: [ # Level 4: Steganography (Simple File Embedding/Appending)
        {'image': 'NullX_explaining.png',
         'text': "Back to images! But this time, the secret isn't just metadata. We're looking at basic steganography - hiding data *inside* the file itself."},
        {'image': 'NullX_explaining.png',
         'text': "There are complex ways, but a simple one is just tacking extra data onto the *end* of a file, after the legitimate image data finishes."},
        {'image': 'NullX_speaking.png',
         'text': "Image viewers usually ignore extra data after the 'End of Image' marker. So, you could append text, another file, anything! It's hidden unless you know to look past the end."},
         {'image': 'NullX_speaking.png',
         'text': "Forensic tools, or sometimes simple 'extract' commands, can check for data appended after known file structure markers. It's less common for malware, more for challenges or hiding notes."},
        {'image': 'NullX_speaking.png', # << Changed from Happy
         'text': "That image... it might have more to it than meets the eye. Try the 'extract' command. See if anything falls out! Ready? Click below!"},
    ],
    5: [ # Level 5: Zip Passwords / Git History
        {'image': 'NullX_explaining.png',
         'text': "Final challenge, Agent! A double-header: encrypted archives and code version history."},
        {'image': 'NullX_explaining.png',
         'text': "ZIP files can be password protected. Sometimes, people get lazy and leave hints *in the file's own metadata comment*! Use 'exif' on the zip."},
         {'image': 'NullX_speaking.png',
         'text': "Then there's Git - used by developers to track code changes. Every save (commit) is logged. If someone commits a password, then removes it later... it's still visible in the 'git log' history!"},
        {'image': 'NullX_Wondering.png',
         'text': "This REALLY happens! Massive data leaks have occurred because developers accidentally committed API keys or private credentials to public GitHub repositories and forgot to purge the history."},
        {'image': 'NullX_Cheering.png', # << Changed from Happy (Cheering for final challenge?)
         'text': "First, examine the ZIP's metadata for password clues ('exif'). Then use 'unzip'. Once inside, check the note file. Does it have a history? Use 'git log'. Go! Click below!"},
    ],
}