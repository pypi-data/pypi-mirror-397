import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px
from datetime import datetime, timedelta
from src.dashboard_utils import load_usage, load_sessions

# Page Configuration
st.set_page_config(
    page_title="Hive Mind", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-top: -10px;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-header">🧠 HIVE MIND</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Control Center & Analytics</div>', unsafe_allow_html=True)
with col2:
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --- Icons & Colors ---
PROVIDER_ICONS = {
    "openai": "🧠", "anthropic": "🤖", "deepseek": "⚡", "google": "🌐", 
    "gemini": "💎", "mistral": "🌪️", "groq": "🚀", "openrouter": "🔗", "generic": "🔌"
}
PROVIDER_COLORS = {
    "openai": "#10a37f",    # OpenAI Green
    "anthropic": "#d97757", # Anthropic Clay
    "deepseek": "#4e6b9f",  # DeepSeek Blue
    "google": "#4285F4",    # Google Blue
    "gemini": "#4285F4",    # Gemini Blue
    "mistral": "#fd6f22",   # Mistral Orange
    "groq": "#f55036",      # Groq Red
    "openrouter": "#6366f1",# OpenRouter Indigo
    "generic": "#888888"    # Gray
}



# --- Load Data ---
usage_data = load_usage()
sessions_data = load_sessions()
df_sessions = pd.DataFrame(sessions_data)

# Convert Time to Datetime objects for filtering
if not df_sessions.empty:
    df_sessions['Datetime'] = pd.to_datetime(df_sessions['Time'], errors='coerce')

# --- Layout: Tabs ---
# --- Layout: Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    view = st.radio("Go to", ["💰 Budget & Cost", "📈 Analytics", "🗂️ Session Explorer", "🤖 Model Catalog"])
    st.divider()

# --- TAB 1: BUDGET & COST ---
# --- VIEW: BUDGET & COST ---
if view == "💰 Budget & Cost":
    st.markdown("### Cost Overview")
    
    # 1. Base Data Gathering
    df_raw = pd.DataFrame(usage_data.get("history", []))
    if not df_raw.empty:
        df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'], unit='s')
        
    daily_limit = float(os.getenv("DAILY_BUDGET_USD", "1.00"))

    # --- ZONE A: TODAY'S PULSE (Always showing TODAY) ---
    st.markdown("##### ⚡ Today's Pulse")
    
    # Calculate Today's Spend (Since 00:00 Local)
    now = datetime.now()
    today_start = pd.Timestamp(now.date())
    
    today_spend = 0.0
    if not df_raw.empty:
         mask_today = df_raw['timestamp'] >= today_start
         today_spend = df_raw.loc[mask_today, 'cost'].sum()
         
    remaining_today = max(0, daily_limit - today_spend)
    pct_today = min(1.0, today_spend / daily_limit) if daily_limit > 0 else 0
    
    # Visual Pulse
    pulse_cols = st.columns([1, 1, 3])
    with pulse_cols[0]:
        st.metric("Today's Spend", f"${today_spend:.4f}", help="Cost incurred since midnight")
    with pulse_cols[1]:
        st.metric("Remaining Budget", f"${remaining_today:.4f}", delta_color="normal", help="Available for rest of the day")
    with pulse_cols[2]:
        st.write("") # Align with metric
        st.markdown(f"**Budget Usage: {pct_today*100:.1f}%**")
        color = "red" if pct_today > 0.9 else "green"
        st.progress(pct_today) # Streamlit progress doesn't support color arg natively in older versions, but let's stick to default
        if pct_today >= 1.0:
            st.error("⚠️ Daily Budget Exceeded!")
            
    st.divider()

    # --- ZONE B: HISTORICAL ANALYTICS ---
    st.markdown("##### 📅 Historical Analytics")
    
    # --- SIDEBAR: CONTROL MODULE ---
    with st.sidebar:
        st.header("⚙️ Control Module")
        st.info("Adjust parameters to filter historical data.")
        
        today = datetime.now()
        last_week = today - timedelta(days=7)
        date_range = st.date_input("Filter Date Range", value=(last_week, today), key="cost_date_filter")
        
        all_providers = sorted(df_raw['provider'].unique()) if not df_raw.empty else []
        selected_providers = st.multiselect("Filter by Provider", all_providers, default=all_providers, key="cost_prov_filter")
        st.divider()
            
    # Apply Filters
    df_filtered = df_raw.copy()
    if not df_filtered.empty:
        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            mask = (df_filtered['timestamp'] >= start_date) & (df_filtered['timestamp'] <= end_date)
            df_filtered = df_filtered.loc[mask]
            
        if selected_providers:
            df_filtered = df_filtered[df_filtered['provider'].isin(selected_providers)]

    # Historical Metrics
    period_cost = df_filtered['cost'].sum() if not df_filtered.empty else 0.0
    num_days = (date_range[1] - date_range[0]).days + 1 if len(date_range) == 2 else 1
    daily_avg = period_cost / max(1, num_days)
    
    # Breaches
    breaches = 0
    if not df_filtered.empty:
        daily_sums = df_filtered.set_index('timestamp').resample('D')['cost'].sum()
        breaches = (daily_sums > daily_limit).sum()

    # --- HUD: KEY METRICS ---
    # Moved to Top Row for visibility
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Period Cost", f"${period_cost:.4f}")
    m2.metric("Daily Average", f"${daily_avg:.4f}")
    m3.metric("Budget Breaches", f"{breaches} Days", delta=f"{breaches} > Limit", delta_color="inverse")
    
    st.divider()
    
# --- CUSTOM COMPONENT OVERRIDE ---
import hashlib
import inspect
from streamlit_adjustable_columns import _component_func, HidableContainer

def condensed_adjustable_columns(
    spec=None,
    labels=None,
    gap="small",
    vertical_alignment="top",
    border=False,
    return_widths=False,
    initial_hidden=None,
    key=None,
):
    """
    Custom version of adjustable_columns with REDUCED HEIGHT (20px instead of 60px)
    to eliminate the empty header space when labels are empty.
    """
    # Handle spec parameter (same logic as st.columns)
    if spec is None:
        spec = 2  # Default to 2 equal columns

    if isinstance(spec, int):
        widths = [1] * spec
    elif hasattr(spec, "__iter__"):
        widths = list(spec)
    else:
        raise ValueError("spec must be an integer or an iterable of numbers")

    # Validate widths
    if not widths:
        raise ValueError("spec must specify at least one column")
    if any(w <= 0 for w in widths):
        raise ValueError("Column widths must be positive numbers")

    # Set default labels
    if labels is None:
        labels = [f"Col {i+1}" for i in range(len(widths))]
    elif len(labels) != len(widths):
        raise ValueError("labels must have the same length as the number of columns")

    # Validate initial_hidden parameter
    if initial_hidden is not None:
        if len(initial_hidden) != len(widths):
            raise ValueError(
                "initial_hidden must have the same length as the number of columns"
            )
        if not all(isinstance(x, bool) for x in initial_hidden):
            raise ValueError("initial_hidden must contain only boolean values")
    else:
        initial_hidden = [False] * len(widths)

    # Create unique identifier for this set of columns
    if key is None:
        caller = inspect.currentframe().f_back
        try:
            src = f"{caller.f_code.co_filename}:{caller.f_lineno}"
        finally:
            del caller
        unique_id = hashlib.md5(src.encode()).hexdigest()[:8]
    else:
        unique_id = key

    # Create session state keys for storing current widths and hidden state
    session_key = f"adjustable_columns_widths_{unique_id}"
    hidden_key = f"adjustable_columns_hidden_{unique_id}"

    # Initialize or get current widths from session state
    if session_key not in st.session_state:
        st.session_state[session_key] = widths.copy()

    current_widths = st.session_state[session_key]

    # Initialize or get hidden state from session state
    if hidden_key not in st.session_state:
        st.session_state[hidden_key] = initial_hidden.copy()

    hidden_columns = st.session_state[hidden_key]

    # Ensure we have the right number of widths and hidden states
    if len(current_widths) != len(widths):
        current_widths = widths.copy()
        st.session_state[session_key] = current_widths

    if len(hidden_columns) != len(widths):
        hidden_columns = initial_hidden.copy()
        st.session_state[hidden_key] = hidden_columns

    # Prepare configuration for the resizer component
    config = {
        "widths": current_widths,
        "labels": labels,
        "gap": gap,
        "border": border,
        "hidden": hidden_columns,
    }

    # Create the resize handles component with REDUCED HEIGHT
    component_value = _component_func(
        config=config,
        key=f"resizer_{unique_id}",
        default={"widths": current_widths, "hidden": hidden_columns},
        height=20,  # MODIFIED: Reduced from 60 to 20 to fit better
    )

    # Update current widths and hidden state from component if it has been modified
    if component_value:
        needs_update = False

        if "widths" in component_value:
            new_widths = component_value["widths"]
            if new_widths != current_widths:
                st.session_state[session_key] = new_widths
                current_widths = new_widths
                needs_update = True

        if "hidden" in component_value:
            new_hidden = component_value["hidden"]
            if new_hidden != hidden_columns:
                st.session_state[hidden_key] = new_hidden
                hidden_columns = new_hidden
                needs_update = True

        if needs_update:
            st.rerun()

    # Add CSS to ensure perfect alignment between resize handles and columns
    alignment_css = """
    <style>
    /* Ensure the resize handles iframe has no extra spacing */
    iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"] {
        border: none !important;
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .element-container:has(iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"]) {
        margin-bottom: 0 !important;
    }
    .element-container:has(iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"]) + div[data-testid="column"] {
        margin-top: 0 !important;
    }
    </style>
    """
    st.markdown(alignment_css, unsafe_allow_html=True)

    # Create the actual Streamlit columns with current widths
    MIN_WIDTH_RATIO = 0.06
    total_width = sum(current_widths)
    min_width_absolute = MIN_WIDTH_RATIO * total_width

    streamlit_widths = [max(width, min_width_absolute) for width in current_widths]

    st_columns = st.columns(
        spec=streamlit_widths,
        gap=gap,
        vertical_alignment=vertical_alignment,
        border=border,
    )

    wrapped_columns = [
        HidableContainer(col, is_hidden=hidden)
        for col, hidden in zip(st_columns, hidden_columns)
    ]

    if return_widths:
        return {
            "columns": wrapped_columns,
            "widths": current_widths,
            "hidden": hidden_columns,
        }
    else:
        return wrapped_columns

def render_dashboard(df_source=None):
    # Cost History Chart
    if df_source is not None:
        df_usage = df_source.copy()
    else:
        df_usage = pd.DataFrame(usage_data.get("history", []))

    if not df_usage.empty:
        # Ensure timestamp is datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df_usage['timestamp']):
             df_usage['timestamp'] = pd.to_datetime(df_usage['timestamp'], unit='s')

        # --- LAYOUT CONTROLS ---
        # Using CUSTOM condensed splitter for minimal header height
        # Layout: Chart (Left) | Nucleus (Right)
        col_chart, col_nucleus = condensed_adjustable_columns([2, 1], labels=["", ""])
        
        # --- NUCLEUS VISUALIZATION (RIGHT COLUMN) ---
        with col_nucleus:
            st.subheader("Hive Mind")
            
            # 1. Calculate Metrics (Using the dataframe we prepared)
            provider_counts = df_usage['provider'].value_counts()
            total_calls = len(df_usage)
            
            # 2. SVG Generator Helper
            def render_nucleus_diagram(counts, total):
                import math
                import glob
                import os
                import base64
                
                # Helper to load icon as base64
                def get_icon_b64(provider_name):
                    base_dir = "src/assets/icons"
                    for ext in ["svg", "png", "jpg"]:
                        path = os.path.join(base_dir, f"{provider_name}.{ext}")
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                data = f.read()
                                b64 = base64.b64encode(data).decode('utf-8')
                                mime = f"image/svg+xml" if ext == "svg" else f"image/{ext}"
                                return f"data:{mime};base64,{b64}"
                    return None

                # Discovery Logic
                discovered = set()
                for f in glob.glob("src/providers/*.py"):
                    name = os.path.basename(f).replace(".py", "")
                    if name not in ["base", "__init__"]:
                        if name == "openai_compatible": name = "generic"
                        discovered.add(name)
                for f in glob.glob("plugins/*.py"):
                    name = os.path.basename(f).replace(".py", "")
                    if name != "__init__": discovered.add(name)
                    
                active_providers = set(counts.index.tolist())
                all_providers = sorted(list(discovered.union(active_providers)))

                # Layout
                cx, cy = 400, 300 # Moved down slightly to accommodate top labels
                radius = 220      # Increased radius for larger spread
                
                # Responsive SVG: Tighter viewBox to "zoom in" (800x600 canvas cropped to 100-700 x)
                # Added margin-top: 40px to align visually with the chart center
                lines = []
                lines.append(f'<svg viewBox="100 0 600 600" style="width: 100%; height: auto; margin-top: 20px;" xmlns="http://www.w3.org/2000/svg">')
                lines.append('<defs>')
                lines.append('<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.2"/></filter>')
                lines.append('</defs>')
                
                lines.append('<style>')
                lines.append('@keyframes flow { to { stroke-dashoffset: -20; } }')
                lines.append('.flow-line { stroke-dasharray: 5, 5; animation: flow 1s linear infinite; }')
                lines.append('</style>')
                
                # Central Nucleus
                lines.append(f'<circle cx="{cx}" cy="{cy}" r="60" fill="#1E3A8A" stroke="#3B82F6" stroke-width="4" filter="url(#shadow)" />')
                lines.append(f'<text x="{cx}" y="{cy}" font-family="Arial" font-size="45" text-anchor="middle" dominant-baseline="middle" fill="white">🔮</text>')
                lines.append(f'<text x="{cx}" y="{cy+85}" font-family="Arial" font-size="18" text-anchor="middle" fill="#1E3A8A" font-weight="bold">HIVE MIND</text>')
                
                count = len(all_providers)
                for i, provider in enumerate(all_providers):
                    angle = (2 * math.pi * i) / count
                    px = cx + radius * math.cos(angle)
                    py = cy + radius * math.sin(angle)
                    
                    calls = counts.get(provider, 0)
                    isActive = calls > 0
                    pct = (calls / total * 100) if total > 0 else 0
                    width = max(2, min(12, (pct / 8))) 
                    
                    # Resolve Icon
                    icon_b64 = get_icon_b64(provider.split(':')[0])
                    fallback_emoji = PROVIDER_ICONS.get(provider.split(':')[0], "🔌")
                    
                    if isActive:
                        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" stroke="#93C5FD" stroke-width="{width}" class="flow-line" />')
                        
                        # Node Circle
                        lines.append(f'<circle cx="{px}" cy="{py}" r="40" fill="white" stroke="#6B7280" stroke-width="2" filter="url(#shadow)" />')
                        
                        if icon_b64:
                            lines.append(f'<defs><clipPath id="clip-{i}"><circle cx="{px}" cy="{py}" r="30" /></clipPath></defs>')
                            lines.append(f'<image href="{icon_b64}" x="{px-30}" y="{py-30}" width="60" height="60" clip-path="url(#clip-{i})" />')
                        else:
                            lines.append(f'<text x="{px}" y="{py}" font-family="Arial" font-size="35" text-anchor="middle" dominant-baseline="middle">{fallback_emoji}</text>')
                        
                        lines.append(f'<text x="{px}" y="{py+55}" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#374151">{provider.upper()}</text>')
                        lines.append(f'<text x="{px}" y="{py+75}" font-family="Arial" font-size="14" text-anchor="middle" fill="#6B7280">{calls} calls ({pct:.1f}%)</text>')
                    else:
                        lines.append(f'<circle cx="{px}" cy="{py}" r="35" fill="#F3F4F6" stroke="#D1D5DB" stroke-width="1" />')
                        if icon_b64:
                             lines.append(f'<image href="{icon_b64}" x="{px-25}" y="{py-25}" width="50" height="50" opacity="0.6" />')
                        else:
                            lines.append(f'<text x="{px}" y="{py}" font-family="Arial" font-size="30" text-anchor="middle" dominant-baseline="middle" opacity="0.6">{fallback_emoji}</text>')
                        lines.append(f'<text x="{px}" y="{py+55}" font-family="Arial" font-size="14" text-anchor="middle" fill="#9CA3AF">{provider.upper()}</text>')
                        
                lines.append('</svg>')
                return "".join(lines)

            # Render
            st.markdown(render_nucleus_diagram(provider_counts, total_calls), unsafe_allow_html=True)
            
        # --- CHART VISUALIZATION (LEFT COLUMN) ---
        with col_chart:
            df_chart = df_usage.copy()
            df_chart['Color_Key'] = df_chart['provider'].apply(lambda p: p.split(':')[0])
            
            # --- STACKED PROVIDER CHART (Standard View) ---
            st.subheader("Spending Trend (Daily)")
            
            # 1. FIX TIMEZONE: Convert Data to Local Time
            # This ensures that an event at 21:00 on Dec 14 counts for Dec 14, not Dec 15 UTC.
            local_tz = datetime.now().astimezone().tzinfo
            df_chart['datetime_local'] = pd.to_datetime(df_chart['timestamp'], unit='s', utc=True).dt.tz_convert(local_tz)
            df_chart['day_date'] = df_chart['datetime_local'].dt.date
            
            # Determine Daily Limit
            daily_limit = float(os.getenv("DAILY_BUDGET_USD", "1.00"))
            import plotly.graph_objects as go
            fig = go.Figure()

            # 2. GROUP BY LOCAL DATE & PROVIDER
            df_grouped = df_chart.groupby(['day_date', 'provider'])['cost'].sum().reset_index()
            df_grouped['date_str'] = df_grouped['day_date'].astype(str)
            
            # 3. RENDER STACKED BARS
            unique_providers = sorted(df_grouped['provider'].unique())
            for p in unique_providers:
                p_data = df_grouped[df_grouped['provider'] == p]
                p_name = p.split(':')[0]
                color = PROVIDER_COLORS.get(p_name, "#888888")
                
                fig.add_trace(go.Bar(
                    x=p_data['date_str'],
                    y=p_data['cost'],
                    name=p_name.upper(),
                    marker_color=color
                ))
                
            # 4. WARNING MARKERS (For Breached Days)
            # Calculate daily totals based on LOCAL date groups
            df_daily_total = df_grouped.groupby('date_str')['cost'].sum().reset_index()
            
            breaches = df_daily_total[df_daily_total['cost'] > daily_limit]
            
            if not breaches.empty:
                fig.add_trace(go.Scatter(
                    x=breaches['date_str'],
                    y=breaches['cost'] + (daily_limit * 0.05), # Slightly above bar
                    mode='markers+text',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    text="⚠️",
                    textposition="top center",
                    name="Over Budget",
                    showlegend=False
                ))
            
            fig.update_layout(barmode='stack')

            # --- COMMON LAYOUT (Threshold & Styling) ---
            # Threshold Line
            fig.add_shape(
                type="line",
                xref="paper", 
                x0=0,
                y0=daily_limit,
                x1=1,
                y1=daily_limit,
                line=dict(color="red", width=2, dash="dashdot"),
            )
            # Annotation for limit
            fig.add_annotation(
                xref="paper",
                x=1,
                y=daily_limit,
                text=f"Limit: ${daily_limit}",
                showarrow=False,
                yshift=10,
                font=dict(color="red")
            )

            fig.update_layout(
                title=dict(text=""),
                margin=dict(t=30, l=0, r=10),
                yaxis=dict(title="Daily Cost (USD)", showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, type='category'), # Explicit category
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
            )
            
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("No spending history recorded yet.")


# --- TAB 2: ANALYTICS ---
# --- TAB 2: ANALYTICS ---
# --- VIEW: ANALYTICS ---
if view == "📈 Analytics":
    if not df_sessions.empty:
        st.markdown("### Operational Insights")
        
        # 1. Filters
        c_filter, c_void = st.columns([2, 1])
        with c_filter:
            c_date, c_type = st.columns(2)
            with c_date:
                # Default to last 7 days + today
                today = datetime.now()
                last_week = today - timedelta(days=7)
                date_range = st.date_input(
                    "Filter Date Range",
                    value=(last_week, today),
                    key="analytics_date_filter"
                )
            with c_type:
                all_types = sorted(df_sessions['Type'].unique())
                selected_types = st.multiselect(
                    "Filter by Type",
                    all_types,
                    default=all_types,
                    key="analytics_type_filter"
                )
        
        # 2. Apply Filters
        df_analytics = df_sessions.copy()
        
        # Date Filter
        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            # Ensure filtering respects the chosen dates (inclusive)
            # df_sessions has 'Datetime' column
            mask = (df_analytics['Datetime'] >= start_date) & (df_analytics['Datetime'] <= end_date)
            df_analytics = df_analytics.loc[mask]
            
        # Type Filter
        if selected_types:
            df_analytics = df_analytics[df_analytics['Type'].isin(selected_types)]
            
        st.divider()

        # 3. Visualizations (Using Filtered Data)
        if not df_analytics.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Sessions", len(df_analytics))
            m2.metric("Avg Files/Session", f"{df_analytics['Files'].mean():.1f}")
            m3.metric("Most Active Type", df_analytics['Type'].mode()[0] if not df_analytics.empty else "N/A")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Sessions by Type")
                type_counts = df_analytics['Type'].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                fig_pie = px.pie(type_counts, values='Count', names='Type', hole=0.4)
                st.plotly_chart(fig_pie, width="stretch")
                
            with c2:
                st.subheader("Activity Timeline")
                # Convert rough timestamp to datetime if possible, simplistic approach
                try:
                    # Assuming format YYYY-MM-DD
                    # If Time is mostly date strings, this works. If it's a mix, might be noisy.
                    df_analytics['Date'] = pd.to_datetime(df_analytics['Time']).dt.date
                    df_analytics['DateStr'] = df_analytics['Date'].astype(str)
                    
                    # Group by Date and Type
                    df_timeline = df_analytics.groupby(['DateStr', 'Type']).size().reset_index(name='Count')

                    # --- REINDEX TO SHOW EMPTY DAYS ---
                    # Create full date range from filter
                    if len(date_range) == 2:
                        full_idx = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
                        full_dates = full_idx.astype(str)
                        
                        # Cross join with all known types to ensure stacked integrity
                        all_types = df_analytics['Type'].unique()
                        import itertools
                        full_combinations = pd.DataFrame(
                            list(itertools.product(full_dates, all_types)), 
                            columns=['DateStr', 'Type']
                        )
                        
                        # Merge actual data into full frame
                        df_timeline = pd.merge(full_combinations, df_timeline, on=['DateStr', 'Type'], how='left').fillna(0)

                    fig_timeline = px.bar(df_timeline, x='DateStr', y='Count', color='Type', title=None)
                    fig_timeline.update_layout(xaxis=dict(type='category', title="Date"))
                    st.plotly_chart(fig_timeline, width="stretch")
                except:
                    st.warning("Could not parse timestamps for timeline.")
        else:
             st.warning("No sessions found for the selected filters.")
    else:
        st.info("No sessions available for analytics.")

# --- TAB 3: SESSION EXPLORER (Original Logic Enhanced) ---
# --- VIEW: SESSION EXPLORER ---
if view == "🗂️ Session Explorer":
    st.markdown("### Artifact Inspector")
    
    if not df_sessions.empty:
        # Filters in an expander to keep it clean
        with st.expander("🔎 Filter & Search", expanded=True):
            f1, f2, f3 = st.columns([1, 1, 2])
            with f1:
                all_types = sorted(df_sessions['Type'].unique())
                selected_types = st.multiselect("Filter by Type", all_types, default=all_types)
            with f2:
                # Date Range Filter
                min_date = df_sessions['Datetime'].min().date()
                max_date = df_sessions['Datetime'].max().date()
                date_range = st.date_input("Filter by Date Range", value=(min_date, max_date))
            with f3:
                search_term = st.text_input("Search Topic", placeholder="e.g., 'Refactor', 'Budget'...")
        
        # Apply Filters
        filtered_df = df_sessions[df_sessions['Type'].isin(selected_types)]
        
        # Apply Date Filter
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            # Ensure filtering respects the chosen dates (inclusive)
            filtered_df = filtered_df[
                (filtered_df['Datetime'].dt.date >= start_date) & 
                (filtered_df['Datetime'].dt.date <= end_date)
            ]
        elif isinstance(date_range, tuple) and len(date_range) == 1:
             # Handle single date selection case
             filtered_df = filtered_df[filtered_df['Datetime'].dt.date == date_range[0]]
            
        if search_term:
            filtered_df = filtered_df[filtered_df['Topic'].str.contains(search_term, case=False)]
            

        
        st.divider()
        st.markdown(f"**Showing {len(filtered_df)} Session(s)**")
        
        # --- GROUP BY DATE ---
        # Add a string date column for grouping
        filtered_df['DayString'] = filtered_df['Datetime'].dt.strftime('%Y-%m-%d')
        unique_days = sorted(filtered_df['DayString'].unique(), reverse=True)
        
        for day_idx, day in enumerate(unique_days):
            day_sessions = filtered_df[filtered_df['DayString'] == day]
            
            # Expander for the Date (Expand first item by default)
            with st.expander(f"📅 {day} ({len(day_sessions)} sessions)", expanded=(day_idx == 0)):
                
                # --- TABS BY TYPE ---
                present_types = sorted(day_sessions['Type'].unique())
                if present_types:
                    tabs = st.tabs([t.replace("_", " ").title() for t in present_types])
                    
                    for t_idx, t in enumerate(present_types):
                        with tabs[t_idx]:
                            type_sessions = day_sessions[day_sessions['Type'] == t]
                            
                            # Create a label for each session (Removed Type prefix as it's redundant in tab)
                            type_sessions['Label'] = type_sessions.apply(lambda x: f"{x['Topic']} ({x['Time'].split(' ')[1]})", axis=1)
                            
                            # Use a specific key for this day+type selectbox
                            selected_session_label = st.selectbox(
                                "Select Session", 
                                type_sessions['Label'].tolist(), 
                                key=f"sel_session_{day}_{t}"
                            )
                            
                            # Retrieve the selected row
                            if selected_session_label:
                                row = type_sessions[type_sessions['Label'] == selected_session_label].iloc[0]
                                
                                st.caption(f"📂 Path: `{row['Path']}`")

                                # List files sorted
                                files = sorted(glob.glob(os.path.join(row['Path'], "*")))
                                file_names = [os.path.basename(f) for f in files]
                                
                                if not file_names:
                                    st.warning("No artifacts in this session.")
                                else:
                                    c_sel, c_view = st.columns([1, 2])
                                    with c_sel:
                                        # Use PATH hash for key stability
                                        safe_key = str(hash(row['Path']))
                                        selected_file_name = st.radio("Select Artifact", file_names, key=f"sel_art_{safe_key}")
                                    
                                    with c_view:
                                        if selected_file_name:
                                            full_path = os.path.join(row['Path'], selected_file_name)
                                            try:
                                                with open(full_path, "r", encoding='utf-8', errors='replace') as f:
                                                    content = f.read()
                                                
                                                st.markdown(f"**📄 {selected_file_name}**")
                                                if selected_file_name.endswith(".json"):
                                                    try:
                                                        st.json(json.loads(content))
                                                    except:
                                                        st.warning("⚠️ File is not valid JSON. Showing raw content:")
                                                        st.code(content)
                                                elif selected_file_name.endswith(".md"):
                                                    st.markdown(content)
                                                else:
                                                    st.code(content)
                                            except Exception as e:
                                                st.error(f"Error reading file: {e}")

    else:
        st.warning("No session artifacts found.")

# --- RENDER DASHBOARD (Budget Tab) ---
if view == "💰 Budget & Cost":
    render_dashboard(df_filtered)


# --- TAB 4: MODEL CATALOG ---
# --- VIEW: MODEL CATALOG ---
if view == "🤖 Model Catalog":
    st.markdown("### 🤖 Available Models")
    st.caption("Browse all models currently discovered by the MCP Orchestrator.")
    
    # 1. Load Models (Cached)
    @st.cache_data(ttl=3600)
    def fetch_all_models():
        import sys
        # Ensure src is in path
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
            
        try:
            from src.tools import LLMManager
            from dotenv import load_dotenv
            load_dotenv()
            
            manager = LLMManager()
            # Manager will run discovery
            return manager.list_models()
        except Exception as e:
            return {"error": str(e)}

    # Fetch models
    with st.spinner("Discovering models..."):
        models_data = fetch_all_models()
    
    # Refresh Button
    if st.button("🔄 Refresh Models"):
        fetch_all_models.clear()
        st.rerun()
        
    if "error" in models_data:
        st.error(f"Failed to load models: {models_data['error']}")
    else:

        # 2. Search & Filter
        c_search, c_sota = st.columns([4, 1])
        with c_search:
            search_query = st.text_input("🔍 Search Models", placeholder="Type to filter (e.g., 'claude', 'gpt-4', '32b')...")
        with c_sota:
            st.write("") # Spacer
            st.write("") 
            show_sota = st.toggle("🏆 SOTA Only", value=False, help="Show only State-of-the-Art models (GPT-4, Claude 3.5, etc.)")

        # SOTA Logic
        SOTA_KEYWORDS = ["gpt-4", "claude-3-5", "sonnet", "gemini-1.5-pro", "gemini-ultra", "405b", "o1-", "opus"]
        
        # Flatten for search
        all_flat = []
        for provider, m_list in models_data.items():
            for m in m_list:
                is_sota_model = any(k in m.lower() for k in SOTA_KEYWORDS)
                if show_sota and not is_sota_model:
                    continue
                all_flat.append({"Provider": provider, "Model ID": m, "Full ID": f"{provider}:{m}"})
                
        df_models = pd.DataFrame(all_flat)
        if df_models.empty and "Full ID" not in df_models.columns:
            df_models = pd.DataFrame(columns=["Provider", "Model ID", "Full ID"])
        
        if search_query:
            mask = df_models["Full ID"].str.contains(search_query, case=False)
            df_filtered = df_models[mask]
        else:
            df_filtered = df_models
            
        # 3. Categorized Display
        # Group by Provider again based on filtered results
        
        # INJECT CSS FOR ICONS
        st.markdown("""
        <style>
        .provider-icon {
            background-color: white;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: auto;
        }
        .provider-icon img {
            width: 24px !important; 
            height: 24px !important;
            border-radius: 0 !important; /* Reset streamlit styling */
        }
        .provider-icon-text {
            font-size: 20px;
            line-height: 35px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if not df_filtered.empty:
            providers = sorted(df_filtered["Provider"].unique())
            
            # Show summarized count
            st.info(f"Showing **{len(df_filtered)}** models across **{len(providers)}** providers.")

            for prov in providers:
                prov_models = df_filtered[df_filtered["Provider"] == prov]["Model ID"].tolist()
                
                # Determine color/icon
                color = PROVIDER_COLORS.get(prov, "#888888")
                
                # Resolve Real Icon Path
                icon_path = None
                base_dir = "src/assets/icons"
                real_icon_html = ""
                
                # Check for icon file
                for ext in ["svg", "png", "jpg"]:
                    try_path = os.path.join(base_dir, f"{prov}.{ext}")
                    if os.path.exists(try_path):
                        import base64
                        with open(try_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                            mime = f"image/svg+xml" if ext == "svg" else f"image/{ext}"
                            real_icon_html = f'<img src="data:{mime};base64,{b64}">'
                        break
                
                # Render Icon HTML (Bubble)
                if real_icon_html:
                    html_content = f'<div class="provider-icon">{real_icon_html}</div>'
                else:
                    emoji = PROVIDER_ICONS.get(prov, "🔌")
                    html_content = f'<div class="provider-icon"><span class="provider-icon-text">{emoji}</span></div>'

                # Layout: Icon + Expander (Adjusted Grid)
                c_icon, c_exp = st.columns([1, 20]) # Tighter layout
                with c_icon:
                    st.markdown(html_content, unsafe_allow_html=True)

                with c_exp:
                    with st.expander(f"**{prov.upper()}** ({len(prov_models)} models)", expanded=(search_query != "" or show_sota)):
                        # Group by common prefixes if too many (optional, but good for OpenRouter)
                        if len(prov_models) > 20:
                             st.write(f"_{len(prov_models)} models available. Use search to find specific ones._")
                             
                        st.dataframe(
                            pd.DataFrame(prov_models, columns=["Model ID"]), 
                            use_container_width=True,
                            hide_index=True
                        )
        else:
            st.warning("No models found matching your search.")

