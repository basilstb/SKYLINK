from django.test import TestCase

class DomainRedirectMiddlewareTest(TestCase):
    def test_redirect_from_old_domain(self):
        # Request with HTTP_HOST set to the old domain
        response = self.client.get('/', HTTP_HOST='delivery-site-project-1.onrender.com')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://express-logistics-1.onrender.com/')

    def test_no_redirect_from_new_domain(self):
        # Request with HTTP_HOST set to the new domain
        response = self.client.get('/', HTTP_HOST='express-logistics-1.onrender.com')
        # Since '/' is the index page, it should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_no_redirect_from_localhost(self):
        # Request with HTTP_HOST set to localhost
        response = self.client.get('/', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)

