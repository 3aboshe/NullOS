# --- START OF FILE level_manager.py ---

# level_manager.py
# This file defines the structure, content, and simulated command outputs for each level of the CTF game.
import settings # Needed for resource paths (images) and potentially flag regex
import os
import base64 # Required for encoding/decoding in Level 3 & 5 simulations

# Helper function to simulate the output of the 'strings' command.
# This makes the output dynamic based on the level's actual flag.
def simulate_strings(file_description, flag_value):
    """Generates a plausible-looking 'strings' command output including a provided flag."""
    # Use a default error flag if none is provided (shouldn't happen in normal flow)
    if not flag_value: flag_value = "FLAG{error_flag_not_provided}"
    # Simulate typical strings found in a binary, embedding the level's flag within.
    output = [
        f"Simulating 'strings' output for: {file_description}",
        "=========================================",
        # Common Windows executable strings
        "MZP..........This program cannot be run in DOS mode.", "$PE", ".text", ".rdata",
        ".data", ".rsrc", ".reloc", "KERNEL32.DLL", "USER32.dll", "ADVAPI32.dll",
        "GetProcAddress", "LoadLibraryA", "MessageBoxA", "VirtualAlloc", "WriteProcessMemory",
        # Metadata-like strings
        "CompanyName", "Shadow Operations Inc.", "ProductName", "Stealth Client",
        "InternalProductName", "Project Chimera", "OriginalFilename", "client.exe",
        "ProductVersion", "3.1.4", "FileVersion", "3.1.4.1",
        "Copyright (C) 2024 Shadow Ops. All rights reserved.",
        # Potential hints or functional strings
        "/settings/config.dat", "user_id=agent_x", "debug_log_enabled=0",
        "UploadDataToServer", "EncryptBufferAES", "ResolveDNSEx",
        # >>> The actual flag is embedded here dynamically <<<
        f"SuperSecretDebugKey_Or_Flag: {flag_value}",
        # Other plausible strings
        "Connection String: tcp://10.6.6.6:4444", "Fallback C2: https://secure-update.web",
        "Stack buffer overflow possibility detected nearby.",
        "send_data_to_c2_encrypted", "base64_encode_payload",
        "-----BEGIN RSA PRIVATE KEY-----", "...key data simulation...ABC123...",
        "-----END RSA PRIVATE KEY-----",
        "WinExec", "CreateProcessW", "UnhandledExceptionFilter",
        "=========================================",
        "End of simulated strings.",
    ]
    return output

