#!/usr/bin/env python3
"""Send campaign status report to João and Eugene."""

import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import send_email

REPORT_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Georgia,serif;">
<div style="max-width:720px;margin:20px auto;background:#fff;border-radius:8px;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;">

  <!-- Header -->
  <div style="background:#1a1a2e;padding:32px 36px;">
    <h1 style="color:#C5A55A;margin:0;font-size:26px;">Nação Valente — Campaign Report</h1>
    <p style="color:#aaa;margin:8px 0 0;font-size:14px;">
      Status: 4 de Março 2026 · Prepared by Eugene Nayshtetik</p>
  </div>

  <div style="padding:32px 36px;color:#2c2c2c;line-height:1.8;font-size:15px;">

    <!-- ═══ SECTION 1: COMPLETED ═══ -->
    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:0;">✅ O Que Foi Feito</h2>

    <!-- 1.1 Website -->
    <h3 style="color:#1a1a2e;margin-bottom:8px;">1. Website — nacaovalente.com.pt</h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;width:40%;">Landing Page</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Completa e online — hero com vídeo, secções Sobre o Livro, Autor, Lançamento,
          Comprar, Newsletter. Design responsivo (mobile + desktop).</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Certificado SSL</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Let's Encrypt instalado (válido até 1 Jun 2026). HTTPS funcional.</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Newsletter / Email Capture</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Formulário funcional com PHP backend. Dados guardados em base de dados MySQL.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Painel de Subscritores</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ <a href="https://nacaovalente.com.pt/admin.php" style="color:#C5A55A;">admin.php</a>
          — protegido por password, exportação CSV, proteção anti brute-force.</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">SEO</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Meta tags, Open Graph, Twitter Card, JSON-LD (Book schema), sitemap.xml,
          robots.txt, hreflang, alt tags — tudo implementado.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Vídeo Lançamento</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Adicionado à secção "Na Imprensa" — vídeo do lançamento na Culturgest
          + 3 outras aparições (DN, NOW Canal, IT Security Conference).</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Indexação</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Submetido ao IndexNow (Bing, Yandex, DuckDuckGo, Seznam, Naver).
          Google já conhece o site.</td>
      </tr>
    </table>

    <!-- 1.2 Content -->
    <h3 style="color:#1a1a2e;margin-bottom:8px;">2. Conteúdo de Promoção</h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;width:40%;">Plano Promocional</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ <a href="https://nacaovalente.com.pt/promo_plan.html" style="color:#C5A55A;">promo_plan.html</a>
          — calendário 6 semanas, gaps identificados, plano de ação.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Podcast Pitches</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ 5 pitches personalizados (Observador, Expresso, RTP, Polititank, FFMS)
          + template genérico + media kit.</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Emails de Reviews</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ Sequência de 3 emails para participantes do Culturgest + pedidos de
          endorsement aos 4 painelistas + template LinkedIn.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Calendário de Conteúdo</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ 6 semanas: 14 LinkedIn + 17 Instagram + 6 Stories = 37 peças de conteúdo.
          10 quote cards. Estratégia de hashtags.</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Templates Visuais</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          ✅ 10 Instagram quote cards + 5-slide carousel 4P + 5 anúncios Meta +
          4 banners LinkedIn. Todos em HTML pronto a exportar.</td>
      </tr>
    </table>

    <!-- 1.3 Automation -->
    <h3 style="color:#1a1a2e;margin-bottom:8px;">3. Agentes Automatizados (GitHub Actions)</h3>
    <p style="margin-bottom:12px;">9 agentes AI a correr automaticamente, enviam resultados por email:</p>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#1a1a2e;color:#C5A55A;">
        <th style="padding:8px 12px;text-align:left;">Agente</th>
        <th style="padding:8px 12px;text-align:left;">Horário</th>
        <th style="padding:8px 12px;text-align:left;">Função</th>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">News Hook Monitor</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Diário 8:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Monitoriza notícias PT e sugere oportunidades de ligação ao livro</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Review Tracker</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Diário 9:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Monitoriza reviews nas livrarias online (Bertrand, Wook, FNAC, Amazon)</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Content Generator</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Domingo 19:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Gera templates de conteúdo semanal por tema</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">LinkedIn Ghostwriter</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Segunda 9:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">3 posts LinkedIn prontos a publicar na voz do João</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Instagram Curator</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Segunda 10:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Plano semanal do grid: 5 posts + captions + hashtags + Stories</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Image Prompt Engineer</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Segunda 11:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">5 prompts Midjourney/DALL-E para criar visuais da semana</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Social Media Strategist</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Terça + Sexta 8:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Tópicos trending + ângulos de engagement para LinkedIn</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Visual Storyteller</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Terça 9:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Conceitos: 1 carousel + 1 sequência Stories + 1 Reel/vídeo</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Trend Researcher</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Quarta 9:00</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Intelligence brief semanal: tendências, concorrência, oportunidades</td>
      </tr>
    </table>
    <p style="font-size:13px;color:#666;">
      <strong>Nota:</strong> Os horários são hora de Lisboa. Todos os agentes enviam
      resultados por email para joaomiguelannes@gmail.com (CC: e.nayshtetik@gmail.com).
      Os agentes a <strong>negrito</strong> são os 6 novos (Tier 1).</p>

    <!-- ═══ SECTION 2: TO DO ═══ -->
    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:36px;">📋 O Que Falta Fazer (Ações do João)</h2>

    <h3 style="color:#c0392b;margin-bottom:8px;">🔴 Prioridade Alta — Esta Semana</h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#fdf2f2;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;width:5%;font-weight:bold;">1</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;width:30%;font-weight:bold;">Google Search Console</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Ir a <a href="https://search.google.com/search-console/welcome" style="color:#C5A55A;">search.google.com/search-console</a>
          → Adicionar propriedade → "URL prefix" → <code>https://nacaovalente.com.pt/</code>
          → Verificar (HTML tag ou DNS) → Submeter sitemap.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">2</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Bing Webmaster Tools</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Ir a <a href="https://www.bing.com/webmasters/" style="color:#C5A55A;">bing.com/webmasters</a>
          → Adicionar site → Verificar → Submeter sitemap.</td>
      </tr>
      <tr style="background:#fdf2f2;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">3</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Instagram Bio</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Atualizar link na bio de @nacaovalente para <code>https://nacaovalente.com.pt/</code></td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">4</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">LinkedIn Featured</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Adicionar na secção "Em destaque" do perfil LinkedIn: link do site + capa do livro.</td>
      </tr>
      <tr style="background:#fdf2f2;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">5</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Facebook Page</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Atualizar website na Página Facebook + publicar post com link do lançamento.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">6</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Goodreads</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Ir a <a href="https://www.goodreads.com/book/new" style="color:#C5A55A;">goodreads.com/book/new</a>
          → Criar página de autor + adicionar livro com ISBN, capa e descrição.</td>
      </tr>
      <tr style="background:#fdf2f2;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">7</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Amazon Author Central</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Ir a <a href="https://author.amazon.co.uk/" style="color:#C5A55A;">author.amazon.co.uk</a>
          → Reclamar página de autor, adicionar bio e link para nacaovalente.com.pt.</td>
      </tr>
    </table>

    <h3 style="color:#e67e22;margin-bottom:8px;">🟡 Prioridade Média — Este Mês</h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#fef9f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;width:35%;">Open Library</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="https://openlibrary.org/books/add" style="color:#C5A55A;">openlibrary.org/books/add</a>
          → Adicionar por ISBN: 978-989-693-214-5 (preenche automaticamente).</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Google Business Profile</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="https://business.google.com/create" style="color:#C5A55A;">business.google.com</a>
          → Criar perfil como Livro/Produto.</td>
      </tr>
      <tr style="background:#fef9f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Enviar Podcast Pitches</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          5 pitches prontos no ficheiro podcast_pitches.html. Enviar para:
          Observador, Expresso, RTP, Polititank, FFMS.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Enviar Pedidos de Review</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Emails prontos no review_emails.html. Sequência de 3 emails para
          participantes do Culturgest + pedidos aos painelistas.</td>
      </tr>
      <tr style="background:#fef9f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">ResearchGate / ORCID</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Criar/atualizar perfil, adicionar livro como publicação.</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">SEDES</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Pedir menção/listagem do livro no site da SEDES.</td>
      </tr>
      <tr style="background:#fef9f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Worten / El Corte Inglés</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          Verificar se o livro está disponível nestes canais adicionais.</td>
      </tr>
    </table>

    <h3 style="color:#27ae60;margin-bottom:8px;">🟢 Ações Contínuas (Os Agentes Ajudam)</h3>
    <ul style="font-size:14px;">
      <li><strong>Segundas-feiras:</strong> Recebe por email 3 posts LinkedIn + grid Instagram
        + prompts para imagens. Rever, ajustar, publicar.</li>
      <li><strong>Terças e Sextas:</strong> Recebe oportunidades de engagement em trending topics.
        Comentar nos posts sugeridos.</li>
      <li><strong>Quartas:</strong> Recebe intelligence brief semanal. Usar para decidir
        prioridades de conteúdo.</li>
      <li><strong>Diariamente:</strong> Monitorização de notícias e reviews automática.</li>
    </ul>

    <!-- ═══ SECTION 3: INFRASTRUCTURE ═══ -->
    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:36px;">🔧 Infraestrutura Técnica</h2>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;width:35%;">Hosting</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">bravo.acloud.pt (VPN required)</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Domínio</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">nacaovalente.com.pt (SSL Let's Encrypt ativo)</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">GitHub Repo</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="https://github.com/Skabber2000/Brave_Nation" style="color:#C5A55A;">
          github.com/Skabber2000/Brave_Nation</a></td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Base de Dados</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">MySQL: c15valente (para subscritores newsletter)</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">AI API</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">OpenAI GPT-4o (agentes automáticos)</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">Email Automático</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">Gmail SMTP (App Password)</td>
      </tr>
    </table>

    <!-- ═══ SECTION 4: ACCESS ═══ -->
    <h2 style="color:#1a1a2e;border-bottom:2px solid #C5A55A;padding-bottom:8px;
      margin-top:36px;">🔑 Acessos Importantes</h2>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:14px;">
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;width:35%;">Painel de Subscritores</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="https://nacaovalente.com.pt/admin.php" style="color:#C5A55A;">nacaovalente.com.pt/admin.php</a>
          <br>Password: <code>NV_admin_2026!</code></td>
      </tr>
      <tr>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">phpMyAdmin</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="http://nacaovalente.com.pt/phpmyadmin" style="color:#C5A55A;">nacaovalente.com.pt/phpmyadmin</a>
          <br>User: c15valente</td>
      </tr>
      <tr style="background:#f9f6f0;">
        <td style="padding:8px 12px;border:1px solid #e0ddd5;font-weight:bold;">GitHub Actions</td>
        <td style="padding:8px 12px;border:1px solid #e0ddd5;">
          <a href="https://github.com/Skabber2000/Brave_Nation/actions" style="color:#C5A55A;">
          github.com/.../actions</a> — ver estado dos 9 agentes</td>
      </tr>
    </table>

    <!-- Signature -->
    <div style="margin-top:40px;padding-top:20px;border-top:2px solid #C5A55A;">
      <p style="color:#666;font-size:14px;margin:0;">
        Qualquer dúvida, é só dizer.<br>
        <strong>Eugene Nayshtetik</strong><br>
        e.nayshtetik@gmail.com</p>
    </div>

  </div>

  <div style="background:#1a1a2e;padding:16px 36px;font-size:12px;color:#666;">
    Nação Valente Campaign · nacaovalente.com.pt · Março 2026
  </div>

</div></body></html>"""


def main():
    os.environ.setdefault("SMTP_EMAIL", "e.nayshtetik@gmail.com")
    os.environ.setdefault("NOTIFY_EMAIL", "joaomiguelannes@gmail.com")
    os.environ.setdefault("CC_EMAIL", "e.nayshtetik@gmail.com")

    send_email(
        "Nação Valente — Relatório da Campanha (4 Mar 2026)",
        REPORT_HTML,
    )
    print("✅ Report sent!")


if __name__ == "__main__":
    main()
