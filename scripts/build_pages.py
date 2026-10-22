"""Prepare portable Pages URLs and optional, verified AdSense integration."""
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

PRIMARY = 'https://vanshxrastogi.github.io'
LEGACY = 'https://vansh-rastogi-film.unscriptedstorylab.chatgpt.site'

def build(source=Path('dist'), destination=Path('_site'), site_url=None):
    site_url = (site_url or os.environ['SITE_URL']).rstrip('/')
    parsed = urlsplit(site_url)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('SITE_URL must be a clean absolute HTTPS URL')
    base = parsed.path.rstrip('/')
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    # Generate only for the actual repository, not isolated portable-build fixtures.
    if source.resolve() == Path(__file__).resolve().parents[1] / 'dist':
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_blog import build_blog
        build_blog(destination)
    text_types = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.webmanifest'}
    for path in destination.rglob('*'):
        if not path.is_file() or path.suffix not in text_types:
            continue
        text = path.read_text(encoding='utf-8')
        # Sites-hosted media remains external; page and canonical URLs stay portable.
        site_hosts = re.escape(LEGACY) + r'(?!/media/)' + '|' + re.escape(PRIMARY)
        text = re.sub(site_hosts, lambda _: site_url, text)
        if base:
            if path.suffix == '.html':
                text = re.sub(r'''(\b(?:href|src|poster|action)=["'])/(?!/)''', lambda m: m[1] + base + '/', text)
            if path.suffix in {'.js', '.json', '.webmanifest'}:
                text = re.sub(r'''(["'`])/(?!/)''', lambda m: m[1] + base + '/', text)
            if path.suffix == '.css':
                text = re.sub(r'''(url\(["']?)/(?!/)''', lambda m: m[1] + base + '/', text)
            if path.name == 'robots.txt':
                text = re.sub(r'(?m)^(Allow|Disallow): /(.*)$', lambda m: m[1] + ': ' + base + '/' + m[2], text)
        path.write_text(text, encoding='utf-8')
    configure_adsense(destination)
    if site_url == PRIMARY and source.resolve() == Path(__file__).resolve().parents[1] / 'dist':
        configure_analytics(destination)
    (destination / '.nojekyll').touch()
    print('Prepared GitHub Pages artifact:', destination)

def configure_adsense(destination):
    config_file = destination / 'monetization.json'
    if not config_file.exists():
        return
    config = json.loads(config_file.read_text(encoding='utf-8'))
    publisher = config.get('publisherId', '')
    enabled = config.get('enableAds', False)
    if not publisher:
        if enabled:
            raise ValueError('AdSense requires your real publisher ID')
        return
    if not re.fullmatch(r'ca-pub-\d{16}', publisher):
        raise ValueError('Invalid AdSense publisher ID')
    if enabled and not (config.get('approvedSite') is True and config.get('consentConfigured') is True):
        raise ValueError('Enable ads only after site approval and required consent setup')
    meta = '<meta name="google-adsense-account" content="' + publisher + '">'
    script = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + publisher + '" crossorigin="anonymous"></script>'
    eligible = set(config.get('adPaths', []))
    for path in destination.rglob('*.html'):
        relative = '/' + path.relative_to(destination).as_posix()
        code = meta
        if enabled and relative in eligible:
            code += script
        text = path.read_text(encoding='utf-8')
        additions = ''
        if 'name="google-adsense-account"' not in text:
            additions += meta
        if enabled and relative in eligible and 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' not in text:
            additions += script
        path.write_text(text.replace('</head>', additions + '</head>', 1), encoding='utf-8')
    (destination / 'ads.txt').write_text('google.com, ' + publisher.removeprefix('ca-') + ', DIRECT, f08c47fec0942fa0\n')

