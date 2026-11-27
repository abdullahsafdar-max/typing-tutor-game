# Typing Tutor Game

A keyboard typing game developed using **Python** and **Pygame-ce**. Characters fall from the top of the screen, and the player must type the matching character before it reaches the Dead Bar.

## Features

- Falling lowercase letters, uppercase letters, and digits.
- Case-sensitive typing (`a` and `A` are different).
- Correct key presses remove the matching character and increase Hits.
- Wrong key presses increase Key Presses but do not increase Misses.
- Characters crossing the Dead Bar increase Misses.
- Live statistics: Hits, Misses, Key Presses, Accuracy, and Remaining Characters.
- 60-second game timer.
- Game Over screen with final statistics.
- Restart and return-to-menu options.
- Visual effects for hits, wrong keys, misses, and character urgency.
- Recent game event history.

## DSA Concepts Used

This project implements the following Data Structures and Algorithms:

### 1. Queue (Custom Linked List)
- Stores upcoming characters.
- Uses `enqueue()` to add characters.
- Uses `dequeue()` to remove characters.
- Follows FIFO (First In, First Out).

### 2. Stack
- Stores recent game events such as HIT, MISS, and WRONG KEY.
- Uses `push()` to add events.
- Uses `pop()` to remove the latest event.
- Follows LIFO (Last In, First Out).

### 3. Linear Search
- Searches active characters to find a matching typed key.
- Matching is case-sensitive.
- If duplicate characters exist, the character closest to the Dead Bar is selected.

### 4. Insertion Sort
- Sorts active characters according to their Y-coordinate in descending order.
- Places the most urgent characters first.
- Uses a stable sorting approach.

### 5. Python List
- Stores currently active falling character objects.
- Allows the game to update, search, sort, and remove active characters.

## Technologies Used

- Python
- Pygame-ce
- Git and GitHub
- Python unittest

## Project Setup

### Requirements
- Python 3
- Pygame-ce

### Installation (Windows)

1. Clone the repository:

   ```bash
   git clone https://github.com/abdullahsafdar-max/typing-tutor-game.git
   ```

2. Open the project folder:

   ```bash
   cd typing-tutor-game
   ```

3. Create a virtual environment:

   ```bash
   py -m venv .venv
   ```

4. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Run the game:

   ```bash
   python main.py
   ```

## Game Controls

| Key / Action | Function |
|---|---|
| ENTER | Start the game or restart after Game Over |
| Type a character | Hit the matching falling character |
| M | Return to the main menu from Game Over |
| ESC | Exit the game |
| Window Close Button | Exit the game |

## Game Rules

- Type the exact character displayed on the screen.
- Uppercase and lowercase letters are treated differently.
- A correct key press increases Hits and Key Presses.
- A wrong key press increases Key Presses but does not count as a Miss.
- A character crossing the Dead Bar increases Misses.
- Accuracy is calculated using:

  `Accuracy = (Hits / Total Key Presses) * 100`

- Remaining Characters = Queued Characters + Active Characters.
- The game ends when the timer reaches zero or when all characters have been completed.

## Testing

The project uses Python's built-in `unittest` framework.

Run all tests using:

```powershell
python -m unittest discover -s tests -t . -v
```

**Latest Test Results:**
- Total Tests: 338
- Passed: 338
- Failed: 0
- Skipped: 0

Manual gameplay testing was also completed successfully.

## Project Structure

```text
Typing Tutor/
│
├── assets/
│
├── data_structures/
│   ├── character_queue.py
│   ├── history_stack.py
│   ├── searching.py
│   └── sorting.py
│
├── game/
│   ├── character.py
│   ├── effects.py
│   ├── game.py
│   ├── game_state.py
│   ├── game_stats.py
│   ├── renderer.py
│   ├── round_manager.py
│   ├── spawner.py
│   └── typing_handler.py
│
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Author

**Abdullah Safdar**

🎓 BS Business Analytics Student

🌐 GitHub: [https://github.com/abdullahsafdar-max](https://github.com/abdullahsafdar-max)

---

## GitHub Repository Verification

The following commands were used to verify that the local project and GitHub repository contain the same latest commit.

```powershell
(.venv) PS D:\Typing Tutor> git fetch origin

(.venv) PS D:\Typing Tutor> git status -sb

## main...origin/main

(.venv) PS D:\Typing Tutor> git log -1 --oneline

f35e682 (HEAD -> main, origin/main, origin/HEAD) Milestone 9: Add gameplay UI polish with hit, wrong key and miss feedback, urgency colours and stats panel

(.venv) PS D:\Typing Tutor> git log origin/main -1 --oneline

f35e682 (HEAD -> main, origin/main, origin/HEAD) Milestone 9: Add gameplay UI polish with hit, wrong key and miss feedback, urgency colours and stats panel
```

**Verification Result:** The local `main` branch and GitHub `origin/main` branch are up to date and point to the same commit.