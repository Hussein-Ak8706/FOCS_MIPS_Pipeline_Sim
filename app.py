
import streamlit as st
import sys
from io import StringIO
from parse import parseAll
from combinedClasses import (
    pipelined4StageFwd,
    pipelined5StageFwd,
    pipelined4StageStall,
    pipelined5StageStall
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Plaksha Orbital Pipeline Deck",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown("""
<style>
.main-header {
    font-size: 2.4rem;
    font-weight: bold;
    color: #1f77b4;
    text-align:center;
}
.sub-header {
    text-align:center;
    color:gray;
    margin-bottom:2rem;
}
.hazard-text {
    color:#d32f2f;
    font-weight:bold;
}
.pipeline-viz {
    width:100%;
    border-collapse:collapse;
    font-family:monospace;
}
.pipeline-viz th {
    background:#1f77b4;
    color:white;
    padding:8px;
    border:1px solid #ddd;
}
.pipeline-viz td {
    border:1px solid #ddd;
    padding:8px;
    text-align:center;
}
.stage-IF { background:#e3f2fd; font-weight:bold; }
.stage-ID { background:#f3e5f5; font-weight:bold; }
.stage-EX { background:#fff3e0; font-weight:bold; }
.stage-MEM { background:#e8f5e9; font-weight:bold; }
.stage-WB { background:#fce4ec; font-weight:bold; }
.stage-MEMWB { background:#e0f2f1; font-weight:bold; }
.stage-STALL { background:#ffebee; color:red; font-weight:bold; }
.fwd-label {
    display:block;
    font-size:0.65rem;
    margin-top:2px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown('<div class="main-header">🚀 Plaksha Orbital Pipeline Deck</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Pipeline Simulator (Step + Full View)</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
defaults = {
    "instructions": [],
    "schedule": None,
    "fwd": [],
    "raw": [],
    "simulator": None,
    "current_cycle": 1,
    "max_cycle": 1,
    "view_mode": "Step-by-Step"
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.header("⚙️ Configuration")

    pipeline_type = st.selectbox(
        "Pipeline Type",
        ["4-Stage Pipeline", "5-Stage Pipeline"]
    )

    hazard_mode = st.selectbox(
        "Hazard Resolution",
        ["Forwarding (Advanced)", "Stalling (Basic)"]
    )

    st.divider()
    st.header("📝 Add Instruction")

    instruction_type = st.selectbox(
        "Instruction Type",
        ["ADD", "SUB", "LW", "SW"]
    )

    if instruction_type in ["ADD", "SUB"]:

        c1, c2, c3 = st.columns(3)

        with c1:
            dst = st.selectbox("Dst", [f"R{i}" for i in range(1, 32)], key="dst")

        with c2:
            s1 = st.selectbox("Src1", [f"R{i}" for i in range(1, 32)], key="src1")

        with c3:
            s2 = st.selectbox("Src2", [f"R{i}" for i in range(1, 32)], key="src2")

        instruction = f"{instruction_type} {dst}, {s1}, {s2}"

    elif instruction_type == "LW":

        c1, c2, c3 = st.columns(3)

        with c1:
            dst = st.selectbox("Dst", [f"R{i}" for i in range(1, 32)], key="lw_dst")

        with c2:
            off = st.number_input("Offset", 0, 1024, 0)

        with c3:
            base = st.selectbox("Base", [f"R{i}" for i in range(1, 32)], key="lw_base")

        instruction = f"LW {dst}, {off}({base})"

    else:

        c1, c2, c3 = st.columns(3)

        with c1:
            src = st.selectbox("Src", [f"R{i}" for i in range(1, 32)], key="sw_src")

        with c2:
            off = st.number_input("Offset ", 0, 1024, 0)

        with c3:
            base = st.selectbox("Base ", [f"R{i}" for i in range(1, 32)], key="sw_base")

        instruction = f"SW {src}, {off}({base})"

    st.code(instruction)

    if st.button("➕ Add Instruction", use_container_width=True):
        if len(st.session_state.instructions) < 10:
            st.session_state.instructions.append(instruction)
            st.rerun()

    st.divider()

    if st.button("▶️ Run Simulation", type="primary", use_container_width=True):

        if not st.session_state.instructions:
            st.error("Add at least one instruction.")

        else:
            try:
                parsed = parseAll(st.session_state.instructions)

                regAvail = {f"R{i}": -1 for i in range(1, 32)}

                old_stdout = sys.stdout
                sys.stdout = StringIO()

                if pipeline_type == "4-Stage Pipeline":
                    sim = (
                        pipelined4StageFwd(regAvail, parsed)
                        if hazard_mode == "Forwarding (Advanced)"
                        else pipelined4StageStall(regAvail, parsed)
                    )
                else:
                    sim = (
                        pipelined5StageFwd(regAvail, parsed)
                        if hazard_mode == "Forwarding (Advanced)"
                        else pipelined5StageStall(regAvail, parsed)
                    )

                sim.createShedule()

                sys.stdout = old_stdout

                st.session_state.schedule = sim.schedule
                st.session_state.fwd = sim.fwd if hasattr(sim, "fwd") else []
                st.session_state.raw = sim.raw if hasattr(sim, "raw") else []
                st.session_state.simulator = sim
                st.session_state.current_cycle = 1

                mc = 1
                for row in sim.schedule:
                    if row:
                        mc = max(mc, max(row.keys()))

                st.session_state.max_cycle = mc

                st.rerun()

            except Exception as e:
                sys.stdout = old_stdout
                st.error(str(e))

    if st.button("🔄 Reset", use_container_width=True):
        for key, val in defaults.items():
            st.session_state[key] = val
        st.rerun()

# ---------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------
left, right = st.columns([1, 2])

# ---------------------------------------------------
# LEFT PANEL
# ---------------------------------------------------
with left:

    st.header("📋 Instructions")

    if st.session_state.instructions:

        for i, instr in enumerate(st.session_state.instructions):

            c1, c2 = st.columns([4, 1])

            with c1:
                st.text(f"I{i+1}: {instr}")

            with c2:
                if st.button("🗑️", key=f"del{i}"):
                    st.session_state.instructions.pop(i)
                    st.rerun()

        st.divider()
        st.header("⚠️ RAW Hazards")

        if st.session_state.schedule is None:
            st.info("Run simulation first.")

        else:
            found = False

            for i, deps in enumerate(st.session_state.raw):
                if deps:
                    found = True
                    for dep in deps:
                        st.markdown(
                            f'<div class="hazard-text">● I{i+1} depends on I{dep+1}</div>',
                            unsafe_allow_html=True
                        )

            if not found:
                st.success("No RAW hazards.")

# ---------------------------------------------------
# RIGHT PANEL
# ---------------------------------------------------
with right:

    st.header("🎯 Pipeline Visualization")

    if st.session_state.schedule is not None:

        st.radio(
            "Display Mode",
            ["Step-by-Step", "Full Schedule"],
            horizontal=True,
            key="view_mode"
        )

        if st.session_state.view_mode == "Step-by-Step":

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("⬅ Previous"):
                    st.session_state.current_cycle = max(
                        1,
                        st.session_state.current_cycle - 1
                    )
                    st.rerun()

            with c2:
                if st.button("➡ Next"):
                    st.session_state.current_cycle = min(
                        st.session_state.max_cycle,
                        st.session_state.current_cycle + 1
                    )
                    st.rerun()

            with c3:
                st.metric("Current Cycle", st.session_state.current_cycle)

            visible = st.session_state.current_cycle

        else:
            visible = st.session_state.max_cycle
            st.success(f"Showing all {visible} cycles")

        schedule = st.session_state.schedule
        fwd = st.session_state.fwd

        src_map = {}
        dst_map = {}

        for item in fwd:
            sidx, sc = item[0]
            didx, dc = item[1]

            src_map.setdefault((sidx, sc), []).append(f"to I{didx+1}")
            dst_map.setdefault((didx, dc), []).append(f"from I{sidx+1}")

        html = '<table class="pipeline-viz"><tr><th>Instr</th>'

        for c in range(1, visible + 1):
            html += f"<th>C{c}</th>"

        html += "</tr>"

        for i, row in enumerate(schedule):

            html += f"<tr><td><b>I{i+1}</b></td>"

            for c in range(1, visible + 1):

                stage = row.get(c, "")

                if stage:
                    cls = stage.replace("/", "")
                    txt = stage

                    if (i, c) in src_map:
                        for t in src_map[(i, c)]:
                            txt += f'<span class="fwd-label">{t}</span>'

                    if (i, c) in dst_map:
                        for t in dst_map[(i, c)]:
                            txt += f'<span class="fwd-label">{t}</span>'

                    html += f'<td class="stage-{cls}">{txt}</td>'

                else:
                    html += "<td></td>"

            html += "</tr>"

        html += "</table>"

        st.markdown(html, unsafe_allow_html=True)

    else:
        st.info("Run simulation first.")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.divider()