# --- Define the main LEVELS dictionary ---
# This is the core data structure holding all information for each level.
# Keys are level IDs (integers).
# Values are dictionaries containing level-specific details.
LEVELS = {
    1: {
        "name": "Reveal Macafee's Location",                      # Display name for the level
        "flag": "FLAG{hidden_in_metadata}",               # The correct flag for this level
        "fake_flags": [],                                 # List of incorrect flags (optional)
        "desktop_files": {                                # Dictionary defining files visible on the desktop
            # Key: filename, Value: dictionary of properties
            "image.jpg": {"clickable": True, "target_image": settings.CLICKABLE_IMAGE_PATH, "icon_type": "image"},
            "notes.txt": {"clickable": True, "target_text": "Objective: Find the flag.\nHints:\n- Sometimes data hides in plain sight, or rather, in metadata.\n- Use the 'exif' command on files that might contain it (like images).\n- Remember 'submit FLAG{...}' or Left-Click flags in terminal output.", "icon_type": "text"},
        },
        "commands": {                                     # Dictionary simulating command outputs for this level
            # Key: command string, Value: output (list of strings or string)
            "exif image.jpg": None,                       # Placeholder, updated dynamically after definition
            "ls": ["image.jpg", "notes.txt"],
            "cat image.jpg": ["cat: Cannot display binary image content."],
            "cat notes.txt": ["Objective: Find the flag.\nHints:\n- Sometimes data hides in plain sight, or rather, in metadata.\n- Use the 'exif' command on files that might contain it (like images).\n- Remember 'submit FLAG{...}' or Left-Click flags in terminal output."],
            # Provides context-specific help strings for the 'help' command
            "help": [" exif <filename> - View EXIF metadata of images/PDFs."],
        },
        "win_message": "Metadata scan complete! Moving to file dissection.", # Message on completing level
        "next_level": 2,                                  # ID of the level to transition to after winning
    },
    2: {
        "name": "Executable Secrets",
        "flag": "FLAG{strings_reveal_all}",
        "fake_flags": ["FLAG{just_a_red_herring}", "FLAG{metadata_is_misleading}"],
        "desktop_files": {
            "report.pdf": {"clickable": True, "target_text": "Analysis Report: suspicious_data.bin\n--------------------\nFindings:\n- File header analysis inconclusive.\n- Basic metadata contains misleading information: FLAG{metadata_is_misleading}\n- Potential strings output yielded test code FLAG{just_a_red_herring}.\nConclusion:\nRequires deeper analysis of the binary structure or strings.", "icon_type": "pdf"},
            # 'filanaly' icon type simulates a file analysis tool or binary data file
            "analysis_tool.exe": {"clickable": False, "icon_type": "filanaly"}
        },
        "commands": {
            "ls": ["report.pdf", "analysis_tool.exe"],
            "cat report.pdf": ["cat: Cannot display PDF content directly."],
            "cat analysis_tool.exe": ["cat: Cannot display binary executable content."],
            "exif report.pdf": [ # Simulate some basic PDF metadata
                "Simulating EXIF for report.pdf...",
                "Title: Analysis Incomplete", "Author: Unit 731",
                f"Comment: You won't find it here... maybe? -> FLAG{{metadata_is_misleading}}", # Embed fake flag
                "Date: 2024-01-15", "Software: GhostScript",
                "--- End EXIF ---",
            ],
            "exif analysis_tool.exe": ["exif: File format does not support standard EXIF."],
            "strings analysis_tool.exe": None, # Placeholder - Updated below dynamically using simulate_strings
            "strings report.pdf": ["Simulating strings on report.pdf...", "(mostly binary PDF structure data)", "Author: Unit 731", "Title: Analysis Incomplete"],
            # Add help for the 'strings' command relevant to this level
            "help": [" strings <filename> - Display readable strings within any file."],
        },
        "win_message": "Binary analysis successful! Entering the encoding maze.",
        "next_level": 3,
     },
    3: {
        "name": "Decoding the Logs",
        "flag": "FLAG{b4s3_sixty_f0ur_FUn}",
        "fake_flags": ["FLAG{encoding_is_easy}", "FLAG{not_the_real_one}"],
        # The level's actual flag, but Base64 encoded for the user to find and decode
        "encoded_flag": "RkxBR3tiNHMzX3NpeHR5X2YwdXJfRlVufQ==",
        "desktop_files": {
            "log.txt": {"clickable": True, "target_text": None, "icon_type": "text"}, # Log content is dynamically generated
            "decoder_manual.txt": {"clickable": True, "target_text": "Manual: decode64 Utility\n------------------------\nPurpose: Decodes Base64 encoded text.\nUsage:   decode64 <base64_string>\n\nNotes:\n- Base64 often looks like random upper/lower case letters and numbers.\n- May end with '=' or '=='.\n- CLICK the Base64 string in the terminal to copy it!\n- Then type 'decode64 ', Right-Click terminal to paste, and Enter.", "icon_type": "text"},
            # Another dummy executable icon
            "sys_monitor.exe": {"clickable": False, "icon_type": "executable"}
        },
        "commands": {
            "ls": ["log.txt", "decoder_manual.txt", "sys_monitor.exe"],
            "cat log.txt": None, # Log content set dynamically below
            "cat decoder_manual.txt": ["Manual: decode64 Utility\n------------------------\nPurpose: Decodes Base64 encoded text.\nUsage:   decode64 <base64_string>\n\nNotes:\n- Base64 often looks like random upper/lower case letters and numbers.\n- May end with '=' or '=='.\n- CLICK the Base64 string in the terminal to copy it!\n- Then type 'decode64 ', Right-Click terminal to paste, and Enter."],
            "cat sys_monitor.exe": ["cat: Cannot display binary executable content."],
            "decode64": ["Usage: decode64 <base64_string>", "Error: Missing Base64 input string."], # Default output if no argument
            # Add help for the 'decode64' command
            "help": [" decode64 <string> - Decode Base64 encoded text."],
        },
        "win_message": "Base64 decoded! Revisiting image manipulation.",
        "next_level": 4,
     },
    4: {
        "name": "Hidden within the Pixels",
        "flag": "FLAG{hidden_in_the_image}",
        "fake_flags": ["FLAG{exif_is_lying_again}", "FLAG{strings_are_fake_too}"],
        "desktop_files": {
            "image.jpg": {"clickable": True, "target_image": settings.CLICKABLE_IMAGE_PATH, "icon_type": "image"},
            "readme.txt": {"clickable": True, "target_text": "Subject: Image File Anomaly\n--------------------------\nAgent,\nThis image seems suspiciously familiar.\nStandard metadata checks (EXIF, strings) revealed known fake flags.\nConsider methods where data might be appended or embedded directly.\nThe 'extract' command may be able to uncover data hidden in this way.\nTry: extract image.jpg", "icon_type": "text"},
        },
        "commands": {
            "ls": ["image.jpg", "readme.txt"], # Initially only these two files
            "cat image.jpg": ["cat: Cannot display binary image content."],
            "cat readme.txt": ["Subject: Image File Anomaly\n--------------------------\nAgent,\nThis image seems suspiciously familiar.\nStandard metadata checks (EXIF, strings) revealed known fake flags.\nConsider methods where data might be appended or embedded directly.\nThe 'extract' command may be able to uncover data hidden in this way.\nTry: extract image.jpg"],
            # 'cat' output for the file that *will be created* by the 'extract' command
            "cat extracted_flag.txt": None, # Populated dynamically by simulation
            "exif image.jpg": [ # Level 4 specific EXIF with fake flag
                "Simulating EXIF for image.jpg (Level 4)...", "-----------------------------------",
                "Make: HiddenCam", "Model: StegaMaster 5000", "Software: DataEmbed v3",
                f"UserComment: Another dead end: FLAG{{exif_is_lying_again}}", # L4 Fake flag
                "DateTime: 2024-03-01 11:11:11", "-----------------------------------",
            ],
            "strings image.jpg": [ # Level 4 specific strings with fake flag and hint
                 "Simulating 'strings' on image.jpg (Level 4)...", "-----------------------------",
                 "JFIF", "Adobe", "Photoshop", "Generic JPEG markers...",
                 "Maybe it's appended?", f"Try harder: FLAG{{strings_are_fake_too}}", # L4 Fake flag
                 "MarkerHint: EOF+HiddenData?", # Hint towards extraction
                 "-----------------------------", "End of simulated strings."
            ],
            # Simulation output for the 'extract' command itself
            "extract image.jpg": ["Processing image.jpg...", "Hidden data signature found at end of file...", "Success! Extracted data block to 'extracted_flag.txt'."],
            "extract readme.txt": ["extract: Cannot extract data from text file 'readme.txt'."],
            "extract extracted_flag.txt": ["extract: Cannot extract data from 'extracted_flag.txt'. It's already extracted content."], # Handle attempt to extract from extracted file
            # Add help for the 'extract' command
            "help": [" extract <filename> - Attempts to extract appended data from a file (like images)."],
        },
        "win_message": "Steganography success! Prepare for archive diving.",
        "next_level": 5,
    },

    5: {
        "name": "Archive Secrets & History",
        "flag": "FLAG{git_history_reveals_truth}",
        "password": "SuperSecretPW123", # Correct password for the encrypted zip file
        "fake_flags": ["FLAG{zip_contains_nothing}", "FLAG{base64_was_a_decoy}", "FLAG{fake_exif_flag}"],
        # A fake flag, encoded in Base64, embedded in the extracted note
        "embedded_fake_flag_b64": "RkxBR3tiYXNlNjRfd2FzX2FfZGVjb3l9", # FLAG{base64_was_a_decoy}
        # *** NEW: Define the content for the note that will be extracted from the PNG ***
        "extracted_note_content": [
             "AGENT X LOG - URGENT",
             "Data received, seems encoded.",
             # Embed the fake Base64 encoded flag (will be clickable in terminal)
             "RkxBR3tiYXNlNjRfd2FzX2FfZGVjb3l9", # The fake flag B64 string
             "\nDecodes to 'FLAG{base64_was_a_decoy}'. Seems like a distraction.",
             "\nRemember to check file history ('git log')? Previous versions might hold the real key.", # Git hint
             "- NullX out.",
        ],
        "desktop_files": {
            # The clickable action is handled specifically in GameState to show password prompt
            "encrypted.zip": {"clickable": False, "icon_type": "zip"},
            "hint.txt": {"clickable": True, "target_text": "Encrypted Archive Instructions:\n1. The password might be hidden in the ZIP file's own metadata. Use 'exif encrypted.zip'.\n2. Use the password with the unzip command:\n   unzip encrypted.zip -p YOUR_PASSWORD_HERE\n3. If you just run 'unzip encrypted.zip' it will prompt you.\n4. Once extracted, examine the contents. The secret note seems embedded within the image. Try 'extract'.\n5. Check history ('git log') of the extracted note if available.", "icon_type": "text"}
        },
        # Definition of file *inside* the zip archive.
        # NOW ONLY CONTAINS the image file.
        "zip_contents": {
            "secret.png": {"clickable": True, "target_image": settings.SECRET_IMG_LVL5_PATH, "icon_type": "png"},
            # secret_note.txt is NO LONGER directly in the zip
        },
        "commands": {
            # Commands available before unzipping
            "ls": ["encrypted.zip", "hint.txt"], # Initial state
            "cat encrypted.zip": ["cat: Cannot display binary ZIP content."],
            "cat hint.txt": ["Encrypted Archive Instructions:\n1. The password might be hidden in the ZIP file's own metadata. Use 'exif encrypted.zip'.\n2. Use the password with the unzip command:\n   unzip encrypted.zip -p YOUR_PASSWORD_HERE\n3. If you just run 'unzip encrypted.zip' it will prompt you.\n4. Once extracted, examine the contents. The secret note seems embedded within the image. Try 'extract'.\n5. Check history ('git log') of the extracted note if available."],
            "exif encrypted.zip": None, # Metadata containing password hint - set dynamically
            "strings encrypted.zip": ["Simulating strings on encrypted.zip...", "PK...", "secret.png", "Contains some standard ZIP headers and the image filename.", "Maybe check exif?"],
            "unzip": ["Usage: unzip <file.zip> -p <password>", "Or:    unzip encrypted.zip (for prompt)"], # Base unzip help message

            # Commands for file *inside* the zip (available after successful unzip)
            "cat secret.png": ["cat: Cannot display binary PNG content."],
            "exif secret.png": ["Simulating EXIF for secret.png...", "Artist: NullX?", f"UserComment: FLAG{{fake_exif_flag}}"], # Fake flag
            "strings secret.png": ["Simulating strings on secret.png...", "...IHDR...", "tEXtComment", "Maybe data appended?", "Try 'extract' command?"], # Hint towards extraction
            # *** NEW: Command to extract the note FROM the PNG ***
            "extract secret.png": ["Processing secret.png...", "Embedded data signature found...", "Success! Extracted hidden content to 'secret_note.txt'."],
            "extract encrypted.zip": ["extract: Command not suitable for zip files. Use 'unzip'."],
            "extract hint.txt": ["extract: Cannot extract data from text file 'hint.txt'."],

            # Commands available only AFTER extracting secret_note.txt
            "cat secret_note.txt": None, # Content set dynamically by simulation
            "decode64 RkxBR3tiYXNlNjRfd2FzX2FfZGVjb3l9": ["Decoded: FLAG{base64_was_a_decoy} (This seems too obvious...)"],
            "git log secret_note.txt": None, # Simulated Git history (contains real flag) - set dynamically
            "git": ["Usage: git log <filename> - Show commit history.", "Error: Unknown git command."], # Basic git help

            # Contextual help for commands relevant to this level
            "help": [
                " unzip <zipfile> [-p <password>] - Extract password-protected ZIP.",
                " exif <zipfile> - Check metadata for password hints.",
                " extract <filename> - Attempts to extract appended/embedded data (try on secret.png).", # Added extract hint
                " git log <filename> - View commit history of a file (after extraction).", # Clarified 'after extraction'
                " decode64 <string> - Decode Base64 strings.",
            ]
        },
        "win_message": "Archive breached and history uncovered! OS Mastered!",
        "next_level": None, # Marks the end of the game (no next level)
    },
}

