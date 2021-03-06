from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
import bs4
import requests


class CovidStatSkill(MycroftSkill):

        def __init__(self):
                super(CovidStatSkill, self).__init__(name='CovidStatSkill')

                self.res_url = 'https://covid19info.live'
                self.res = requests.get(res_url)

                try:
                    self.res.raise_for_status()
                except Exception as exc:
                    print('There was a problem: %s' % (exc))

                self.covid_content = bs4.BeautifulSoup(self.res.text)

                self.elems = self.covid_content.select('span.val')

                self.global_confirmed = self.elems[5].getText()

                print(str(self.global_confirmed))


        @intent_handler(IntentBuilder('').require('Covid').require('Global'))
        def handle_covid_global_intent(self, message):
            self.speak_dialog('global.confirmed')


            





def create_skill():
    return CovidStatSkill()