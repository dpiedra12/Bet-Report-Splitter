import streamlit as st
import pandas as pd
import io
import zipfile

st.title("Bet Report Splitter")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Validar columnas necesarias
    if "Partner" not in df.columns or "Event Id" not in df.columns:
        st.error("El archivo debe contener las columnas 'Partner' y 'Event Id'")
    else:
        st.success("Archivo cargado correctamente ✅")

        # ==============================
        # EVENT IDS GENERALES
        # ==============================

        event_ids = df["Event Id"].dropna().unique()

        st.subheader("Event IDs encontrados")
        st.metric("Total de Eventos", len(event_ids))

        cols = st.columns(3)
        for index, event in enumerate(event_ids):
            cols[index % 3].write(f"• {event}")

        st.divider()

        # ==============================
        # GENERAR ARCHIVOS POR PARTNER + EVENT
        # ==============================

        files_by_partner = {}
        all_files = []

        partners = df["Partner"].dropna().unique()

        for partner in partners:
            df_partner = df[df["Partner"] == partner]
            event_ids_partner = df_partner["Event Id"].dropna().unique()

            partner_files = []

            for event_id in event_ids_partner:
                df_event = df_partner[df_partner["Event Id"] == event_id]

                safe_partner = str(partner).replace(" ", "").replace("/", "")
                file_name = f"{safe_partner}_Event_{event_id}.xlsx"

                file_data = {
                    "partner": partner,
                    "event_id": event_id,
                    "data": df_event,
                    "file_name": file_name
                }

                partner_files.append(file_data)
                all_files.append(file_data)

            files_by_partner[partner] = partner_files

        # ==============================
        # BOTÓN DESCARGAR TODOS (ZIP)
        # ==============================

        st.subheader("Descarga masiva")

        if st.button("📦 Descargar TODOS los archivos en ZIP"):

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

                for file_info in all_files:
                    excel_buffer = io.BytesIO()
                    file_info["data"].to_excel(
                        excel_buffer,
                        index=False,
                        engine="openpyxl"
                    )
                    excel_buffer.seek(0)

                    zip_file.writestr(
                        file_info["file_name"],
                        excel_buffer.read()
                    )

            zip_buffer.seek(0)

            st.download_button(
                label="⬇ Descargar ZIP completo",
                data=zip_buffer,
                file_name="Bet_Report_All_Files.zip",
                mime="application/zip"
            )

        st.divider()

        # ==============================
        # MOSTRAR DESCARGAS AGRUPADAS
        # ==============================

        st.subheader("Archivos individuales")

        total_files = sum(len(v) for v in files_by_partner.values())
        st.write(f"Total de archivos generados: {total_files}")

        for partner, files in files_by_partner.items():

            with st.expander(f"Partner: {partner} ({len(files)} archivos)"):
                
                for file_info in files:
                    output = io.BytesIO()

                    file_info["data"].to_excel(
                        output,
                        index=False,
                        engine="openpyxl"
                    )

                    output.seek(0)

                    st.download_button(
                        label=f"Descargar {file_info['file_name']}",
                        data=output,
                        file_name=file_info["file_name"],
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"{partner}_{file_info['event_id']}"
                    )