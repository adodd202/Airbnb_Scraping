# Airbnb_Scraping
Scraping Airbnb with Scrapy Splash and performing EDA in Python and R.

Presentation can be found here:
https://docs.google.com/presentation/d/1dShCpHl9UuVHzVdXqi681p0b0J8rCQKT6qhkjXF5H_8/edit?usp=sharing

------------------

File structure:
1. airbnb folder: scraper using scrapy splash
2. Python_EDA.ipynb:_ explatory data analysis in Python (and some machine learning), wrap it up for R use
3. R_EDA.R:_ explatory data analysis in R

------------------

Project Overview:

This project scrapes Manhattan Airbnb locations via Scrapy Splash. It scrapes at a rate of ~500 listings per hour.
The main scraping speed bottleneck is due to Airbnb banning scraping exceeding scraping faster than one page per 6 seconds.

The exploratory data analysis (EDA) begins in Python with some data cleaning and visulization of data correlation and histograms. 

I attempted to fit a random forest to my data to predict Airbnb listing prices in Python and then tried again in R. Though at times I saw a mean squared error (MSE) on my model of 2500, the error was usually closer to 10,000. I did not understand what changed between the two models, though it may have been related to removing outlier values (high rent homes). I was particularly interested in seeing the effect of longitude and latitude (i.e.: location) on the price so I experimented extensively with modeling this and graphing it on a map in R. I used KNN to show trends better but still did not see any correlations. I believe this would be something to explore further with a larger data set (values and parameters with better feature engineering) and/or better methods.

In the actual code, I go from Python in EDA to R in EDA (and location modeling as previously mentioned). Finally, I end with some more R EDA showing the effect of variables such as room number on price.

Thanks for reading.

Andrew
