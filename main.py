import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ (WIDESCREEN & PROFESSIONAL THEME) ---
st.set_page_config(page_title="Olive Manufacturing ERP", layout="wide", page_icon="🏭")

# --- CUSTOM CSS ΓΙΑ ΕΠΑΓΓΕΛΜΑΤΙΚΟ UI ---
st.markdown("""
<style>
    div.stButton > button {width: 100%; border-radius: 5px; height: 50px; font-weight: bold;}
    .reportview-container {background: #f5f5f5;}
    .big-font {font-size:20px !important; font-weight: bold;}
    .cost-header {background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# --- 1. DATA ENGINE (Η ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ) ---
@st.cache_data
def load_master_data():
    # 1.1 Μηχανές & Γραμμές Παραγωγής (Asset Management)
    machines = pd.DataFrame({
        "Γραμμή": ["Γραμμή 1 (Αυτόματη)", "Γραμμή 2 (Ημι-αυτόματη)", "Γραμμή Τενεκέ (5L)"],
        "Ταχύτητα (Φιάλες/Ώρα)": [2500, 800, 400],
        "Ισχύς (kW)": [45.0, 15.0, 12.0], # Κατανάλωση Ρεύματος
        "Κόστος Συντήρησης (€/Ώρα)": [15.0, 5.0, 4.0],
        "Εργάτες που απαιτούνται": [4, 2, 3],
        "Χρόνος Αλλαγής (Setup mins)": [45, 20, 30] # Χρόνος για αλλαγή κωδικού
    })

    # 1.2 Υλικά Συσκευασίας (BOM - Bill of Materials)
    packaging = pd.DataFrame({
        "Κωδικός": ["Dorica 250ml", "Dorica 500ml", "Marasca 750ml", "Tin 5L"],
        "Κόστος Γυαλιού/Δοχείου (€)": [0.18, 0.28, 0.42, 1.10],
        "Καπάκι (€)": [0.04, 0.04, 0.05, 0.12],
        "Ετικέτα (€)": [0.06, 0.08, 0.10, 0.15], # Μπρος-Πίσω + Λαιμού
        "Χαρτοκιβώτιο (€)": [0.45, 0.55, 0.60, 0.85],
        "Τεμάχια/Κιβώτιο": [12, 12, 12, 4],
        "Παλέτα Κόστος (€)": [12.0, 12.0, 12.0, 14.0],
        "Κιβώτια/Παλέτα": [120, 80, 60, 40]
    })
    
    return machines, packaging

df_machines, df_pack = load_master_data()

# --- 2. SIDEBAR - ΠΑΡΑΜΕΤΡΟΙ ΕΡΓΟΣΤΑΣΙΟΥ ---
with st.sidebar:
    st.header("🏭 Factory Settings")
    
    with st.expander("🔌 Ενέργεια & Εργατικά", expanded=True):
        energy_cost = st.number_input("Κόστος KWh (€)", value=0.18, format="%.3f")
        labor_hourly_rate = st.number_input("Μέσο Ωρομίσθιο (€/h)", value=12.50) # Με εργοδοτικές εισφορές
    
    with st.expander("🏢 Γενικά Βιομηχανικά Έξοδα (Overheads)"):
        # Εδώ κάνουμε επιμερισμό βάσει χρόνου λειτουργίας
        factory_rent_day = st.number_input("Ενοίκιο/Ημέρα (€)", value=100.0)
        admin_cost_pct = st.number_input("Διοικητικά Έξοδα (%)", value=12.0, help="Ποσοστό επί του κόστους παραγωγής")

# --- 3. ΚΥΡΙΩΣ ΕΦΑΡΜΟΓΗ ---
st.title("🫒 Advanced Costing & Manufacturing Engine")

# Χωρισμός σε Βήματα Λογικής
tab_calc, tab_analysis, tab_bom = st.tabs(["⚙️ Υπολογισμός Παραγωγής", "📊 Ανάλυση Κόστους (Waterfall)", "📝 Βάση Δεδομένων"])

with tab_calc:
    col_prod_1, col_prod_2 = st.columns([1, 1])
    
    with col_prod_1:
        st.subheader("1. Παραγγελία & Προϊόν")
        batch_size = st.number_input("Μέγεθος Παρτίδας (Τεμάχια)", value=5000, step=500, help="Όσο μεγαλύτερη η παρτίδα, τόσο μειώνεται το κόστος αλλαγής ανά μονάδα.")
        selected_oil_price = st.number_input("Τιμή Ελαιολάδου (€/kg)", value=8.20)
        oil_loss_pct = st.slider("Φύρα Φιλτραρίσματος (%)", 0.0, 5.0, 1.8)
        
    with col_prod_2:
        st.subheader("2. Επιλογή Γραμμής")
        selected_pack = st.selectbox("Συσκευασία (SKU)", df_pack["Κωδικός"])
        selected_line = st.selectbox("Γραμμή Παραγωγής", df_machines["Γραμμή"])
        
        # Ανάκτηση δεδομένων μηχανής
        machine_data = df_machines[df_machines["Γραμμή"] == selected_line].iloc[0]
        pack_data = df_pack[df_pack["Κωδικός"] == selected_pack].iloc[0]
        
        st.info(f"⚡ Ταχύτητα: {machine_data['Ταχύτητα (Φιάλες/Ώρα)']} φιάλες/ώρα | 👥 Προσωπικό: {machine_data['Εργάτες που απαιτούνται']} άτομα")

    st.markdown("---")

    # --- CALCULATION ENGINE (Ο ΠΥΡΗΝΑΣ) ---
    if st.button("🚀 ΕΚΤΕΛΕΣΗ ΚΟΣΤΟΛΟΓΗΣΗΣ", type="primary"):
        
        # A. ΧΡΟΝΟΙ ΠΑΡΑΓΩΓΗΣ
        # Καθαρός χρόνος λειτουργίας (Run Time)
        run_time_hours = batch_size / machine_data['Ταχύτητα (Φιάλες/Ώρα)']
        # Χρόνος στησίματος (Setup Time) - μετατροπή λεπτών σε ώρες
        setup_time_hours = machine_data['Χρόνος Αλλαγής (Setup mins)'] / 60
        # Συνολικός χρόνος δέσμευσης γραμμής
        total_time_hours = run_time_hours + setup_time_hours
        
        # B. ΚΟΣΤΟΣ Α' ΥΛΩΝ (Λάδι)
        # Υπολογισμός βάρους λαδιού (Density 0.916)
        vol_ml = 5000 if "5L" in selected_pack else int(''.join(filter(str.isdigit, selected_pack)))
        oil_weight_kg = (vol_ml * 0.916) / 1000
        cost_oil_raw = oil_weight_kg * selected_oil_price
        cost_oil_final = cost_oil_raw * (1 + oil_loss_pct/100) # Με τη φύρα

        # C. ΚΟΣΤΟΣ ΥΛΙΚΩΝ ΣΥΣΚΕΥΑΣΙΑΣ (Direct Materials)
        # Κόστος ανά τεμάχιο για τα υλικά
        cost_packaging_unit = (
            pack_data["Κόστος Γυαλιού/Δοχείου (€)"] + 
            pack_data["Καπάκι (€)"] + 
            pack_data["Ετικέτα (€)"] + 
            (pack_data["Χαρτοκιβώτιο (€)"] / pack_data["Τεμάχια/Κιβώτιο"]) + 
            (pack_data["Παλέτα Κόστος (€)"] / (pack_data["Τεμάχια/Κιβώτιο"] * pack_data["Κιβώτια/Παλέτα"]))
        )
        # Προσθήκη φύρας υλικών (π.χ. 2% σπασμένα)
        cost_packaging_final = cost_packaging_unit * 1.02

        # D. ΒΙΟΜΗΧΑΝΙΚΟ ΚΟΣΤΟΣ (Conversion Cost)
        # 1. Εργατικά: (Ώρες λειτουργίας + Ώρες αλλαγής) * Εργάτες * Ωρομίσθιο
        total_labor_cost = total_time_hours * machine_data['Εργάτες που απαιτούνται'] * labor_hourly_rate
        
        # 2. Ενέργεια: (Ώρες λειτουργίας + 20% setup) * kW * Τιμή KWh
        energy_consumption = (run_time_hours + (setup_time_hours * 0.2)) * machine_data['Ισχύς (kW)']
        total_energy_cost = energy_consumption * energy_cost
        
        # 3. Συντήρηση & Αποσβέσεις Μηχανής
        total_machine_maint = total_time_hours * machine_data['Κόστος Συντήρησης (€/Ώρα)']
        
        # 4. Γενικά Βιομηχανικά (Factory Overhead Allocation)
        # Επιμερισμός ενοικίου βάσει ωρών που δέσμευσε η παραγγελία το εργοστάσιο (υπόθεση 8ωρη βάρδια)
        overhead_allocation = (factory_rent_day / 8) * total_time_hours

        # ΣΥΝΟΛΑ ΑΝΑ ΜΟΝΑΔΑ
        cost_labor_unit = total_labor_cost / batch_size
        cost_energy_unit = total_energy_cost / batch_size
        cost_machine_unit = total_machine_maint / batch_size
        cost_overhead_unit = overhead_allocation / batch_size
        
        # E. ΤΕΛΙΚΟ ΚΟΣΤΟΣ EXW
        factory_cost_exw = cost_oil_final + cost_packaging_final + cost_labor_unit + cost_energy_unit + cost_machine_unit + cost_overhead_unit
        
        # F. Διοικητικά & Χρηματοοικονομικά
        admin_cost = factory_cost_exw * (admin_cost_pct / 100)
        final_cost = factory_cost_exw + admin_cost

        # --- ΑΠΟΤΕΛΕΣΜΑΤΑ ---
        st.session_state['results'] = {
            "Oil": cost_oil_final,
            "Packaging": cost_packaging_final,
            "Labor": cost_labor_unit,
            "Energy": cost_energy_unit,
            "Machine": cost_machine_unit,
            "Overheads": cost_overhead_unit,
            "Admin": admin_cost,
            "Total": final_cost,
            "Setup_Impact": (setup_time_hours * machine_data['Εργάτες που απαιτούνται'] * labor_hourly_rate) / batch_size # Πόσο μας κόστισε η αλλαγή ανά μπουκάλι
        }
        
        st.success("✅ Ο Υπολογισμός Ολοκληρώθηκε με επιτυχία.")

if 'results' in st.session_state:
    res = st.session_state['results']
    
    with tab_analysis:
        st.subheader(f"📊 Ανάλυση Κόστους: {selected_pack}")
        
        # 1. Metrics Top Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Τελικό Κόστος", f"€{res['Total']:.3f}", help="Πλήρες κόστος ανά τεμάχιο")
        m2.metric("Κόστος Αλλαγής (Setup)", f"€{res['Setup_Impact']:.4f}", help="Πόσο επιβαρύνει την τιμή η αλλαγή της μηχανής")
        m3.metric("Ενέργεια/Τεμάχιο", f"€{res['Energy']:.4f}")
        m4.metric("Εργατικά/Τεμάχιο", f"€{res['Labor']:.3f}")
        
        # 2. Waterfall Chart (Επαγγελματικό)
        st.markdown("### Cost Build-up (Waterfall)")
        
        fig = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x = ["Λάδι", "Υλικά Συσκευασίας", "Εργατικά", "Ενέργεια", "Μηχανή/Συντήρηση", "Γενικά Έξοδα", "Διοικητικά", "ΤΕΛΙΚΟ"],
            textposition = "outside",
            text = [f"{x:.2f}" for x in [res['Oil'], res['Packaging'], res['Labor'], res['Energy'], res['Machine'], res['Overheads'], res['Admin'], res['Total']]],
            y = [res['Oil'], res['Packaging'], res['Labor'], res['Energy'], res['Machine'], res['Overheads'], res['Admin'], res['Total']],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(title = "Διάρθρωση Κόστους ανά Φιάλη", showlegend = False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. Sensitivity Analysis (Ευαισθησία στο μέγεθος παρτίδας)
        st.markdown("### 📉 Οικονομίες Κλίμακας (Batch Size Impact)")
        st.caption("Πώς μειώνεται το κόστος αν αυξήσεις την παραγωγή (λόγω επιμερισμού του Setup Time);")
        
        # Γρήγορος υπολογισμός για το γράφημα
        batches = [1000, 3000, 5000, 10000, 20000]
        costs = []
        # Χρησιμοποιούμε τα ίδια δεδομένα αλλά αλλάζουμε το batch
        base_fixed = res['Labor'] + res['Energy'] + res['Machine'] # Απλοποίηση για το γράφημα
        for b in batches:
             # Το Setup cost διαιρείται με το batch size
             setup_impact = (res['Setup_Impact'] * batch_size) / b 
             costs.append(res['Total'] - res['Setup_Impact'] + setup_impact)
             
        fig_line = px.line(x=batches, y=costs, markers=True, labels={"x": "Ποσότητα Παρτίδας", "y": "Κόστος (€)"})
        st.plotly_chart(fig_line, use_container_width=True)

with tab_bom:
    st.subheader("Data Management")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Μηχανές & Γραμμές**")
        st.data_editor(df_machines, num_rows="dynamic")
    with c2:
        st.markdown("**Υλικά Συσκευασίας (BOM)**")
        st.data_editor(df_pack, num_rows="dynamic")
