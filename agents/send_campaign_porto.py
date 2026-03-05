#!/usr/bin/env python3
"""Send Porto campaign plan to Joao for approval."""

import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import send_email

BASE_URL = "https://nacaovalente.com.pt/ads"

ADS = [
    {"name": "ad_event_1080x1080.png", "label": "Evento + Capa (Feed)", "w": "200"},
    {"name": "ad_quote_1080x1080.png", "label": "Citacao + Autor (Feed)", "w": "200"},
    {"name": "ad_story_1080x1920.png", "label": "Story Completo (9:16)", "w": "112"},
]


def build_email():
    visuals_html = """
        <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
          margin-top:36px;">Visuais para Aprovacao</h2>
        <p style="font-size:14px;color:#666;margin-bottom:16px;">
          3 conceitos criativos prontos para Meta Ads. Clicar para ver em tamanho real.</p>
        <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
          <tr>
    """
    for ad in ADS:
        url = f"{BASE_URL}/{ad['name']}"
        visuals_html += f"""
            <td style="padding:8px;text-align:center;vertical-align:top;">
              <a href="{url}" target="_blank" style="text-decoration:none;">
                <img src="{url}" alt="{ad['label']}"
                  width="{ad['w']}" style="display:block;border-radius:6px;
                  border:1px solid #ddd;">
              </a>
              <p style="font-size:11px;color:#888;margin:6px 0 0;
                font-family:Arial,sans-serif;">{ad['label']}</p>
            </td>
        """
    visuals_html += "</tr></table>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Georgia,serif;">
<div style="max-width:720px;margin:20px auto;background:#fff;border-radius:8px;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;">

  <div style="background:#1a1a2e;padding:32px 36px;">
    <h1 style="color:#C5A55A;margin:0;font-size:24px;">
      Campanha Porto — Para Aprovacao</h1>
    <p style="color:#aaa;margin:8px 0 0;font-size:14px;">
      Primeira campanha paga: Facebook + Instagram + Google Ads</p>
  </div>

  <div style="padding:32px 36px;color:#2c2c2c;line-height:1.8;font-size:15px;">

    <div style="background:#fff7ed;border-left:4px solid #C5A55A;padding:16px 20px;
      margin-bottom:28px;border-radius:0 6px 6px 0;">
      <p style="margin:0;font-size:15px;"><strong>Joao,</strong></p>
      <p style="margin:8px 0 0;">Preparei a primeira campanha paga para promover o lancamento
        do Porto (25 de Marco). Preciso da tua aprovacao para avancar.</p>
    </div>

    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:0;">Resumo da Campanha</h2>

    <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
      <tr style="background:#f9f6f0;">
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;width:35%;">
          Objectivo</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;">
          Inscricoes para o lancamento Porto (Google Form)</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;">Canais</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;">
          Facebook + Instagram (Meta Ads) + Google Search</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;">Periodo</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;">
          6 a 24 de Marco (19 dias)</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;">Orcamento Total</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-size:16px;">
          <strong style="color:#e94560;">&euro;400</strong>
          (Meta &euro;280 + Google &euro;80 + Reserva &euro;40)</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;">Resultado Esperado</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;">
          60-120 inscricoes (custo &euro;3-7 por inscricao)</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;font-weight:bold;">Plano Completo</td>
        <td style="padding:10px 14px;border:1px solid #e0ddd5;">
          <a href="https://nacaovalente.com.pt/campaign_porto.html"
            style="color:#C5A55A;font-weight:bold;">Ver plano detalhado</a>
          (copy de anuncios, targeting, timeline, KPIs)</td>
      </tr>
    </table>

    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:36px;">3 Conceitos de Anuncio</h2>
    <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
      <tr style="background:#1a1a2e;color:#C5A55A;">
        <th style="padding:8px 12px;text-align:left;">#</th>
        <th style="padding:8px 12px;text-align:left;">Conceito</th>
        <th style="padding:8px 12px;text-align:left;">Formato</th>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">1</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <strong>Evento + Capa</strong> — Lancamento Porto com data, local, "Esgotou em Lisboa"</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">1080x1080 (Feed)</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">2</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <strong>Citacao + Autor</strong> — "Defendo um Estado forte..." com foto e dados do evento</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">1080x1080 (Feed)</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">3</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <strong>Story Completo</strong> — Capa, titulo, evento, oradores, CTA</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">1080x1920 (Story/Reel)</td>
      </tr>
    </table>

    {visuals_html}

    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:36px;">O Que Preciso de Ti</h2>

    <div style="background:#e8f5e9;border-left:4px solid #27ae60;padding:16px 20px;
      border-radius:0 6px 6px 0;margin-bottom:16px;">
      <ol style="margin:0;padding-left:20px;font-size:14px;">
        <li style="margin-bottom:8px;"><strong>Aprovar o orcamento</strong> (&euro;400)
          — ou dizer qual o teu limite</li>
        <li style="margin-bottom:8px;"><strong>Aprovar os visuais</strong>
          — ou pedir alteracoes</li>
        <li style="margin-bottom:8px;"><strong>Criar conta Meta Business Suite</strong>
          (se ainda nao tens) e dar-me acesso, ou partilhar login</li>
        <li style="margin-bottom:8px;"><strong>Criar conta Google Ads</strong>
          e associar o cartao de pagamento</li>
        <li style="margin-bottom:8px;"><strong>Adicionar metodo de pagamento</strong>
          em ambas as plataformas</li>
      </ol>
    </div>

    <p style="font-size:14px;color:#666;">
      Assim que aprovares, configuro tudo e lancamos no dia seguinte.
      O site ja foi atualizado com a seccao do evento Porto + botao de inscricao.</p>

    <div style="margin-top:32px;padding-top:20px;border-top:2px solid #C5A55A;">
      <p style="color:#666;font-size:14px;margin:0;">
        Abraco,<br>
        <strong>Eugene Nayshtetik</strong><br>
        e.nayshtetik@gmail.com</p>
    </div>

  </div>

  <div style="background:#1a1a2e;padding:16px 36px;font-size:12px;color:#666;">
    Nacao Valente Campaign · nacaovalente.com.pt · Marco 2026
  </div>

</div></body></html>"""


def main():
    os.environ.setdefault("SMTP_EMAIL", "e.nayshtetik@gmail.com")
    os.environ.setdefault("NOTIFY_EMAIL", "joaomiguelannes@gmail.com")
    os.environ.setdefault("CC_EMAIL", "e.nayshtetik@gmail.com")

    html = build_email()
    send_email(
        "Nacao Valente — Campanha Porto: Para Aprovacao (FB + IG + Google)",
        html,
    )
    print("Campaign plan sent to Joao for approval!")


if __name__ == "__main__":
    main()
