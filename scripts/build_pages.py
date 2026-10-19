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

if __name__ == '__main__':
    build()


