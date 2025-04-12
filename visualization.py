import matplotlib.pyplot as plt
from date_utils import calculate_duration, calculate_total_experience_direct
import os
import plotly.graph_objects as go
import plotly.express as px  # En üste eklendiğinden emin ol
import os
from collections import defaultdict
from date_utils import calculate_duration, calculate_total_experience_direct
import pandas as pd

# Grafiklerin kaydedileceği klasör (Flask'ın static klasörü içinde olacak)
CHART_DIR = os.path.join("web_viewer", "static", "charts")
os.makedirs(CHART_DIR, exist_ok=True)

def save_similarity_scores_bar(all_matches):
    labels = [f"{item['position']} @ {item['company']}" for item in all_matches]
    scores = [item['score'] for item in all_matches]

    plt.figure(figsize=(10, 6))
    plt.barh(labels, scores)
    plt.xlabel("Benzerlik Skoru (S-BERT)")
    plt.title("Pozisyonlara Göre Eşleşme Skorları")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "similarity.png"), dpi=150)
    plt.close()

def save_position_durations_bar(all_work_periods):
    labels = []
    durations_in_months = []

    for period in all_work_periods:
        dur_str = calculate_duration(period['start'], period['end'])
        if dur_str:
            y, m = calculate_total_experience_direct([dur_str])
            months = y * 12 + m
            labels.append(f"{period['position']} @ {period['company']}")
            durations_in_months.append(months)

    plt.figure(figsize=(10, 6))
    plt.barh(labels, durations_in_months)
    plt.xlabel("Süre (ay)")
    plt.title("Pozisyon Bazında Çalışma Süresi")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "position_durations.png"), dpi=150)
    plt.close()