# --- Post-Definition Dynamic Updates ---
# This function runs once after the LEVELS dictionary is defined.
# It populates placeholder values (like None) with dynamically generated content,
# such as embedding the actual flags or passwords into simulated command outputs.
def update_level_command_outputs():
    """Updates dynamic command outputs in the LEVELS dictionary based on level data."""
    print("Level Manager: Updating dynamic level command outputs...")
    try:
        # Level 1: Update 'exif image.jpg' output to include the real flag
        if 1 in LEVELS and 'flag' in LEVELS[1] and 'commands' in LEVELS[1]:
            level_flag = LEVELS[1]['flag']
            LEVELS[1]["commands"]["exif image.jpg"] = [ # Define the multi-line output
                "Simulating EXIF data for image.jpg...", "-----------------------------------",
                "Make: PixelCorp", "Model: CaptureMaster X", "Software: PhotoEdit Pro v2.1",
                "Comment: Standard holiday photo.",
                f"UserComment: {level_flag}", # Embed the actual flag here
                "DateTime: 2023-12-25 14:30:00", "GPSLatitude: N 34 5' 23.1\"", "GPSLongitude: W 118 14' 37.5\"",
                "-----------------------------------",
            ]

        # Level 2: Update 'strings analysis_tool.exe' using the simulation function and real flag
        if 2 in LEVELS and 'flag' in LEVELS[2] and 'commands' in LEVELS[2]:
            level_flag = LEVELS[2]['flag']
            LEVELS[2]["commands"]["strings analysis_tool.exe"] = simulate_strings("analysis_tool.exe", level_flag)

        # Level 3: Update 'cat log.txt' command output and the corresponding 'target_text' for clicking the file
        if 3 in LEVELS and 'encoded_flag' in LEVELS[3] and 'commands' in LEVELS[3]:
            encoded = LEVELS[3]['encoded_flag'] # The Base64 encoded flag for this level
            log_content = [ # Simulate log file lines
                "[INFO] System startup sequence initiated.", "[WARN] Disk space low on /var.",
                "[INFO] Service 'nginx' started.", "[INFO] Service 'firewalld' active.",
                "[ERROR] Failed login attempt for user 'root' from 192.168.1.105.",
                # Embed the clickable encoded flag within a log message
                f"[AUDIT] Data blob transferred: {encoded}",
                f"[DEBUG] Flag cache check: FLAG{{encoding_is_easy}} returned.", # Embed a fake flag
                "[INFO] User 'admin' logged out.", "[WARN] High memory usage by PID 4567.",
                "[INFO] System shutdown scheduled.",
            ]
            # Set the output for the 'cat log.txt' command
            LEVELS[3]["commands"]["cat log.txt"] = log_content
            # Set the text content for clicking the 'log.txt' icon (consistency)
            if "log.txt" in LEVELS[3]["desktop_files"]:
                 LEVELS[3]["desktop_files"]["log.txt"]["target_text"] = "\n".join(log_content)

        # Level 4: Update the 'cat' command output for the dynamically created 'extracted_flag.txt'
        if 4 in LEVELS and 'flag' in LEVELS[4] and 'commands' in LEVELS[4]:
             level_flag = LEVELS[4]['flag']
             # Define the content that 'cat extracted_flag.txt' should display
             LEVELS[4]["commands"]["cat extracted_flag.txt"] = [
                 "--- Extracted Data Block ---",
                 " Parece que alguém escondeu algo aqui.", # Some flavor text
                 f" Here it is: {level_flag}", # Embed the real flag
                 " --- End Of Block ---"
             ]

        # Level 5: Update zip file EXIF, content of note file definition, and git log output
        if 5 in LEVELS and 'password' in LEVELS[5] and 'flag' in LEVELS[5] and 'commands' in LEVELS[5]:
            level_pw = LEVELS[5]['password']
            level_flag = LEVELS[5]['flag']
            # fake_b64 = LEVELS[5]['embedded_fake_flag_b64'] # No longer needed directly here

            # Update 'exif encrypted.zip' to include the password hint
            LEVELS[5]["commands"]["exif encrypted.zip"] = [
                "Simulating EXIF data for encrypted.zip...", "-----------------------------------",
                "FileName: encrypted.zip", "FileSize: 1.5 MB", "CompressionMethod: Deflate", # Adjusted size
                "RequiresPassword: Yes",
                f"Comment: Hint => '{level_pw}' <= Might be useful?", # Embed password hint
                "Timestamp: 2024-02-28 15:00:00", "Software: SecureZip v9",
                "-----------------------------------",
            ]

            # Get the defined content for the extracted note from the new key
            extracted_note_lines = LEVELS[5].get("extracted_note_content", ["Error: Note content missing."])
            extracted_note_full_content = "\n".join(extracted_note_lines)

            # Set the output for the 'cat secret_note.txt' command (will only work after extraction)
            LEVELS[5]["commands"]["cat secret_note.txt"] = extracted_note_lines

            # Simulate the output for 'git log secret_note.txt', embedding the real flag
            # This definition remains the same, but the command will only work after extraction
            git_log_output = [
                "commit deadbeefcafe1234567890abcdef00000000 (HEAD -> main)", # Simulate Git commit hash
                "Author: Agent Shadow <shadow@agency.local>",
                "Date:   Wed Feb 28 14:55:10 2024 +0000",
                "",
                "    Update note with encoded decoy", # Commit message
                "",
                "    Added misleading Base64 string to throw off investigators.",
                "",
                "commit 1337h4x0r89abcdef1234567890d00dfeed", # Simulate older commit hash
                "Author: Agent Shadow <shadow@agency.local>",
                "Date:   Wed Feb 28 14:50:30 2024 +0000",
                "",
                f"    Initial commit - SECURED PAYLOAD STORED", # Commit message hinting at flag
                "",
                f"    Stored the critical asset: {level_flag}", # <<< Embed the real level 5 flag here
                f"    This must absolutely not be leaked.",
            ]
            LEVELS[5]["commands"]["git log secret_note.txt"] = git_log_output

    except KeyError as e:
        print(f"CRITICAL Error during level command update - Key missing: {e}. Check level definitions.")
    except Exception as e:
        print(f"CRITICAL Unexpected error during post-definition update of LEVELS: {e}")
# --- Execute the update function immediately after LEVELS is defined ---
# This ensures all dynamic content is populated before the game uses the LEVELS data.
update_level_command_outputs()

# --- Function to retrieve level data ---
def get_level_data(level_id):
    """Returns the dictionary for the requested level_id, or None if not found."""
    # .get() is safer than direct dictionary access as it returns None if the key doesn't exist
    return LEVELS.get(level_id)

# --- Function to get all defined level IDs ---
def get_all_level_ids():
    """Returns a sorted list of valid level IDs defined in LEVELS."""
    # Get all keys (level IDs) from the LEVELS dictionary and sort them numerically
    return sorted(list(LEVELS.keys()))

# --- END OF FILE level_manager.py ---