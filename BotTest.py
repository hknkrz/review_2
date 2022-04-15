import unittest

from SendMessage import topic, describe_doc, new_docs, new_topics, get_tags, words


class TestMessageHandler(unittest.TestCase):

    def setUp(self):
        self.test_args = {'broken_doc': '23', 'broken_new': 'two',
                          'broken_topics': 'dqwdqwd',
                          'broken_topic': 'Егор_Просвирнин_съел_всех_коммунистов',
                          'broken_tags': 'broken_link/aaa', 'broken_words': '/words broken_link/ooo',

                          'correct_doc': 'https://www.interfax.ru/business/683861',
                          'correct_new': '5',
                          'correct_topics': '3',
                          'correct_topic': 'Brexit',
                          'correct_tags': 'https://www.interfax.ru/business/683861',
                          'correct_words': 'https://www.interfax.ru/business/683861'}

        self.test_topic = topic
        self.test_describe_doc = describe_doc
        self.test_new_docs = new_docs
        self.test_new_topics = new_topics
        self.test_get_tags = get_tags
        self.test_words = words

    @unittest.expectedFailure
    def test_broken_args(self):
        self.assertRaises(self.test_topic(self.test_args['broken_topic']))
        self.assertRaises(self.test_describe_doc(self.test_args['broken_doc']))
        self.assertRaises(self.test_new_docs(self.test_args['broken_new']))
        self.assertRaises(self.test_new_topics(self.test_args['broken_topics']))
        self.assertRaises(self.test_get_tags(self.test_args['broken_tags']))
        self.assertRaises(self.test_words(self.test_args['broken_words']))

    def test_no_wallet(self):
        self.assertTrue(self.test_topic(self.test_args['correct_topic']))
        self.assertTrue(self.test_describe_doc(self.test_args['correct_doc']))
        self.assertTrue(self.test_new_docs(self.test_args['correct_new']))
        self.assertTrue(self.test_new_topics(self.test_args['correct_topics']))
        self.assertTrue(self.test_get_tags(self.test_args['correct_tags']))
        self.assertTrue(self.test_words(self.test_args['correct_words']))


if __name__ == "__main__":
    unittest.main()
