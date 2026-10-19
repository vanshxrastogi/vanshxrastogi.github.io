import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_blog
import build_pages

class BlogSafetyTests(unittest.TestCase):
    def test_drafts_are_excluded_from_production_and_feed(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as tmp:
            dest=Path(tmp); build_blog.build_blog(dest)
            for p in build_blog.load_posts(True):
                self.assertFalse((dest/'blog'/p['slug']/'index.html').exists())
                self.assertNotIn(p['slug'],(dest/'sitemap.xml').read_text())
                self.assertNotIn(p['slug'],(dest/'blog/feed.xml').read_text())
            ET.parse(dest/'sitemap.xml'); ET.parse(dest/'blog/feed.xml')
    def test_preview_drafts_are_noindex_and_links_resolve(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as tmp:
            dest=Path(tmp); posts=build_blog.build_blog(dest,True)
            self.assertEqual(len(posts),3)
            for p in posts:
                text=(dest/'blog'/p['slug']/'index.html').read_text(encoding='utf-8')
                self.assertIn('noindex,follow',text)
                self.assertIn('EDITORIAL PREVIEW',text)
                self.assertIn('"@type": "Article"',text)
    def test_markdown_cannot_inject_html_or_javascript(self):
        text,_=build_blog.markdown('<script>alert(1)</script>')
        self.assertNotIn('<script>',text)
        with self.assertRaises(ValueError): build_blog.markdown('[bad](javascript:alert)')
    def test_existing_meta_does_not_block_approved_ad_script(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as tmp:
            dest=Path(tmp); (dest/'index.html').write_text('<head><meta name="google-adsense-account" content="ca-pub-4425848148181831"></head>')
            cfg={'publisherId':'ca-pub-4425848148181831','enableAds':True,'approvedSite':True,'consentConfigured':True,'adPaths':['/index.html']}
            (dest/'monetization.json').write_text(json.dumps(cfg)); build_pages.configure_adsense(dest); build_pages.configure_adsense(dest)
            self.assertEqual((dest/'index.html').read_text().count('pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'),1)
    def test_unapproved_ads_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as tmp:
            dest=Path(tmp); (dest/'monetization.json').write_text(json.dumps({'publisherId':'ca-pub-4425848148181831','enableAds':True}))
            with self.assertRaises(ValueError): build_pages.configure_adsense(dest)

if __name__=='__main__': unittest.main()

