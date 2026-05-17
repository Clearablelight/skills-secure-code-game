# Run tests.py by following the instructions below:

# This file contains passing tests.

# Run them by opening a terminal and running the following:
# $ python3 Season-2/Level-4/tests.py

# Note: first you have to run code.py following the instructions
# on top of that file so that the environment variables align but
# it's not necessary to run both files in parallel as the tests
# initialize a new environment, similar to code.py

from code import app, get_planet_info
import unittest
from flask_testing import TestCase

class MyTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        return app

    def test_index_route(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertTemplateUsed('index.html')

    def test_get_planet_info_invalid_planet(self):
        planet = 'Pluto'
        expected_info = 'Unknown planet.'
        result = get_planet_info(planet)
        self.assertEqual(result, expected_info)

    def test_get_planet_info_valid_planet(self):
        planet = 'Mercury'
        expected_info = 'The smallest and fastest planet in the Solar System.'
        result = get_planet_info(planet)
        self.assertEqual(result, expected_info)

    def test_index_valid_planet(self):
        planet = 'Venus'
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        self.assertEqual(response.data.decode()[:15], '<!DOCTYPE html>')

    def test_index_missing_planet(self):
        response = self.client.post('/')
        self.assert200(response)
        self.assertEqual(response.data.decode(), '<h2>Please enter a planet name.</h2>')

    def test_index_empty_planet(self):
        response = self.client.post('/', data={'planet': ''})
        self.assert200(response)
        self.assertEqual(response.data.decode(), '<h2>Please enter a planet name.</h2>')

    # XSS: injected <script> tag must be HTML-escaped, not rendered as executable markup
    def test_xss_script_tag(self):
        planet = "<script>alert(1)</script>"
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        # Payload must appear HTML-encoded (& lt; form), not as a raw executable tag
        self.assertIn(b'&lt;script&gt;', response.data)
        # The raw unescaped injection must not appear outside the page's own script block
        self.assertNotIn(b'<script>alert', response.data)

    # XSS bypass: img onerror event handler must be HTML-escaped, not executed
    def test_xss_img_onerror(self):
        planet = '<img src="x" onerror="alert(1)">'
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        # Must not contain a raw unescaped <img tag (an attribute-bearing one)
        self.assertNotIn(b'<img src=', response.data)
        # onerror must appear only in escaped form (&#34; or &quot; quoting)
        self.assertNotIn(b'onerror="alert', response.data)

    # XSS bypass: uppercase SCRIPT tag must be HTML-escaped
    def test_xss_uppercase_script(self):
        planet = '<SCRIPT>alert(1)</SCRIPT>'
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        self.assertNotIn(b'<SCRIPT>', response.data)

    # XSS bypass: javascript: URI scheme must not appear as a raw href attribute
    def test_xss_javascript_uri(self):
        planet = '<a href="javascript:alert(1)">click</a>'
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        self.assertNotIn(b'<a href=', response.data)

    # XSS bypass: pre-encoded HTML entities in input must not become executable markup
    def test_xss_html_entities(self):
        planet = '&lt;img src="x" onerror="alert(1)"&gt;'
        response = self.client.post('/', data={'planet': planet})
        self.assert200(response)
        # The input entities must themselves be re-escaped, not decoded to a raw <img tag
        self.assertNotIn(b'<img', response.data)

if __name__ == '__main__':
    unittest.main()