def configure_analytics(destination):
    """Basic consent: load GA4 only after opt-in, across static and generated pages."""
    javascript = r'''(() => {
  'use strict';
  if (location.hostname !== 'vanshxrastogi.github.io') return;
  const id = 'G-F1C19J899E', key = 'vr-analytics-consent-v1';
  let choice = null, loaded = false;
  try { choice = localStorage.getItem(key); } catch (_) {}
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  const denied = {analytics_storage:'denied', ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied'};
  window.gtag('consent', 'default', denied);
  function start() {
    window['ga-disable-' + id] = false;
    window.gtag('consent', 'update', {...denied, analytics_storage:'granted'});
    if (loaded) return;
    loaded = true;
    window.gtag('js', new Date());
    window.gtag('config', id, {allow_google_signals:false, allow_ad_personalization_signals:false, cookie_domain:location.hostname, page_location:location.origin + location.pathname});
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(script);
  }
  const style = document.createElement('style');
  style.textContent = '#vr-consent{position:fixed;inset:auto 16px 16px auto;max-width:420px;width:calc(100% - 32px);box-sizing:border-box;padding:20px;background:#fff8ec;color:#351b22;border:1px solid #987342;box-shadow:0 8px 32px #0003;border-radius:12px;z-index:10000;font:15px/1.5 system-ui}#vr-consent[hidden]{display:none}#vr-consent p{margin:0 0 12px}#vr-consent a{color:#632837;text-decoration:underline}#vr-consent button,#vr-privacy-choice{font:inherit;cursor:pointer;border:1px solid #632837;border-radius:5px;padding:9px 13px;background:#fff8ec;color:#632837}#vr-consent button{margin:4px 8px 0 0}#vr-consent button:focus-visible,#vr-privacy-choice:focus-visible{outline:3px solid #987342;outline-offset:3px}#vr-privacy-choice{display:block;margin:16px auto;font:12px system-ui}';
  document.head.appendChild(style);
  const panel = document.createElement('section');
  panel.id = 'vr-consent';
  panel.setAttribute('aria-label', 'Analytics privacy choices');
  panel.innerHTML = '<p><strong>Your privacy, your choice.</strong></p><p>Allow Google Analytics to measure visits and interactions so I can improve this portfolio? Optional analytics stays off until you agree. <a href="/privacy.html">Privacy policy</a></p><button type="button" data-choice="granted">Allow analytics</button><button type="button" data-choice="denied">No thanks</button>';
  panel.hidden = choice === 'granted' || choice === 'denied';
  document.body.appendChild(panel);
  const settings = document.createElement('button');
  settings.id = 'vr-privacy-choice'; settings.type = 'button'; settings.textContent = 'Analytics privacy choices';
  (document.querySelector('footer') || document.body).appendChild(settings);
  settings.addEventListener('click', () => { panel.hidden = false; panel.querySelector('button').focus(); });
  panel.addEventListener('click', event => {
    const button = event.target.closest('button[data-choice]');
    if (!button) return;
    choice = button.dataset.choice;
    try { localStorage.setItem(key, choice); } catch (_) {}
    if (choice === 'granted') start();
    else {
      window['ga-disable-' + id] = true;
      window.gtag('consent', 'update', denied);
      document.cookie.split(';').forEach(cookie => {
        const name = cookie.split('=')[0].trim();
        if (name === '_ga' || name.startsWith('_ga_')) {
          document.cookie = name + '=; Max-Age=0; path=/';
          document.cookie = name + '=; Max-Age=0; path=/; domain=' + location.hostname;
        }
      });
    }
    panel.hidden = true; settings.focus();
  });
  if (choice === 'granted') start();
})();'''
    (destination / 'portfolio-analytics.js').write_text(javascript, encoding='utf-8')
    tag = '<script defer src="/portfolio-analytics.js?v=1"></script>'
    for path in destination.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        if 'portfolio-analytics.js' not in text:
            text = text.replace('</head>', tag + '</head>', 1)
        if path.name == 'privacy.html':
            text = text.replace('LAST UPDATED: 19 OCTOBER 2026', 'LAST UPDATED: 21 OCTOBER 2026')
            text = text.replace('Google AdSense advertising and Google Analytics are not currently enabled on this site. Form security services may use cookies or similar technologies.', 'Google Analytics 4 is used only after you choose Allow analytics. It measures page views and interactions, and may process device and browser information and use analytics cookies. Your choice is saved in this browser. You can decline or withdraw consent using Analytics privacy choices in the footer; declining does not prevent use of the portfolio. Google advertising signals and ad personalisation are disabled in this integration. Google AdSense advertising remains disabled. Form security services may use cookies or similar technologies. <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google privacy policy</a>.')
        path.write_text(text, encoding='utf-8')

if __name__ == '__main__':
    build()


