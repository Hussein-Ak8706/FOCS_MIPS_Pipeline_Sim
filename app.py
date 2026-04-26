import streamlit as st
import sys
import json
import streamlit.components.v1 as components
from io import StringIO
from parse import parseAll
from combinedClasses import pipelined4StageFwd, pipelined5StageFwd, pipelined4StageStall, pipelined5StageStall

# Set page configuration
st.set_page_config(
    page_title="Plaksha Orbital Pipeline Deck",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .instruction-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<p class="main-header">🚀 Plaksha Orbital Pipeline Deck</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Next-Generation Processor Pipeline Simulator</p>', unsafe_allow_html=True)

# Initialize session state
if 'instructions' not in st.session_state:
    st.session_state.instructions = []
if 'schedule' not in st.session_state:
    st.session_state.schedule = None
if 'fwd' not in st.session_state:
    st.session_state.fwd = []
if 'simulator' not in st.session_state:
    st.session_state.simulator = None

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    pipeline_type = st.selectbox(
        "Pipeline Type",
        ["4-Stage Pipeline", "5-Stage Pipeline"],
        help="4-Stage: IF, ID, EX, MEM/WB\n5-Stage: IF, ID, EX, MEM, WB"
    )
    
    hazard_mode = st.selectbox(
        "Hazard Resolution",
        ["Forwarding (Advanced)", "Stalling (Basic)"],
        help="Forwarding: Uses data forwarding to minimize stalls\nStalling: Uses only stalls to resolve hazards"
    )
    
    st.divider()
    
    st.header("📝 Add Instructions")
    instruction_type = st.selectbox("Instruction Type", ["ADD", "SUB", "LW", "SW"])
    
    if instruction_type in ["ADD", "SUB"]:
        col1, col2, col3 = st.columns(3)
        with col1: dst_reg = st.selectbox("Destination", [f"R{i}" for i in range(1, 32)], key="dst")
        with col2: src1_reg = st.selectbox("Source 1", [f"R{i}" for i in range(1, 32)], key="src1")
        with col3: src2_reg = st.selectbox("Source 2", [f"R{i}" for i in range(1, 32)], key="src2")
        instruction_str = f"{instruction_type} {dst_reg}, {src1_reg}, {src2_reg}"
    elif instruction_type == "LW":
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: dst_reg = st.selectbox("Destination", [f"R{i}" for i in range(1, 32)], key="dst")
        with col2: offset = st.number_input("Offset", min_value=0, max_value=1024, value=0, key="offset")
        with col3: base_reg = st.selectbox("Base Reg", [f"R{i}" for i in range(1, 32)], key="base")
        instruction_str = f"{instruction_type} {dst_reg}, {offset}({base_reg})"
    else:  # SW
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: src_reg = st.selectbox("Source", [f"R{i}" for i in range(1, 32)], key="src")
        with col2: offset = st.number_input("Offset", min_value=0, max_value=1024, value=0, key="offset")
        with col3: base_reg = st.selectbox("Base Reg", [f"R{i}" for i in range(1, 32)], key="base")
        instruction_str = f"{instruction_type} {src_reg}, {offset}({base_reg})"
    
    st.text(f"Preview: {instruction_str}")
    
    if st.button("➕ Add Instruction", use_container_width=True):
        if len(st.session_state.instructions) < 10:
            st.session_state.instructions.append(instruction_str)
            st.rerun()
        else:
            st.error("Maximum 10 instructions allowed!")
    
    st.divider()
    
    if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
        if len(st.session_state.instructions) == 0:
            st.error("Please add at least one instruction!")
        else:
            try:
                parsed_instrs = parseAll(st.session_state.instructions)
                regAvail = {f"R{i}": -1 for i in range(1, 32)}
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                if pipeline_type == "4-Stage Pipeline":
                    simulator = pipelined4StageFwd(regAvail, parsed_instrs) if hazard_mode == "Forwarding (Advanced)" else pipelined4StageStall(regAvail, parsed_instrs)
                else:
                    simulator = pipelined5StageFwd(regAvail, parsed_instrs) if hazard_mode == "Forwarding (Advanced)" else pipelined5StageStall(regAvail, parsed_instrs)
                
                simulator.createShedule()
                sys.stdout = old_stdout
                st.session_state.schedule = simulator.schedule
                st.session_state.fwd = simulator.fwd if hasattr(simulator, 'fwd') else []
                st.session_state.simulator = simulator
                st.rerun()
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Error during simulation: {str(e)}")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.instructions, st.session_state.schedule, st.session_state.fwd, st.session_state.simulator = [], None, [], None
        st.rerun()

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Instruction Sequence")
    if st.session_state.instructions:
        for i, instr in enumerate(st.session_state.instructions):
            col_a, col_b = st.columns([4, 1])
            with col_a: st.text(f"I{i+1}: {instr}")
            with col_b:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.instructions.pop(i)
                    st.rerun()
    else:
        st.info("No instructions added yet.")

with col2:
    st.header("🎯 Pipeline Visualization")
    
    if st.session_state.schedule is not None:
        schedule = st.session_state.schedule
        fwd = st.session_state.fwd
        
        # --- NEW: Create a mapping for forwarding info ---
        fwd_src_map = {} # (instr_idx, cycle) -> list of strings
        fwd_dst_map = {} # (instr_idx, cycle) -> list of strings
        
        for f in fwd:
            src_idx, src_cycle = f[0]
            dst_idx, dst_cycle = f[1]
            
            # Map source info (e.g., "forwarded to I2, C5")
            if (src_idx, src_cycle) not in fwd_src_map:
                fwd_src_map[(src_idx, src_cycle)] = []
            fwd_src_map[(src_idx, src_cycle)].append(f"to I{dst_idx+1}, C{dst_cycle}")
            
            # Map destination info (e.g., "from I1, C4")
            if (dst_idx, dst_cycle) not in fwd_dst_map:
                fwd_dst_map[(dst_idx, dst_cycle)] = []
            fwd_dst_map[(dst_idx, dst_cycle)].append(f"from I{src_idx+1}, C{src_cycle}")
        # ------------------------------------------------

        # Calculate max cycle
        max_cycle = 0
        for instr in schedule:
            if instr:
                max_cycle = max(max_cycle, max(instr.keys()))
        
        # Create HTML table with updated styles
        html = """
        <style>
            .pipeline-viz {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }
            .pipeline-viz th {
                background-color: #1f77b4;
                color: white;
                padding: 10px; border: 1px solid #ddd;
                text-align: center; font-weight: bold;
            }
            .pipeline-viz td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                background-color: white;
                min-height: 60px; /* Ensure space for labels */
            }
            .stage-IF { background-color: #e3f2fd !important; color: #1565c0; font-weight: bold; }
            .stage-ID { background-color: #f3e5f5 !important; color: #6a1b9a; font-weight: bold; }
            .stage-EX { background-color: #fff3e0 !important; color: #e65100; font-weight: bold; }
            .stage-MEM { background-color: #e8f5e9 !important; color: #2e7d32; font-weight: bold; }
            .stage-WB { background-color: #fce4ec !important; color: #c2185b; font-weight: bold; }
            .stage-MEMWB { background-color: #e0f2f1 !important; color: #00695c; font-weight: bold; }
            .stage-STALL { background-color: #ffebee !important; color: #c62828; font-weight: bold; }
            
            /* NEW: Forwarding Label Styles */
            .fwd-label {
                font-size: 0.65rem;
                font-weight: normal;
                display: block;
                line-height: 1.1;
                margin-top: 4px;
                padding: 2px;
                border-top: 1px dashed rgba(0,0,0,0.1);
            }
            .fwd-to { color: #2e7d32; }
            .fwd-from { color: #c62828; }
        </style>
        <table class="pipeline-viz">
            <tr><th>Instruction</th>
        """
        
        for c in range(1, max_cycle + 1):
            html += f"<th>C{c}</th>"
        html += "</tr>"
        
        for i, instr in enumerate(schedule):
            html += f'<tr><td class="instr-label">I{i+1}</td>'
            for c in range(1, max_cycle + 1):
                stage = instr.get(c, "")
                if stage:
                    stage_class = f"stage-{stage.replace('/', '')}"
                    
                    # Check for forwarding labels
                    fwd_info = ""
                    if (i, c) in fwd_src_map:
                        for text in fwd_src_map[(i, c)]:
                            fwd_info += f'<span class="fwd-label fwd-to">fwd {text}</span>'
                    if (i, c) in fwd_dst_map:
                        for text in fwd_dst_map[(i, c)]:
                            fwd_info += f'<span class="fwd-label fwd-from">fwd {text}</span>'
                    
                    html += f'<td class="{stage_class}">{stage}{fwd_info}</td>'
                else:
                    html += '<td></td>'
            html += '</tr>'
        
        html += '</table>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Run simulation to see visualization.")

# Footer
st.divider()
st.markdown("<div style='text-align: center; color: #666;'>Plaksha Orbital Computing Deck | CS2011: Foundations of Computer Systems</div>", unsafe_allow_html=True)