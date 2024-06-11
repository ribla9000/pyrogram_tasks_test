1. The first of all create the ```.env``` file.
2. Fill the ```.env``` using ```env_example``` file
3. run command ```docker compose -f docker-compose.yaml up```
4. Test the application


The bot is designed to create/manage/view tasks created by the user. Solutions and technologies were taken from the Test task. Alchemy was used as ORM. I don’t agree with the decision to choose Pirogram as a library for working with telegram bots, it is inconvenient, and it does not have a nested FSM. I would suggest using the "aiogram" or "python-telegram-bot" libraries. I chose Postregs due to the fact that this solution does not need “non-persistent” ones and also has a need for relations. In addition, in the ```db.py``` file I redefined the methods of the Database Class in case the ORM changes. The pyrogram_patch library was also used to add FSM and not waste time on its implementation.
