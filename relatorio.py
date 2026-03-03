import io
import streamlit as st
import pandas as pd
from datetime import datetime
from analysis.metrics import calcular_saldo, votos_por_local, filtrar_por_item


def _gerar_pdf(dados: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable, PageBreak)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Estilos customizados
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'],
                                     fontSize=13, textColor=colors.HexColor('#318ce7'), spaceBefore=14, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                fontSize=10, leading=14, spaceAfter=4)
    caption_style = ParagraphStyle('Caption', parent=styles['Normal'],
                                   fontSize=8, textColor=colors.grey, spaceAfter=8)

    story = []

    # Cabeçalho
    story.append(Paragraph("📊 Radar Eleitoral SC", titulo_style))
    story.append(Paragraph("Relatório de Inteligência Eleitoral", styles['Heading3']))
    story.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | "
        f"Cargo: {dados['cargo']} | Ano: {dados['ano']} | "
        f"Filtro: {dados['mun']}",
        caption_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#318ce7')))
    story.append(Spacer(1, 0.3*cm))

    for item_data in dados['candidatos']:
        item = item_data['nome']
        story.append(Paragraph(item, subtitulo_style))

        # KPIs
        kpi_data = [
            ['Métrica', '2018', '2022', 'Variação'],
            ['Votos totais',
             f"{item_data['v18']:,}", f"{item_data['v22']:,}",
             f"{'▲' if item_data['dif'] > 0 else '▼'} {abs(item_data['dif']):,} ({item_data['perc']:+.1f}%)"],
            ['Share (%)', '-', f"{item_data['share']:.2f}%", '-'],
            ['Posição no ranking', '-', f"{item_data['posicao']}º", '-'],
            ['Municípios com votos', '-', f"{item_data['n_municipios']}", '-'],
        ]
        t = Table(kpi_data, colWidths=[5*cm, 3*cm, 3*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#318ce7')),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))

        # Top 10 municípios
        if item_data.get('top10'):
            story.append(Paragraph("Top 10 Municípios por Votos", styles['Heading4']))
            top_data = [['Município', 'Votos', 'Share (%)']] + [
                [r['nm_municipio'], f"{int(r['qt_votos']):,}", f"{r['share']:.2f}%"]
                for r in item_data['top10']
            ]
            t2 = Table(top_data, colWidths=[8*cm, 4*cm, 4*cm])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f4ff')),
                ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t2)

        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Radar Eleitoral SC — Relatório gerado automaticamente.", caption_style))

    doc.build(story)
    return buffer.getvalue()


def render(df_atual, df_18, df_22, selecionados_todos, mun_sel, ano_sel, cargo_sel):
    st.subheader("📰 Relatório Automático em PDF")
    st.caption("Gera um relatório completo com os principais indicadores dos candidatos selecionados.")

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral para gerar o relatório.")
        return

    if st.button("📄 Gerar Relatório PDF", use_container_width=True, key="gerar_relatorio"):
        with st.spinner("Gerando relatório..."):
            dados = {
                "cargo": cargo_sel,
                "ano": ano_sel,
                "mun": mun_sel,
                "candidatos": []
            }

            df_base = df_atual.copy()
            if mun_sel != "TODOS":
                df_base = df_base[df_base['nm_municipio'] == mun_sel]
            total_votos = df_base['qt_votos'].sum()

            ranking_geral = (df_base.groupby('nm_votavel')['qt_votos'].sum()
                             .sort_values(ascending=False).reset_index())
            ranking_geral.index += 1

            for item in selecionados_todos:
                saldo = calcular_saldo(df_18, df_22, item, mun_sel)
                v_atual = votos_por_local(df_atual, item, mun_sel)
                share = (v_atual / total_votos * 100) if total_votos > 0 else 0

                try:
                    posicao = ranking_geral[ranking_geral['nm_votavel'] == item].index[0]
                except IndexError:
                    posicao = "-"

                df_item = filtrar_por_item(df_base, item)
                n_municipios = df_item['nm_municipio'].nunique() if 'nm_municipio' in df_item.columns else 0

                # Top 10 municípios
                votos_mun = df_item.groupby('nm_municipio')['qt_votos'].sum().reset_index()
                total_mun = df_base.groupby('nm_municipio')['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total'})
                votos_mun = votos_mun.merge(total_mun, on='nm_municipio')
                votos_mun['share'] = (votos_mun['qt_votos'] / votos_mun['total'] * 100).round(2)
                top10 = votos_mun.sort_values('qt_votos', ascending=False).head(10).to_dict('records')

                dados["candidatos"].append({
                    "nome": item,
                    "v18": int(saldo["v_18"]),
                    "v22": int(saldo["v_22"]),
                    "dif": int(saldo["dif"]),
                    "perc": round(saldo["perc"], 1),
                    "share": round(share, 2),
                    "posicao": posicao,
                    "n_municipios": n_municipios,
                    "top10": top10
                })

            pdf_bytes = _gerar_pdf(dados)

        nome_arquivo = f"relatorio_radar_eleitoral_{ano_sel}.pdf"
        st.success("✅ Relatório gerado com sucesso!")
        st.download_button(
            label="⬇️ Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=nome_arquivo,
            mime="application/pdf",
            key="dl_relatorio_pdf"
        )

        # Preview das métricas
        st.markdown("#### Preview do conteúdo")
        for item_data in dados["candidatos"]:
            with st.expander(f"📍 {item_data['nome']}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Votos 2022", f"{item_data['v22']:,}")
                c2.metric("Share", f"{item_data['share']:.2f}%")
                c3.metric("Posição", f"{item_data['posicao']}º")
                c4.metric("Municípios", item_data['n_municipios'])
