import curses
key_mapping= {
    ord('q'): ("quit_app", {}),
    ord('o'): ("load_root_content", {"level": "home"}),
    ord('k'): ("nav_up", "K is for Up"),
    ord('j'): ("nav_down", "J is for Down"),
    ord('h'): ("nav_left", "H is for Right"),
    ord('l'): ("nav_right", "L is for Right")
    }
