import flet as ft
import time
import datetime
import sqlite3
import os
import threading

# --- BANCO DE DADOS (SQLite) ---
DB_NAME = "dados_estudos.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            segundos INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT UNIQUE,
            feito INTEGER DEFAULT 0
        )
    """)
    
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

def carregar_dados():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(segundos) FROM estudo")
    row_tempo = cursor.fetchone()
    total_segundos = row_tempo[0] if row_tempo and row_tempo[0] else 0
    
    cursor.execute("SELECT texto, feito FROM checklist")
    rows_checklist = cursor.fetchall()
    checklist = [{"texto": r[0], "feito": bool(r[1])} for r in rows_checklist]
    conn.close()
    return total_segundos, checklist

def salvar_item_checklist(texto, feito):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE checklist SET feito = ? WHERE texto = ?", (1 if feito else 0, texto))
    conn.commit()
    conn.close()

def salvar_sessao_estudo(segundos):
    if segundos > 0:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO estudo (segundos) VALUES (?)", (segundos,))
        conn.commit()
        conn.close()

init_db()

# --- APLICAÇÃO FLET ---
def main(page: ft.Page):
    page.title = "Foco - UERJ"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    total_segundos, checklist_dados = carregar_dados()
    
    estado = {
        "segundos_sessao": 0,
        "total_acumulado": total_segundos,
        "rodando": False
    }

    lbl_sessao = ft.Text(value="Sessão: 00:00:00", size=20, color=ft.colors.BLUE_200)
    lbl_total = ft.Text(value=f"Total Salvo: {str(datetime.timedelta(seconds=total_segundos))}", size=16, color=ft.colors.GREY_400)
    
    def loop_cronometro():
        while True:
            if estado["rodando"]:
                estado["segundos_sessao"] += 1
                td_sessao = datetime.timedelta(seconds=estado["segundos_sessao"])
                lbl_sessao.value = f"Sessão: {str(td_sessao)}"
                try:
                    page.update()
                except Exception:
                    break
            time.sleep(1)

    def alternar_cronometro(e):
        estado["rodando"] = not estado["rodando"]
        if not estado["rodando"]:
            salvar_sessao_estudo(estado["segundos_sessao"])
            estado["total_acumulado"] += estado["segundos_sessao"]
            estado["segundos_sessao"] = 0
            lbl_sessao.value = "Sessão: 00:00:00"
            lbl_total.value = f"Total Salvo: {str(datetime.timedelta(seconds=estado['total_acumulado']))}"
            
        btn_timer.text = "PAUSAR E SALVAR" if estado["rodando"] else "INICIAR FOCO"
        page.update()

    btn_timer = ft.ElevatedButton("INICIAR FOCO", on_click=alternar_cronometro)

    lista_checklist = ft.Column()

    def alternar_item(e):
        salvar_item_checklist(e.control.label, e.control.value)
        page.update()

    for item in checklist_dados:
        lista_checklist.controls.append(
            ft.Checkbox(
                label=item["texto"],
                value=item["feito"],
                on_change=alternar_item
            )
        )

    page.add(
        ft.Text("🧠 Cronômetro de Foco", size=24, weight=ft.FontWeight.BOLD),
        ft.Column([lbl_sessao, lbl_total], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([btn_timer], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=30, color=ft.colors.GREY_800),
        ft.Text("📋 Checklist Diário", size=24, weight=ft.FontWeight.BOLD),
        lista_checklist
    )

    t = threading.Thread(target=loop_cronometro, daemon=True)
    t.start()

if __name__ == "__main__":
    # O Flet moderno gerencia a porta automaticamente pelas variáveis de ambiente do Render
    ft.run(main)
