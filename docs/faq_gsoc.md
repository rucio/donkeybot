[Move back to documentation homepage](https://github.com/rucio/donkeybot/tree/master/docs)

## Contents
- [Contents](#contents)
- [Outline](#outline)
- [Who wrote Donkeybot during GSoC '20?](#who-wrote-donkeybot-during-gsoc-20)
- [What is GSoC?](#what-is-gsoc)
- [Is there an official GSoC FAQ besides this... thing?](#is-there-an-official-gsoc-faq-besides-this-thing)
- [Where can I see a detailed timeline of the project?](#where-can-i-see-a-detailed-timeline-of-the-project)
- [What problems did you face?](#what-problems-did-you-face)
- [Do you suggest any future improvements?](#do-you-suggest-any-future-improvements)
- [Can you provide a Reading List with material that helped you during GSoC?](#can-you-provide-a-reading-list-with-material-that-helped-you-during-gsoc)

## Outline

This page is written from the Google Summer of Code (GSoC) student's perspective and tries to answer some FAQs related to GSoC.    
While also providing ideas for improvement and problems faced in this project.

## Who wrote Donkeybot during GSoC '20?

Hey there👋  
My name is Vasilis, from Greece and I'm a student developer !    
You probably guessed half of that if you know about GSoC and the other half by looking at my name.   

The important thing you need to know is that I loved this experience and working with everyone in the Rucio team, so if you're thinking about applying to [Google Summer of Code](https://summerofcode.withgoogle.com/) or [contributing to Rucio](https://rucio.readthedocs.io/en/latest/contributing.html), give it a shot !

If you have any questions regarding Donkeybot, GSoC or anything else just [contact me](https://github.com/mageirakos).     
I'm always happy to respond 😁

## What is GSoC?

In one sentence?  

The best way for student developers to get into Open Source contributing.

In more detail?   

I won't be able to explain it any better than Google, so make sure to check the official website of [Google Summer of Code](https://summerofcode.withgoogle.com/).

  
## Is there an official GSoC FAQ besides this... thing?

Of course! Don't just read my thoughts, visit the official Google Summer of Code [FAQ page](https://developers.google.com/open-source/gsoc/faq) and read more. 

Maybe I should just feed Donkeybot the GSoC documentation and see how that performs!    
Or you can [contribute](https://github.com/rucio/donkeybot/blob/master/docs/getting_started.md#contributing) and do it yourself 😁

## Where can I see a detailed timeline of the project?

Like every student I kept a daily/weekly [Progress Report](https://docs.google.com/document/d/1ZwDS5vze91rO0WSC9IQEmBAzL9gpJytaLW-eqj1kTpQ/edit?usp=sharing) to track everything I did throughout the project. It is not detailed to the point of mentioning specific methods/functions/lines of code implemented per day. But, you get a good idea at how and most importantly when I worked on everything. 

I went back while writing this document and added some 'notes from the future' for some things mentioned that you won't find in the source code.  

## What problems did you face?

The main problem we faced as a team was trying to fetch Rucio support emails in a clean format.  
While, seeming simple at the start this proved to be more difficult and somewhat hindered our progress.   

More specifically, we found 2 consistent types of problems in our raw email data : 
- The emlx object tree structure doesn't work correctly and has different types of objects returned without any defining pattern.
- Decoding of the emails doesn't work correctly. This can be due to a number of reasons, including the variety of email clients  Rucio users use and locations they reside in. (The latter affects the language setting in email clients making it hard for regex patterns to be used for cleaning)

While we gave a lot of time in fixing these problems the more we focused on one the other seemed to perform worse.

The **outcome** was to simply used a smaller subset of the emails provided and introduce additional data sources to Donkeybot.  
This proved to be a very good approach even though by the time we followed it and a good data analysis of the emails was completed almost half of GSoC was over.

You can even spot that in the [Progress Report](https://docs.google.com/document/d/1ZwDS5vze91rO0WSC9IQEmBAzL9gpJytaLW-eqj1kTpQ/edit?usp=sharing).

## Do you suggest any future improvements?

There are many things that can be done to Donkeybot.   
I'm only going to list a couple: 
- [Creation of UI](https://github.com/rucio/donkeybot/issues/30) is very important and it will allow us to deploy Donkeybot on a test server to a subset of Rucio Users. Their questions and the answers given can then be supervised and examined creating a dataset for fine-tuning the models used.
- Creation of a custom [NER tagger](https://en.wikipedia.org/wiki/Named-entity_recognition) which will detect Rucio specific laguage like DIDs, RSEs, Operations etc. This has the potential to boost the performance significantly and even provide a way to create dynamic answers.   
eg. A user asks about his quota on a given dataset and Donkeybot runs the cli Rucio commands necessary to provide an answer.

If you have any suggestion make sure to provide them on our [issues page](https://github.com/rucio/donkeybot/issues).

See the official [Rucio documentation](https://rucio.readthedocs.io/en/latest/) if you didn't understand any of the above.    
Or just ask Donkeybot ! 🧐

## Can you provide a Reading List with material that helped you during GSoC?

Yes, but at this moment it's all over the place. I just used it as a link 'dump' doc to store things I wanted to read/watch again.

A lot of things might be missing and I'll make sure to clean it up the first chance I get after GSoC is over.

Still if you want to see it [here it is](https://docs.google.com/document/d/17P6ycLp6tjTYA93mDXXatf5p-8d-_cKNvJDeLU7aZsk/edit?usp=sharing).  
Have fun!


[Move back to documentation homepage](https://github.com/rucio/donkeybot/tree/master/docs)
