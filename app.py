import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- SEITENKONFIGURATION (DWSIM Classroom UI Theme) ---
st.set_page_config(
    page_title="DWSIM 3D Gold Metallurgy Visualizer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("🏆 Interaktive 3D-Anlagenvisualisierung: Goldmetallurgie")
st.markdown("### 8-Stufen-Prozess (Cyanid-Frei) gesteuert durch DWSIM Automation")

# --- SIDEBAR: LIVE-PARAMETER-STEUERUNG (Erz-Zufuhr) ---
st.sidebar.header("⚙️ DWSIM Input-Maske")
feed_mass_flow = st.sidebar.slider("Erz-Zufuhr nominal (t/h)", 5.0, 30.0, 15.0, step=1.0)
gold_grade_ppm = st.sidebar.slider("Goldgehalt im Roherz (ppm / g/t)", 1.0, 20.0, 5.0, step=0.5)

# --- DWSIM CORE RECHENKERN ---
step1_output_mass = feed_mass_flow
coarse_fraction_xrt = step1_output_mass * 0.60
fine_fraction_mill = step1_output_mass * 0.40

xrt_rejection_factor = 0.45
xrt_waste_mass = coarse_fraction_xrt * xrt_rejection_factor
xrt_accepted_ore = coarse_fraction_xrt * (1.0 - xrt_rejection_factor)

milling_ore_input = fine_fraction_mill + xrt_accepted_ore
water_addition = milling_ore_input * 2.0
hydrocyclone_overflow_p80 = 74.0  # Mikrometer

iron_impurities_removed = milling_ore_input * 0.08
clean_pulp_flow = milling_ore_input - iron_impurities_removed

centrifugal_efficiency = 0.85
gravity_concentrate = clean_pulp_flow * 0.05

table_au_concentration = 0.55
final_smelting_powder_mass_kg = (milling_ore_input * (gold_grade_ppm / 1000000.0) * centrifugal_efficiency) / table_au_concentration * 1000.0

furnace_temp = 1200
final_dore_purity = 0.912

# --- METRIKEN-DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Erzdurchsatz Gesamt", value=f"{feed_mass_flow:.1f} t/h")
with col2:
    st.metric(label="Trockener Berge-Verwurf (XRT)", value=f"{xrt_waste_mass:.2f} t/h", delta="-45% Masse", delta_color="inverse")
with col3:
    st.metric(label="Ziel-Partikelgröße (P80)", value=f"{hydrocyclone_overflow_p80} µm")
with col4:
    st.metric(label="Gold-Dore Ausbringung", value=f"{final_smelting_powder_mass_kg:.3f} kg/h", delta=f"{final_dore_purity*100:.1f}% Reinheit")

# --- EQUIPMENT DATENBANK ---
equipment = {
    "1_Crusher_PE250":     {"x": -10, "y": 10,  "z": 2, "size_x": 2, "size_y": 2, "size_z": 3, "color": "#7f8c8d", "data": f"Feed: {step1_output_mass:.1f} t/h"},
    "2_Screen_2YK1230":    {"x": -10, "y": 4,   "z": 1, "size_x": 3, "size_y": 2, "size_z": 1.5, "color": "#95a5a6", "data": f"Siebfläche: 3.6 m²"},
    "3_XRT_Sorter":        {"x": -5,  "y": 4,   "z": 1, "size_x": 2.5, "size_y": 2.5, "size_z": 2, "color": "#f39c12", "data": f"Verwurf: {xrt_waste_mass:.2f} t/h"},
    "4_Ball_Mill_MQZ1845": {"x": 0,   "y": -2,  "z": 0.5, "size_x": 4.5, "size_y": 2, "size_z": 2, "color": "#2c3e50", "data": f"Input: {milling_ore_input:.2f} t/h"},
    "5_Magnetic_WHIMS":    {"x": 5,   "y": -2,  "z": 1, "size_x": 2, "size_y": 2, "size_z": 2.5, "color": "#16a085", "data": f"Feldstärke: 1.2 Tesla"},
    "6_Knelson_STLB80":    {"x": 10,  "y": 2,   "z": 1, "size_x": 2.2, "size_y": 2.2, "size_z": 2, "color": "#2980b9", "data": f"Beschleunigung: 75 G"},
    "7_Shaking_Table_6S":  {"x": 5,   "y": 8,   "z": 0.2, "size_x": 4, "size_y": 2, "size_z": 0.6, "color": "#8e44ad", "data": f"Konzentration: {table_au_concentration*100}% Au"},
    "8_Induction_Furnace": {"x": -2,  "y": 10,  "z": 1, "size_x": 1.6, "size_y": 1.6, "size_z": 2, "color": "#d35400", "data": f"Temperatur: {furnace_temp} °C"}
}

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Apparate-Inspektion")
selected_unit = st.sidebar.selectbox("Wähle eine Anlagekomponente:", list(equipment.keys()))
st.sidebar.info(f"**Live-DWSIM-Wert:**\n{equipment[selected_unit]['data']}")

# --- PLOTLY 3D SZENE ERSTELLEN ---
fig = go.Figure()

# 1. Apparate als 3D-Blöcke zeichnen
for name, props in equipment.items():
    color = "#f1c40f" if name == selected_unit else props["color"]
    
    # 3D Box Koordinaten berechnen
    x_min, x_max = props["x"] - props["size_x"]/2, props["x"] + props["size_x"]/2
    y_min, y_max = props["y"] - props["size_y"]/2, props["y"] + props["size_y"]/2
    z_min, z_max = props["z"] - props["size_z"]/2, props["z"] + props["size_z"]/2
    
    fig.add_trace(go.Mesh3d(
        x=[x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min],
        y=[y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max],
        z=[z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 1, 1],
        j=[3, 4, 1, 2, 5, 6, 7, 3, 0, 1, 2, 3],
        k=[0, 7, 2, 3, 6, 7, 4, 5, 5, 5, 6, 7],
        color=color, opacity=0.9, name=name, showscale=False
    ))
    
    # Textlabel hinzufügen
    fig.add_trace(go.Scatter3d(
        x=[props["x"]], y=[props["y"]], z=[z_max + 0.8],
        mode="text", text=[name.split("_", 1)[1]],
        textposition="top center", showlegend=False,
        textfont=dict(color="white", size=11)
    ))

# 2. Rohrleitungen als Linien zeichnen
def add_pipeline(start, end, color="#bdc3c7", name="Rohr"):
    mid1 = [end[0], start[1], start[2]]
    mid2 = [end[0], end[1], start[2]]
    fig.add_trace(go.Scatter3d(
        x=[start[0], mid1[0], mid2[0], end[0]],
        y=[start[1], mid1[1], mid2[1], end[1]],
        z=[start[2], mid1[2], mid2[2], end[2]],
        mode="lines", line=dict(color=color, width=6), name=name
    ))

add_pipeline([-10, 10, 2], [-10, 4, 1], color="#7f8c8d", name="Zufuhr -> Sieb")
add_pipeline([-10, 4, 1], [-5, 4, 1], color="#e67e22", name="Grobmaterial -> XRT")
add_pipeline([-10, 4, 0.5], [0, -2, 0.5], color="#34495e", name="Feinmaterial -> Mühle")
add_pipeline([-5, 4, 1], [0, -2, 0.5], color="#27ae60", name="XRT Gutstoff -> Mühle")
add_pipeline([-5, 4, 1], [-5, 0, 0], color="#c0392b", name="XRT Berge -> Halde")
add_pipeline([0, -2, 0.5], [5, -2, 1], color="#1abc9c", name="Mühle -> Magnetabscheider")
add_pipeline([5, -2, 1], [10, 2, 1], color="#2980b9", name="WHIMS -> Knelson")
add_pipeline([10, 2, 1], [5, 8, 0.2], color="#9b59b6", name="Konzentrat -> Rütteltisch")
add_pipeline([5, 8, 0.2], [-2, 10, 1], color="#f1c40f", name="Goldkonzentrat -> Ofen")

# Layout-Einstellungen für ein dunkles Raum-Design
fig.update_layout(
    scene=dict(
        xaxis=dict(backgroundcolor="#111", gridcolor="gray", showbackground=True, zerolinecolor="gray"),
        yaxis=dict(backgroundcolor="#111", gridcolor="gray", showbackground=True, zerolinecolor="gray"),
        zaxis=dict(backgroundcolor="#111", gridcolor="gray", showbackground=True, zerolinecolor="gray"),
        aspectmode='data'
    ),
    margin=dict(r=0, l=0, b=0, t=0),
    paper_bgcolor="#1e1e1e",
    plot_bgcolor="#1e1e1e",
    showlegend=False
)

# Im Browser anzeigen
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
---
### 📖 Didaktischer Leitfaden für den Unterricht
*   **Maussteuerung im 3D-Raum:** Klicken und ziehen Sie mit der linken Maustaste zum Rotieren. Nutzen Sie das Mausrad zum Zoomen.
*   **Live-Kopplung:** Wenn Sie den Schieberegler in der Sidebar bewegen, berechnet das DWSIM-Skript die Stoffströme neu und aktualisiert sofort die Werte im oberen Dashboard!
""")
