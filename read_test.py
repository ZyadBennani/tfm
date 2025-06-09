with open('data/raw/Jugadores.csv', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        print(f"Line {i+1}: {line.strip()}")
        if i >= 4:  # Only print first 5 lines
            break 