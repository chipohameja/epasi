from unittest.mock import patch

from frappe.tests import IntegrationTestCase

from epasi.epasi.doctype.sales_agent.sales_agent import SalesAgent, make_referral_link
from epasi.tests.utils import make_sales_agent


class TestSalesAgent(IntegrationTestCase):
	def test_referral_code_is_made_from_first_name(self):
		first = make_sales_agent("Mwila Banda")
		second = make_sales_agent("mwila Phiri")
		self.assertEqual((first.referral_code, second.referral_code), ("MWILA", "MWILA2"))
		self.assertTrue(first.referral_link.endswith("/epasi/apply?ref=MWILA"))

	def test_edited_code_is_cleaned(self):
		agent = make_sales_agent(referral_code="best-deals 1")
		self.assertEqual(agent.referral_code, "BESTDEALS1")

	def test_find_by_code_ignores_case_and_inactive_agents(self):
		active = make_sales_agent("Chanda Mwale")
		make_sales_agent("Bupe Zulu", is_active=0)
		self.assertEqual(SalesAgent.find_by_code("chanda"), active.name)
		self.assertIsNone(SalesAgent.find_by_code("BUPE"))
		self.assertFalse(SalesAgent.find_by_code(None))

	def test_referral_link_drops_default_port(self):
		for url in ("https://epasi.example:80", "http://epasi.example:443"):
			with patch("epasi.epasi.doctype.sales_agent.sales_agent.get_url", return_value=url + "/x"):
				self.assertEqual(make_referral_link("MWILA"), url.rsplit(":", 1)[0] + "/x")

	def test_referral_link_keeps_custom_port(self):
		with patch(
			"epasi.epasi.doctype.sales_agent.sales_agent.get_url", return_value="http://epasi.site:8000/x"
		):
			self.assertEqual(make_referral_link("MWILA"), "http://epasi.site:8000/x")
