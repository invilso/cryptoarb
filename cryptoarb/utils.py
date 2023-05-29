def log(text):
    with open('log.log', '+a', encoding='utf-8') as f:
        f.write(text)