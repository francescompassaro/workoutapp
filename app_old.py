import streamlit as st
import os
import time
import database as db

# Inizializza DB
db.init_db()

st.set_page_config(page_title="Workout Tracker", page_icon="🏋️‍♂️", layout="centered")

st.title("🏋️‍♂️ Gym Tracker Pro")

# --- MAPPATURA IMMAGINI LOCALI (nella cartella assets/) ---
EXERCISE_IMAGES = {
    "Panca Piana Barbell": "assets/panca_piana.jpg",
    "Incline Dumbbell Press": "assets/incline_dumbbell_press.jpg",
    "Dip Petto": "assets/dip_petto.jpg",
    "Military Press": "assets/military_press.jpg",
    "Tricep Pushdown": "assets/tricep_pushdown.jpg",
    "Squat": "assets/squat.jpg",
    "Stacco da Terra": "assets/stacco_da_terra.jpg",
    "Trazioni alla Sbarra/ Lat Machine": "assets/trazioni.jpg",
    "Rematore con Bilanciere": "assets/rematore.jpg",
    "Curl Bicipiti con Manubri": "assets/curl_bicipiti.jpg",
    "Leg Press": "assets/leg_press.jpg",
    "Leg Extension": "assets/leg_extension.jpg",
}

# --- SELEZIONE / AVVIO SESSIONE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if st.session_state.session_id is None:
    st.subheader("Inizia un nuovo allenamento")
    routine = st.selectbox(
        "Seleziona la scheda del giorno:", 
        ["Push A (Petto / Spalle / Tricipiti)", "Pull A (Dorso / Bicipiti)", "Legs A (Gambe / Addome)"]
    )
    
    if st.button("🚀 Avvia Sessione", type="primary"):
        new_id = db.create_session(routine)
        st.session_state.session_id = new_id
        st.rerun()

else:
    # --- SESSIONE ATTIVA ---
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.success(f"Sessione Attiva #ID-{st.session_state.session_id}")
    with col_head2:
        if st.button("🔴 Termina Allenamento"):
            st.session_state.session_id = None
            st.rerun()

    tab1, tab2 = st.tabs(["📝 REGISTRA SERIE", "📊 STORICO COMPLETO"])

    with tab1:
        st.subheader("Aggiungi Set")
        
        col_ex, col_set = st.columns([2, 1])
        with col_ex:
            exercise_list = list(EXERCISE_IMAGES.keys())
            exercise = st.selectbox("Esercizio", exercise_list)
        with col_set:
            set_num = st.number_input("Numero Set", min_value=1, max_value=10, value=1)

        # MOSTRA L'IMMAGINE DALLA CARTELLA ASSETS
        img_path = EXERCISE_IMAGES.get(exercise)
        if img_path and os.path.exists(img_path):
            with st.expander("🖼️ Mostra Esecuzione Corretta dell'Esercizio", expanded=False):
                st.image(
                    img_path, 
                    caption=f"Guida visiva: {exercise}", 
                    use_container_width=True
                )
        elif img_path:
            st.caption(f"⚠️ Immagine non trovata in: `{img_path}`. Assicurati di aver salvato il file nella cartella `assets/`.")

        col_w, col_r, col_rpe = st.columns(3)
        with col_w:
            weight = st.number_input("Carico (Kg)", min_value=0.0, step=2.5, value=60.0)
        with col_r:
            reps = st.number_input("Ripetizioni", min_value=1, max_value=100, value=8)
        with col_rpe:
            rpe = st.number_input("RPE (Opzionale)", min_value=1.0, max_value=10.0, step=0.5, value=8.0)

        if st.button("✅ Salva Serie", type="primary", use_container_width=True):
            db.save_set(st.session_state.session_id, exercise, set_num, weight, reps, rpe)
            st.toast("Set salvato nel database!", icon="💾")
            st.rerun()

        st.divider()

        # --- TIMER DI RECUPERO ---
        st.subheader("⏱️ Timer di Recupero")
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            rest_seconds = st.slider("Secondi di recupero", 30, 300, 90, step=15)
        with col_t2:
            start_timer = st.button("▶️ Avvia Timer")

        if start_timer:
            ph = st.empty()
            for t in range(rest_seconds, -1, -1):
                mins, secs = divmod(t, 60)
                ph.metric("Tempo Rimanente", f"{mins:02d}:{secs:02d}")
                time.sleep(1)
            st.balloons()
            st.success("Recupero completato!")

        st.divider()

        # --- TABELLA SERIE DELLA SESSIONE CORRENTE ---
        st.subheader("Serie Completate Oggi")
        current_df = db.get_session_sets(st.session_state.session_id)
        if not current_df.empty:
            st.dataframe(current_df, use_container_width=True)
        else:
            st.info("Nessuna serie salvata per questa sessione.")

    with tab2:
        st.subheader("Tutti i Dati Salvati")
        history_df = db.get_all_history()
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("Il database è ancora vuoto.")