# GETNFT Bot V3

This repo is a collection of different tools which can be used to give more insights into the usage of the GET Protocol NFTs. The combination of the different components in this repo can facilitate The GET Protocol Events telegram channel.

V1 and V2 gathered the information from the blockchain (via etherscan and Infura), this version (V3) uses the Graph for all information. This results that no database is neccesary anymore to collect all data.

## Prerequisites
The following prerequisites are necessary:
-	A Telegram bot API key ( Get 1 from @botfather at Telegram, it’s free)
-	A Telegram channel where the bot can post

## Configuration:
-	Copy sample.env to prod.env
-	Add the Telegram API keys
-	Add the Telegram channel ID (You can get it via The username to id bot if you don't know it -> @username_to_id_bot)
-	Run the Docker-compose file to start the containers

You can also run the code outside containers, make sure the modules folder is added to your PYTHONPATH in that case.

## Code navigation:
All functionalities are divided over multiple containers which have an own function. The following list will provide a brief function of each container:
-	**DailyReport** contains a program which runs each day at 9:00 and provides a summery of the sold/scanned tickets of the last day.
-	**UpcomingEventsReport** contains a program which runs each day at 16:00 and generates a report with upcoming events in the upcoming 30 days including the amount of tickets being sold for these events.
-	**NewEventReporter** contains a program which sends a message to Telegram when a new event is published or updated.
