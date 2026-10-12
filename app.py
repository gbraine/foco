def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela para o tempo de estudo acumulado (CORRIGIDO: AUTOINCREMENT sem hífen)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            segundos INTEGER DEFAULT 0
        )
    """)
    # Tabela para os itens do checklist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT UNIQUE,
            feito INTEGER DEFAULT 0
        )
    """)
    
    # Inserir itens padrão do checklist caso esteja vazio
    itens_padrao = [
        "10 min NSDR / Foco inicial",
        "Bloco 90 min - Discursiva UERJ",
        "Treino HIIT (4 rodadas)",
        "Refeição 1: Super Veggie",
        "Refeição 2: Nut Pudding",
        "Início do Jejum Noturno (18:00)"
    ]
    for item in itens_padrao:
        cursor.execute("INSERT OR IGNORE INTO checklist (texto, feito) VALUES (?, 0)", (item,))
    
    conn.commit()
    conn.close()
