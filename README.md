# Migration-Media

This project takes newspaper articles and runs google nlp analysis on them. It documents sentiment score/magnitude per article and also stores the entities. These entities are then uses to build a network graph. All code in python

The processing.py file contains code heavily based on code from google cloud website that generates sentiment/entities and then writes them to object files using pickle (for entities) or csv (for sentiment)

the EntTest.py file contains mainly functions for producing visuals with some functions for filtering entities.
