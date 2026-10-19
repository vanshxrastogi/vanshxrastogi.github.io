import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class EmbeddedFilmMetadataTests(unittest.TestCase):
    def test_drive_films_use_player_metadata_and_local_posters(self):
        dist = Path(__file__).resolve().parents[1] / 'dist'
        content = json.loads((dist / 'content.json').read_text(encoding='utf-8'))
        ids = {'buddha-english-full-film'}
        projects = [p for p in content['projects'] if p['id'] in ids]
        self.assertEqual({p['id'] for p in projects}, ids)
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'v': 'http://www.google.com/schemas/sitemap-video/1.1'}
        sitemap = ET.parse(dist / 'video-sitemap.xml').getroot()
        for project in projects:
            with self.subTest(project=project['id']):
                page = (dist / 'films' / (project['id'] + '.html')).read_text(encoding='utf-8')
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page).group(1))
                self.assertNotIn('contentUrl', schema)
                self.assertEqual(schema['embedUrl'], project['embedUrl'])
                self.assertTrue(project['poster'].startswith('/media/'))
                self.assertTrue((dist / project['poster'].lstrip('/')).is_file())
                poster = 'https://vanshxrastogi.github.io' + project['poster']
                self.assertEqual(schema['thumbnailUrl'], [poster])
                parser = Tags()
                parser.feed(page)
                frame = next(attrs for tag, attrs in parser.tags if tag == 'iframe')
                self.assertEqual(frame['src'], project['embedUrl'])
                self.assertTrue(frame['title'])
                self.assertIn('allowfullscreen', frame)
                self.assertNotIn('autoplay', frame['allow'])
                viewport = project.get('presentationRatio', project['aspectRatio']).replace(':', '/')
                self.assertIn('aspect-ratio:' + viewport, frame['style'])
                self.assertTrue(any(tag == 'a' and attrs.get('href') == project['video'] for tag, attrs in parser.tags))
                row = next(row for row in sitemap if project['id'] in row.find('s:loc', ns).text)
                video = row.find('v:video', ns)
                self.assertIsNone(video.find('v:content_loc', ns))
                self.assertEqual(video.find('v:player_loc', ns).text, project['embedUrl'])
                self.assertEqual(video.find('v:thumbnail_loc', ns).text, poster)

    def test_verified_original_films_keep_exact_type_language_and_dimensions(self):
        dist = Path(__file__).resolve().parents[1] / 'dist'
        content = json.loads((dist / 'content.json').read_text(encoding='utf-8'))
        projects = {p['id']: p for p in content['projects']}
        expected = {
            'buddha-english-full-film': ('Full Film', 7296, 1080, '304:45', 539.2, 'PT8M59.2S'),
            'kherashwar-mahadev-trailer': ('Trailer', 3840, 2160, '16:9', 143.88, 'PT2M23.88S'),
        }
        for project_id, values in expected.items():
            with self.subTest(project=project_id):
                project = projects[project_id]
                content_type, width, height, ratio, seconds, iso_duration = values
                self.assertEqual(project['category'], 'ORIGINAL FILMS')
                self.assertEqual(project['contentType'], content_type)
                self.assertEqual((project['width'], project['height'], project['aspectRatio']), (width, height, ratio))
                self.assertEqual(project['durationSeconds'], seconds)
                page = (dist / 'films' / (project_id + '.html')).read_text(encoding='utf-8')
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page).group(1))
                self.assertEqual(schema['duration'], iso_duration)
                self.assertEqual((schema['width'], schema['height']), (width, height))
                self.assertNotIn('creator', schema)
                if project_id == 'buddha-english-full-film':
                    self.assertEqual(project['language'], 'English')
                    self.assertEqual(schema['inLanguage'], 'en')
        self.assertEqual(content['projectOrder'][:3], ['buddha-english-full-film', 'kherashwar-mahadev-trailer', 'room-4-ai-voice-experiment'])


if __name__ == '__main__':
    unittest.main()



