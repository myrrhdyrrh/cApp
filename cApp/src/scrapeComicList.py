import urllib,urllib2,re, cEntities
from BeautifulSoup import BeautifulSoup, SoupStrainer
from google.appengine.ext import db

def getSeries(series, fun=None):
    url = "http://www.midtowncomics.com/store/weeklyreleasebuy.asp"
    #open the file that contains the comics we're currently reading
    series.extend([a +" Annual" for a in series])


    #open dat comiclist
    page= urllib2.urlopen(url)

    #dis our output
    weekSeries = []

    #iterate through current reads, see what's coming out this week that we care
    #about
    soup = BeautifulSoup(page)
    for link in soup.findAll("a"):
        text = link.getText()
        #ignore Variants and subsequent printings
        if "Variant" in text or " ptg" in text or " DF " in text:
            continue
        for title in series:
            if title.lower() in text.lower():                

                formatText, linkTitle = formatLine(text)
                formatText=formatTitle(formatText)
                linkTitle=formatTitle(linkTitle)
                if linkTitle.strip().lower() == title.lower():
                    series.remove(title)
                    
                    if formatText not in weekSeries:
                        weekSeries.append(formatText)
                        if fun!=None:
                            fun(formatText, title)

    #write dat series list
    return weekSeries

def getSeriesFromEntityList(entities, fun=None):
    """
    look up what series are coming out this week from a list of Series
    """
    series = [e.name for e in entities]
    return getSeries(series, fun)

def formatTitle(title):
    """
    remove Vol # from title
    assumes no Vol is higher than 9
    """
    index = re.search("Vol [0-9]", title)
    if(index==None):
        return title
    title =title.replace(index.group(0), "")
    return title
    
def findNumber(line):
    """
    find da number in a lien
    """
    words = line
    number = [word for word in words if "#" in word]
    if number ==[]:
        return -1
    return words.index(number[0])

def formatLine(line):
    """
    remove that extra shit after the number
    """
    words = line.split(" ")
    index = findNumber(words)
    if index == -1:
        return "","" #we don't want no hardcover shit or tpb shit
    output=""
    series=""
    for i in range(index+1):
        if(i<index):
            series+=words[i]+" "
        output+= words[i] +" "
    series.strip()
    output.strip()
    output+="\n"
      
    return output,series