def save_onet_experience_pie(onet_code_groups, all_work_periods):
    onet_totals = {}
    for onet_code, match_infos in onet_code_groups.items():
        durations = []
        for match in match_infos:
            for period in all_work_periods:
                if match['position'] == period['position'] and match['company'] == period['company']:
                    dur = calculate_duration(period['start'], period['end'])
                    if dur:
                        durations.append(dur)
        years, months = calculate_total_experience_direct(durations)
        total_months = years * 12 + months
        if total_months > 0:
            onet_totals[onet_code] = total_months

    if not onet_totals:
        return

    labels = list(onet_totals.keys())
    values = list(onet_totals.values())

    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("O*NET Kodlarına Göre Dağılım (Pasta Grafik)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "onet_experience.png"), dpi=150)
    plt.close()

def save_matched_titles_pie(all_matches, all_work_periods, occupation_data):
    from collections import defaultdict
    import matplotlib.patches as mpatches

    matched_totals = defaultdict(list)

    # Grupla: matched title => durations
    for match_info in all_matches:
        matched_title = match_info['match']['alternate_title']
        position = match_info['position']
        company = match_info['company']

        for period in all_work_periods:
            if period['position'] == position and period['company'] == company:
                duration = calculate_duration(period['start'], period['end'])
                if duration:
                    matched_totals[matched_title].append(duration)

    # Ay cinsine çevir
    labels, values, durations = [], [], []
    for title, duration_list in matched_totals.items():
        y, m = calculate_total_experience_direct(duration_list)
        months = y * 12 + m
        if months > 0:
            labels.append(title)
            values.append(months)
            durations.append(f"{y} yıl {m} ay")

    # Pie chart
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(values, autopct='%1.1f%%', startangle=140)

    # Legend için renkli etiketler
    legend_labels = [f"{label} – {durations[i]}" for i, label in enumerate(labels)]
    patches = [mpatches.Patch(color=w.get_facecolor(), label=legend_labels[i]) for i, w in enumerate(wedges)]

    plt.legend(handles=patches, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    plt.title("Matched Mesleklere Göre Toplam Süre (Pasta Grafik)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "matched_titles_pie.png"), dpi=150)
    plt.close()

def save_position_titles_pie(all_work_periods):
    from collections import defaultdict
    import matplotlib.patches as mpatches

    durations_by_position = defaultdict(list)

    for period in all_work_periods:
        position = period['position']
        duration = calculate_duration(period['start'], period['end'])
        if duration:
            durations_by_position[position].append(duration)

    labels, values, durations = [], [], []
    for pos, duration_list in durations_by_position.items():
        y, m = calculate_total_experience_direct(duration_list)
        total_months = y * 12 + m
        if total_months > 0:
            labels.append(pos)
            values.append(total_months)
            durations.append(f"{y} yıl {m} ay")

    # Pie chart
    plt.figure(figsize=(8, 8))
    wedges, _, _ = plt.pie(values, autopct='%1.1f%%', startangle=140)

    legend_labels = [f"{label} – {durations[i]}" for i, label in enumerate(labels)]
    patches = [mpatches.Patch(color=w.get_facecolor(), label=legend_labels[i]) for i, w in enumerate(wedges)]

    plt.legend(handles=patches, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    plt.title("Pozisyonlara Göre Toplam Çalışma Süresi (Pasta Grafik)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "position_titles_pie.png"), dpi=150)
    plt.close()

   

HTML_CHART_DIR = os.path.join("web_viewer", "static", "charts_html")
os.makedirs(HTML_CHART_DIR, exist_ok=True)

#todo: ALTERNATİVE TİTLE GÖRE PASTA GRAFİĞİ
def save_matched_titles_pie_plotly(all_matches, all_work_periods):
    durations_by_title = defaultdict(list)

    for match_info in all_matches:
        matched_title = match_info['match']['alternate_title']
        position = match_info['position']
        company = match_info['company']

        for period in all_work_periods:
            if position == period['position'] and company == period['company']:
                duration = calculate_duration(period['start'], period['end'])
                if duration:
                    durations_by_title[matched_title].append(duration)

    labels, values, hovertexts = [], [], []

    for title, duration_list in durations_by_title.items():
        y, m = calculate_total_experience_direct(duration_list)
        total_months = y * 12 + m
        if total_months > 0:
            labels.append(title)
            values.append(total_months)
            hovertexts.append(f"{title}<br>{y} yıl {m} ay")

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='percent',
        hoverinfo='text',
        hovertext=hovertexts,
        hole=0.4
    )])

    fig.update_layout(
        title_text="🧠 Matched Mesleklere Göre Süre (Plotly Pasta Grafik)",
        showlegend=True,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#333", size=14),
    )

    fig.write_html(os.path.join(HTML_CHART_DIR, "matched.html"))

from datetime import datetime

def save_career_timeline_plotly(all_work_periods):
    import plotly.express as px
    import pandas as pd
    from datetime import datetime
    import os

    HTML_CHART_DIR = os.path.join("web_viewer", "static", "charts_html")
    os.makedirs(HTML_CHART_DIR, exist_ok=True)

    timeline_data = []

    for period in all_work_periods:
        position = period.get("position", "Unknown")
        company = period.get("company", "Unknown")
        start = period.get("start")
        end = period.get("end")

        # 🔍 log at: hangi kayıt işleniyor
        print(f"👉 Pozisyon: {position} @ {company} | Start: {start} | End: {end}")

        # 💥 Eksik veri varsa atla
        if not start or not end:
            print("⛔ Boş tarih - atlandı")
            continue
        if isinstance(start, str) and "unknown" in start.lower():
            continue
        if isinstance(end, str) and "unknown" in end.lower():
            continue
        if isinstance(end, str) and "present" in end.lower():
            end = datetime.today().strftime('%Y-%m-%d')

        try:
            start_dt = pd.to_datetime(start, errors="coerce")
            end_dt = pd.to_datetime(end, errors="coerce")

            if pd.isna(start_dt) or pd.isna(end_dt):
                print("❌ Tarih çevrilemedi - atlandı")
                continue

            timeline_data.append({
                "Pozisyon": position,
                "Şirket": company,
                "Başlangıç": start_dt,
                "Bitiş": end_dt
            })
        except Exception as e:
            print(f"⚠️ Hata: {e}")

    if not timeline_data:
        print("🚫 Hiç geçerli pozisyon eklenemedi.")
        return

    df = pd.DataFrame(timeline_data)

    fig = px.timeline(
        df,
        x_start="Başlangıç",
        x_end="Bitiş",
        y="Pozisyon",
        color="Şirket",
        hover_name="Şirket",
        title="📈 Kariyer Gelişim Grafiği"
    )

    fig.update_layout(
        xaxis_title="Zaman",
        yaxis_title="Pozisyon",
        yaxis=dict(autorange="reversed"),
        height=500,
        margin=dict(l=100, r=40, t=60, b=40),
        font=dict(size=14)
    )

    fig.write_html(os.path.join(HTML_CHART_DIR, "career.html"))





def save_company_durations_pie_plotly(all_work_periods):
    from collections import defaultdict
    durations_by_company = defaultdict(list)

    for period in all_work_periods:
        company = period['company']
        duration = calculate_duration(period['start'], period['end'])
        if duration:
            durations_by_company[company].append(duration)

    labels, values, hovertexts = [], [], []
    for comp, duration_list in durations_by_company.items():
        y, m = calculate_total_experience_direct(duration_list)
        total_months = y * 12 + m
        if total_months > 0:
            labels.append(comp)
            values.append(total_months)
            hovertexts.append(f"{comp}<br>{y} yıl {m} ay")

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='label+percent',
        hoverinfo='text',
        hovertext=hovertexts,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Magma, line=dict(color='white', width=2))
    )])

    fig.update_layout(
        title_text="🏢 Şirketlere Göre Çalışma Süresi",
        showlegend=True,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#333", size=14),
    )

    fig.write_html(os.path.join(HTML_CHART_DIR, "company.html"))

def save_onet_experience_pie_plotly(onet_code_groups, all_work_periods, occupation_data):
    from collections import defaultdict
    onet_totals = {}

    for onet_code, match_infos in onet_code_groups.items():
        durations = []
        for match in match_infos:
            for period in all_work_periods:
                if match['position'] == period['position'] and match['company'] == period['company']:
                    dur = calculate_duration(period['start'], period['end'])
                    if dur:
                        durations.append(dur)
        y, m = calculate_total_experience_direct(durations)
        total_months = y * 12 + m
        if total_months > 0:
            title = occupation_data[onet_code]["title"] if onet_code in occupation_data else onet_code
            onet_totals[title] = total_months

    labels = list(onet_totals.keys())
    values = list(onet_totals.values())
    hovertexts = [f"{title}<br>{val // 12} yıl {val % 12} ay" for title, val in onet_totals.items()]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='percent',
        hoverinfo='text',
        hovertext=hovertexts,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Viridis, line=dict(color='white', width=2))
    )])

    fig.update_layout(
        title_text="🧩 Mesleklere Göre Toplam Deneyim (O*NET)",
        showlegend=True,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#333", size=14),
    )

    fig.write_html(os.path.join(HTML_CHART_DIR, "onet.html"))



